import pandas as pd
import random
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score


random.seed(42)

TOTAL_RECORDS = 5000

payment_methods = [
    "UPI",
    "CARD",
    "NETBANKING"
]

failure_codes = [
    "BANK_TIMEOUT",
    "NETWORK_ERROR",
    "GATEWAY_TIMEOUT",
    "INSUFFICIENT_FUNDS",
    "CARD_DECLINED",
    "FRAUD_SUSPECTED",
    "INVALID_CARD",
    "EXPIRED_CARD",
    "INVALID_ACCOUNT",
    "ACCOUNT_BLOCKED"
]

records = []


# =====================================================
# GENERATE RECOVERY TRAINING DATA
# =====================================================

for _ in range(TOTAL_RECORDS):

    payment_method = random.choice(payment_methods)

    failure_code = random.choice(failure_codes)

    amount = random.randint(100, 50000)

    attempt_number = random.randint(1, 4)

    customer_failure_count = random.randint(0, 5)

    merchant_failure_rate = round(
        random.uniform(0.01, 0.50),
        2
    )

    transaction_hour = random.randint(
        0,
        23
    )

    is_international = random.choice([
        0,
        1
    ])

    previous_success = random.choice([
        0,
        1
    ])


    # =================================================
    # BASE RECOVERY PROBABILITY
    # =================================================

    if failure_code in [
        "BANK_TIMEOUT",
        "NETWORK_ERROR",
        "GATEWAY_TIMEOUT"
    ]:
        recovery_probability = 0.80

    elif failure_code in [
        "INSUFFICIENT_FUNDS",
        "CARD_DECLINED"
    ]:
        recovery_probability = 0.30

    elif failure_code == "FRAUD_SUSPECTED":
        recovery_probability = 0.05

    else:
        recovery_probability = 0.10


    # =================================================
    # MAKE PROBABILITY DEPEND ON OTHER FEATURES
    # =================================================

    # Previous successful payment increases recovery chance
    if previous_success == 1:
        recovery_probability += 0.05

    # Multiple previous failures reduce recovery chance
    recovery_probability -= (
        customer_failure_count * 0.03
    )

    # More retry attempts reduce recovery chance
    recovery_probability -= (
        (attempt_number - 1) * 0.05
    )

    # High merchant failure rate reduces probability
    recovery_probability -= (
        merchant_failure_rate * 0.10
    )

    # International transactions are slightly harder
    if is_international == 1:
        recovery_probability -= 0.03

    # Very high-value transactions are slightly harder
    if amount > 20000:
        recovery_probability -= 0.03

    # Keep probability between 0 and 1
    recovery_probability = max(
        0.01,
        min(
            recovery_probability,
            0.99
        )
    )

    # Add small random noise
    recovery_probability += random.uniform(
        -0.05,
        0.05
    )

    recovery_probability = max(
        0.01,
        min(
            recovery_probability,
            0.99
        )
    )


    records.append({

        "payment_method":
            payment_method,

        "failure_code":
            failure_code,

        "amount":
            amount,

        "attempt_number":
            attempt_number,

        "customer_failure_count":
            customer_failure_count,

        "merchant_failure_rate":
            merchant_failure_rate,

        "transaction_hour":
            transaction_hour,

        "is_international":
            is_international,

        "previous_success":
            previous_success,

        "recovery_probability":
            recovery_probability
    })


df = pd.DataFrame(records)


# =====================================================
# DISPLAY DATASET
# =====================================================

print("\n========================================")
print("PAYRECOVER AI")
print("RECOVERY PROBABILITY MODEL")
print("========================================")

print("\nDataset Shape:")
print(df.shape)

print("\nSample Data:")
print(df.head())


# =====================================================
# SAVE DATASET
# =====================================================

dataset_path = os.path.join(
    os.path.dirname(__file__),
    "recovery_training_data.csv"
)

df.to_csv(
    dataset_path,
    index=False
)

print("\nTraining dataset saved:")
print(dataset_path)


# =====================================================
# FEATURES
# =====================================================

X = df[
    [
        "payment_method",
        "failure_code",
        "amount",
        "attempt_number",
        "customer_failure_count",
        "merchant_failure_rate",
        "transaction_hour",
        "is_international",
        "previous_success"
    ]
]


# =====================================================
# TARGET
# =====================================================

y = df[
    "recovery_probability"
]


# =====================================================
# TRAIN / TEST SPLIT
# =====================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)


# =====================================================
# PREPROCESSING
# =====================================================

categorical_features = [
    "payment_method",
    "failure_code"
]

numeric_features = [
    "amount",
    "attempt_number",
    "customer_failure_count",
    "merchant_failure_rate",
    "transaction_hour",
    "is_international",
    "previous_success"
]


preprocessor = ColumnTransformer(
    transformers=[

        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            categorical_features
        ),

        (
            "numeric",
            "passthrough",
            numeric_features
        )

    ]
)


# =====================================================
# RANDOM FOREST REGRESSOR
# =====================================================

model = RandomForestRegressor(
    n_estimators=300,
    random_state=42,
    max_depth=12
)


pipeline = Pipeline(
    steps=[

        (
            "preprocessor",
            preprocessor
        ),

        (
            "regressor",
            model
        )

    ]
)


# =====================================================
# TRAIN MODEL
# =====================================================

print("\nTraining recovery probability model...")

pipeline.fit(
    X_train,
    y_train
)


# =====================================================
# PREDICTIONS
# =====================================================

predictions = pipeline.predict(
    X_test
)


# =====================================================
# MODEL EVALUATION
# =====================================================

mae = mean_absolute_error(
    y_test,
    predictions
)

r2 = r2_score(
    y_test,
    predictions
)


print("\n========================================")
print("MODEL PERFORMANCE")
print("========================================")

print(
    f"\nMean Absolute Error: {mae:.4f}"
)

print(
    f"R2 Score: {r2:.4f}"
)


# =====================================================
# SAVE MODEL
# =====================================================

model_path = os.path.join(
    os.path.dirname(__file__),
    "recovery_model.pkl"
)

joblib.dump(
    pipeline,
    model_path
)


print("\n========================================")
print("MODEL SAVED SUCCESSFULLY")
print("========================================")

print(
    f"\nModel: {model_path}"
)