
import sqlite3

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.models import Payment

from backend.agents.diagnosis_agent import diagnose_payment
from backend.agents.recovery_agent import choose_recovery_strategy

from backend.engine.policy_engine import evaluate_policy
from backend.engine.safety_gate import safety_check

from backend.simulator.recovery_simulator import simulate_recovery

from backend.database import (
    create_tables,
    save_payment,
    get_analytics,
    get_payment_history
)


# ==========================================
# CREATE FASTAPI APPLICATION
# ==========================================

app = FastAPI(
    title="PayRecover AI",
    description="AI-powered payment failure diagnosis & revenue recovery system",
    version="1.0.0"
)


# ==========================================
# CORS CONFIGURATION
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# CREATE DATABASE TABLES
# ==========================================

create_tables()


# ==========================================
# HOME
# ==========================================

@app.get("/")
def root():

    return {
        "project": "PayRecover AI",
        "status": "running"
    }


# ==========================================
# ANALYTICS
# ==========================================

@app.get("/analytics")
def analytics():

    return get_analytics()


# ==========================================
# PAYMENT HISTORY
# ==========================================

@app.get("/payments")
def payment_history():

    return get_payment_history()


# ==========================================
# CREATE / ANALYZE PAYMENT
# ==========================================

@app.post("/payments")
def create_payment(payment: Payment):

    # --------------------------------------
    # Step 1: Diagnose payment failure
    # --------------------------------------

    diagnosis = diagnose_payment(payment)


    # --------------------------------------
    # Step 2: Evaluate recovery policy
    # --------------------------------------

    policy = evaluate_policy(
        payment,
        diagnosis
    )


    # --------------------------------------
    # Step 3: Safety check
    # --------------------------------------

    safety = safety_check(
        payment,
        diagnosis,
        policy
    )


    # --------------------------------------
    # Step 4: Choose recovery strategy
    # --------------------------------------

    strategy = choose_recovery_strategy(
        payment,
        diagnosis,
        policy,
        safety
    )


    # --------------------------------------
    # Step 5: Simulate recovery
    # --------------------------------------

    recovery = simulate_recovery(
        payment,
        strategy
    )


    # --------------------------------------
    # Step 6: Save complete analysis
    # --------------------------------------

    try:
        save_payment(
            payment,
            diagnosis,
            policy,
            safety,
            recovery
        )
    except sqlite3.IntegrityError as exc:
        if "UNIQUE constraint failed: payments.payment_id" in str(exc):
            raise HTTPException(
                status_code=409,
                detail=f"Payment ID '{payment.payment_id}' already exists. Use a unique Payment ID."
            ) from exc
        raise HTTPException(
            status_code=500,
            detail="The payment analysis was completed, but the result could not be saved."
        ) from exc


    # --------------------------------------
    # Step 7: Return complete result
    # --------------------------------------

    return {
        "message": "Payment analyzed",
        "payment": payment,
        "diagnosis": diagnosis,
        "policy": policy,
        "safety": safety,
        "recovery_strategy": strategy,
        "recovery": recovery
    }
