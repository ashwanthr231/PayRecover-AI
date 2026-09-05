import sqlite3
from pathlib import Path


# Always resolve the database relative to the project root, not the
# directory from which uvicorn/python happens to be started.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "payrecover.db"


def get_connection():
    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=10
    )

    # Improve SQLite concurrency
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA busy_timeout=10000")

    return connection



def create_tables():

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                payment_id TEXT UNIQUE,
                merchant_id TEXT,
                customer_id TEXT,
                amount REAL,
                payment_method TEXT,
                failure_code TEXT,
                attempt_number INTEGER,
                status TEXT,
                failure_class TEXT,
                confidence REAL,
                recovery_probability REAL,
                recommended_action TEXT,
                policy_decision TEXT,
                safety_status TEXT,
                recovery_status TEXT,
                recovered INTEGER,
                amount_recovered REAL
            )
        """)

        connection.commit()

    finally:
        connection.close()


# ---------------------------------------------------------
# CUSTOMER HISTORY
# ---------------------------------------------------------

def get_customer_failure_count(customer_id):

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM payments
            WHERE customer_id = ?
        """, (customer_id,))

        result = cursor.fetchone()

        return result[0] or 0

    finally:
        connection.close()


def get_previous_success(customer_id):

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM payments
            WHERE customer_id = ?
            AND recovered = 1
        """, (customer_id,))

        result = cursor.fetchone()

        if result[0] > 0:
            return 1

        return 0

    finally:
        connection.close()


# ---------------------------------------------------------
# MERCHANT HISTORY
# ---------------------------------------------------------

def get_merchant_failure_rate(merchant_id):

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Number of historical payment attempts
        cursor.execute("""
            SELECT COUNT(*)
            FROM payments
            WHERE merchant_id = ?
        """, (merchant_id,))

        total_payments = cursor.fetchone()[0] or 0

        if total_payments == 0:
            return 0.10

        # Number of historical payments that were not recovered
        cursor.execute("""
            SELECT COUNT(*)
            FROM payments
            WHERE merchant_id = ?
            AND recovered = 0
        """, (merchant_id,))

        failed_payments = cursor.fetchone()[0] or 0

        failure_rate = failed_payments / total_payments

        return round(failure_rate, 4)

    finally:
        connection.close()


# ---------------------------------------------------------
# FEATURE ENGINEERING
# ---------------------------------------------------------

def get_ml_features(payment):

    customer_failure_count = get_customer_failure_count(
        payment.customer_id
    )

    merchant_failure_rate = get_merchant_failure_rate(
        payment.merchant_id
    )

    previous_success = get_previous_success(
        payment.customer_id
    )

    return {
        "customer_failure_count": customer_failure_count,
        "merchant_failure_rate": merchant_failure_rate,
        "previous_success": previous_success
    }


# ---------------------------------------------------------
# SAVE PAYMENT
# ---------------------------------------------------------

def save_payment(payment, diagnosis, policy, safety, recovery):

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO payments (
                payment_id,
                merchant_id,
                customer_id,
                amount,
                payment_method,
                failure_code,
                attempt_number,
                status,
                failure_class,
                confidence,
                recovery_probability,
                recommended_action,
                policy_decision,
                safety_status,
                recovery_status,
                recovered,
                amount_recovered
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            payment.payment_id,
            payment.merchant_id,
            payment.customer_id,
            payment.amount,
            payment.payment_method,
            payment.failure_code,
            payment.attempt_number,
            payment.status,
            diagnosis["failure_class"],
            diagnosis["confidence"],
            diagnosis["recovery_probability"],
            diagnosis["recommended_action"],
            policy["decision"],
            safety["status"],
            recovery["status"],
            int(recovery["recovered"]),
            recovery["amount_recovered"]
        ))

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# ---------------------------------------------------------
# ANALYTICS
# ---------------------------------------------------------

def get_analytics():

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                COUNT(*),
                SUM(amount),
                SUM(recovered),
                SUM(amount_recovered)
            FROM payments
        """)

        result = cursor.fetchone()

    finally:
        connection.close()

    total_payments = result[0] or 0
    total_failed_amount = result[1] or 0
    recovered_payments = result[2] or 0
    total_recovered_amount = result[3] or 0

    if total_payments > 0:
        recovery_rate = (
            recovered_payments / total_payments
        ) * 100
    else:
        recovery_rate = 0

    return {
        "total_payments": total_payments,
        "failed_payments": total_payments,
        "recovered_payments": recovered_payments,
        "recovery_rate": round(recovery_rate, 2),
        "total_failed_amount": total_failed_amount,
        "total_recovered_amount": total_recovered_amount
    }


# ---------------------------------------------------------
# PAYMENT HISTORY
# ---------------------------------------------------------

def get_payment_history():

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                payment_id,
                merchant_id,
                customer_id,
                amount,
                payment_method,
                failure_code,
                attempt_number,
                status,
                failure_class,
                confidence,
                recovery_probability,
                recommended_action,
                policy_decision,
                safety_status,
                recovered,
                amount_recovered
            FROM payments
            ORDER BY id DESC
        """)

        rows = cursor.fetchall()

    finally:
        connection.close()

    payments = []

    for row in rows:

        payments.append({
            "payment_id": row[0],
            "merchant_id": row[1],
            "customer_id": row[2],
            "amount": row[3],
            "payment_method": row[4],
            "failure_code": row[5],
            "attempt_number": row[6],
            "status": row[7],
            "failure_class": row[8],
            "confidence": row[9],
            "recovery_probability": row[10],
            "recommended_action": row[11],
            "policy_decision": row[12],
            "safety_status": row[13],
            "recovered": bool(row[14]),
            "amount_recovered": row[15]
        })

    return payments