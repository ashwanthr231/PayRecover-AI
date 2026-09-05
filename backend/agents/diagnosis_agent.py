import os
import joblib
import pandas as pd
from datetime import datetime

from backend.database import get_ml_features


# =====================================================
# LOAD ML MODELS
# =====================================================

BASE_DIR = os.path.dirname(__file__)


# Diagnosis model
DIAGNOSIS_MODEL_PATH = os.path.join(
    BASE_DIR,
    "..",
    "ml",
    "diagnosis_model.pkl"
)


# Recovery probability model
RECOVERY_MODEL_PATH = os.path.join(
    BASE_DIR,
    "..",
    "ml",
    "recovery_model.pkl"
)


diagnosis_model = joblib.load(
    DIAGNOSIS_MODEL_PATH
)

recovery_model = joblib.load(
    RECOVERY_MODEL_PATH
)


# =====================================================
# DIAGNOSE PAYMENT
# =====================================================

def diagnose_payment(payment):

    # =================================================
    # GET FEATURES FROM DATABASE
    # =================================================

    history_features = get_ml_features(payment)


    customer_failure_count = history_features[
        "customer_failure_count"
    ]


    merchant_failure_rate = history_features[
        "merchant_failure_rate"
    ]


    previous_success = history_features[
        "previous_success"
    ]


    # Current transaction information

    transaction_hour = datetime.now().hour


    # Currently using default value.
    # We can connect this to actual payment data later.

    is_international = 0


    # =================================================
    # CREATE ML INPUT
    # =================================================

    payment_data = pd.DataFrame([{

        "payment_method":
            payment.payment_method,

        "failure_code":
            payment.failure_code,

        "amount":
            payment.amount,

        "attempt_number":
            payment.attempt_number,

        "customer_failure_count":
            customer_failure_count,

        "merchant_failure_rate":
            merchant_failure_rate,

        "transaction_hour":
            transaction_hour,

        "is_international":
            is_international,

        "previous_success":
            previous_success

    }])


    # =================================================
    # MODEL 1: FAILURE CLASSIFICATION
    # =================================================

    prediction = diagnosis_model.predict(
        payment_data
    )[0]


    # =================================================
    # DIAGNOSIS CONFIDENCE
    # =================================================

    probabilities = diagnosis_model.predict_proba(
        payment_data
    )[0]

    classes = diagnosis_model.classes_


    predicted_index = list(classes).index(
        prediction
    )


    confidence = float(
        probabilities[predicted_index]
    )


    # =================================================
    # MODEL 2: RECOVERY PROBABILITY
    # =================================================

    recovery_prediction = recovery_model.predict(
        payment_data
    )[0]


    # Keep probability between 0 and 1

    recovery_probability = max(
        0.01,
        min(
            float(recovery_prediction),
            0.99
        )
    )


    # =================================================
    # RECOMMENDED ACTION
    # =================================================

    action_map = {

        "TRANSIENT": "RETRY",

        "CUSTOMER_ACTION": "NOTIFY",

        "RISK": "ESCALATE",

        "PERMANENT": "ESCALATE"

    }


    recommended_action = action_map.get(
        prediction,
        "ESCALATE"
    )


    # =================================================
    # EXPLANATION
    # =================================================

    reason_map = {

        "TRANSIENT":
            "The ML model identified the failure as a temporary bank or network issue.",

        "CUSTOMER_ACTION":
            "The ML model identified the failure as requiring customer action.",

        "RISK":
            "The ML model identified the payment as potentially risky and requiring review.",

        "PERMANENT":
            "The ML model identified the failure as unlikely to be automatically recoverable."

    }


    reason = reason_map.get(
        prediction,
        "The payment requires further evaluation."
    )


   
    # =================================================
    # RETURN DIAGNOSIS
    # =================================================

    return {

        "failure_class":
            prediction,

        "confidence":
            round(
                confidence,
                2
            ),

        "recovery_probability":
            round(
                recovery_probability,
                2
            ),

        "recommended_action":
            recommended_action,

        "reason":
            reason,

        # Features used by the ML models
        "ml_features": {

            "customer_failure_count":
                customer_failure_count,

            "merchant_failure_rate":
                round(
                    merchant_failure_rate,
                    4
                ),

            "previous_success":
                previous_success,

            "transaction_hour":
                transaction_hour,

            "is_international":
                is_international
        }
    }

