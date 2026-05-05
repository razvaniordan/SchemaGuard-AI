from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_classify_transaction_priority_1_secure_ecommerce_credit():
    response = client.post(
        "/classify-transaction",
        json={
            "transaction": {
                "transactionId": "txn-priority-1",
                "merchantId": "merchant-1",
                "cardId": "card-1",
                "amount": "100.00",
                "currency": "EUR",
                "region": "EU",
                "channel": "eCommerce",
                "cardType": "Credit",
                "eci": "05",
                "mcc": "5812",
                "authDate": "2026-05-05T10:00:00Z",
                "clearingDate": "2026-05-06T10:00:00Z",
            }
        },
    )

    assert response.status_code == 200

    payload = response.json()
    result = payload["result"]
    fact = payload["factTransaction"]

    assert result["category"] == "Ecom Secure Preferred Credit"
    assert result["categoryCode"] == "ECOM_SECURE_PREFERRED_CREDIT"
    assert result["rulePriority"] == 1
    assert result["feeRatePercent"] == 1.25
    assert float(result["confidence"]) == 1.0

    assert "channel" in result["matchedConditions"]
    assert "authStatus" in result["matchedConditions"]
    assert "clearingTime" in result["matchedConditions"]
    assert "cardType" in result["matchedConditions"]
    assert "region" in result["matchedConditions"]

    assert fact["transactionId"] == "txn-priority-1"
    assert fact["categoryCode"] == "ECOM_SECURE_PREFERRED_CREDIT"
    assert fact["rulePriority"] == 1
    assert fact["dimChannelKey"] == 2
    assert fact["dimRegionKey"] == 1
    assert fact["dimDateKey"] == 20260505


def test_classify_transaction_priority_2_secure_ecommerce_credit_over_24h():
    response = client.post(
        "/classify-transaction",
        json={
            "transaction": {
                "transactionId": "txn-priority-2",
                "amount": "100.00",
                "currency": "EUR",
                "region": "EU",
                "channel": "eCommerce",
                "cardType": "Credit",
                "eci": "05",
                "mcc": "5812",
                "authDate": "2026-05-05T10:00:00Z",
                "clearingDate": "2026-05-06T10:00:01Z",
            }
        },
    )

    assert response.status_code == 200

    result = response.json()["result"]

    assert result["categoryCode"] == "ECOM_SECURE_NON_PREFERRED_CREDIT"
    assert result["rulePriority"] == 2
    assert result["feeRatePercent"] == 1.5


def test_classify_transaction_priority_3_non_secure_ecommerce_credit():
    response = client.post(
        "/classify-transaction",
        json={
            "transaction": {
                "transactionId": "txn-priority-3",
                "amount": "100.00",
                "currency": "EUR",
                "region": "EU",
                "channel": "eCommerce",
                "cardType": "Credit",
                "eci": "07",
                "mcc": "5812",
                "authDate": "2026-05-05T10:00:00Z",
                "clearingDate": "2026-05-06T10:00:00Z",
            }
        },
    )

    assert response.status_code == 200

    result = response.json()["result"]

    assert result["categoryCode"] == "ECOM_NON_SECURE_CREDIT"
    assert result["rulePriority"] == 3
    assert result["feeRatePercent"] == 1.85


def test_classify_transaction_moto_credit():
    response = client.post(
        "/classify-transaction",
        json={
            "transaction": {
                "transactionId": "txn-moto-credit",
                "amount": "100.00",
                "currency": "EUR",
                "channel": "MOTO",
                "cardType": "Credit",
                "mcc": "5812",
            }
        },
    )

    assert response.status_code == 200

    result = response.json()["result"]
    fact = response.json()["factTransaction"]

    assert result["categoryCode"] == "MOTO_CREDIT"
    assert result["rulePriority"] == 8
    assert fact["dimChannelKey"] == 3


def test_classify_transaction_missing_data_falls_back_to_default():
    response = client.post(
        "/classify-transaction",
        json={
            "transaction": {
                "transactionId": "txn-missing-data",
                "amount": "100.00",
                "currency": "EUR"
            }
        },
    )

    assert response.status_code == 200

    result = response.json()["result"]
    fact = response.json()["factTransaction"]

    assert result["categoryCode"] == "DEFAULT_STANDARD_CATEGORY"
    assert result["rulePriority"] == 14
    assert float(result["confidence"]) == 0.5

    assert fact["transactionId"] == "txn-missing-data"
    assert fact["categoryCode"] == "DEFAULT_STANDARD_CATEGORY"
    assert fact["dimChannelKey"] == 0
    assert fact["dimRegionKey"] == 0


def test_classify_transaction_invalid_body_returns_422():
    response = client.post(
        "/classify-transaction",
        json={
            "invalid": "payload"
        },
    )

    assert response.status_code == 422