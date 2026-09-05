import pandas as pd
import random
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report


random.seed(42)

TOTAL_RECORDS = 5000

failure_definitions = {
    "TRANSIENT": [
        "BANK_TIMEOUT",
        "NETWORK_ERROR",
        "GATEWAY_TIMEOUT"
    ],
    "CUSTOMER_ACTION": [
        "INSUFFICIENT_FUNDS",
        "CARD_DECLINED"
    ],
    "RISK": [
        "FRAUD_SUSPECTED"
    ],
    "PERMANENT": [
        "INVALID_CARD",
        "EXPIRED_CARD",
        "INVALID_ACCOUNT",
        "ACCOUNT_BLOCKED"
    ]
}

payment_methods = [
    "UPI",
    "CARD",
    "NETBANKING"
]

records = []

for _ in range(TOTAL_RECORDS):

    failure_class = random.choice(
        list(failure_definitions.keys())
    )

    failure_code = random.choice(
        failure_definitions[failure_class]
    )

    payment_method = random.choice(
        payment_methods
    )

    amount = random.randint(
        100,
        50000
    )

    attempt_number = random.randint(
        1,
        4
    )

    customer_failure_count = random.randint(
        0,
        5
    )

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

    records.append({
        "payment_method": payment_method,
        "failure_code": failure_code,
        "amount": amount,
        "attempt_number": attempt_number,
        "customer_failure_count": customer_failure_count,
        "merchant_failure_rate": merchant_failure_rate,
        "transaction_hour": transaction_hour,
        "is_international": is_international,
        "previous_success": previous_success,
        "failure_class": failure_class
    })


df = pd.DataFrame(records)


print("\n========================================")
print("PAYRECOVER AI - ML TRAINING")
print("========================================")


print("\nDataset Shape:")
print(df.shape)


print("\nClass Distribution:")
print(
    df["failure_class"].value_counts()
)


dataset_path = os.path.join(
    os.path.dirname(__file__),
    "training_data.csv"
)


df.to_csv(
    dataset_path,
    index=False
)


print("\nTraining dataset saved:")
print(dataset_path)


# Features
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


# Target
y = df["failure_class"]


X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


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


model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    class_weight="balanced",
    max_depth=12
)


pipeline = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "classifier",
            model
        )
    ]
)


print("\nTraining Random Forest model...")


pipeline.fit(
    X_train,
    y_train
)


predictions = pipeline.predict(
    X_test
)


accuracy = accuracy_score(
    y_test,
    predictions
)


print("\n========================================")
print("MODEL PERFORMANCE")
print("========================================")


print(
    f"\nAccuracy: {accuracy * 100:.2f}%"
)


print("\nClassification Report:")


print(
    classification_report(
        y_test,
        predictions,
        zero_division=0
    )
)


model_path = os.path.join(
    os.path.dirname(__file__),
    "diagnosis_model.pkl"
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