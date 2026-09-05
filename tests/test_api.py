from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app
import backend.database as database


def test_payment_analysis_smoke():
    original_path = Path(database.DATABASE_PATH)
    test_path = original_path.with_name("test_payrecover.db")
    if test_path.exists():
        test_path.unlink()

    database.DATABASE_PATH = test_path
    database.create_tables()

    client = TestClient(app)

    payload = {
        "payment_id": "test_001",
        "merchant_id": "merchant_test",
        "customer_id": "customer_test",
        "amount": 2499,
        "payment_method": "UPI",
        "failure_code": "BANK_TIMEOUT",
        "attempt_number": 1,
        "status": "FAILED",
    }

    response = client.post("/payments", json=payload)
    assert response.status_code == 200

    result = response.json()
    assert result["diagnosis"]["failure_class"] == "TRANSIENT"
    assert result["policy"]["decision"] == "ALLOW_RETRY"
    assert result["safety"]["status"] == "APPROVED"
    assert result["recovery"]["recovered"] is True

    duplicate = client.post("/payments", json=payload)
    assert duplicate.status_code == 409

    invalid = client.post(
        "/payments",
        json={**payload, "payment_id": "test_002", "amount": 0},
    )
    assert invalid.status_code == 422

    database.DATABASE_PATH = original_path
    if test_path.exists():
        test_path.unlink()
