from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_health_endpoint_returns_up():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "UP"
    assert response.json()["service"] == "SchemeGuard Rule Engine"


def test_metadata_endpoint_returns_supported_dimensions():
    response = client.get("/metadata")

    assert response.status_code == 200

    payload = response.json()

    assert payload["phase"] == "EU Phase 1"
    assert payload["supportedPriorities"] == {
        "min": 1,
        "max": 14,
    }
    assert "POS" in payload["supportedChannels"]
    assert "eCommerce" in payload["supportedChannels"]
    assert "MOTO" in payload["supportedChannels"]
    assert "Credit" in payload["supportedCardTypes"]
    assert "Debit" in payload["supportedCardTypes"]


def test_categories_endpoint_returns_14_categories():
    response = client.get("/categories")

    assert response.status_code == 200

    categories = response.json()

    assert len(categories) == 14
    assert categories[0]["priority"] == 1
    assert categories[0]["category"] == "Ecom Secure Preferred Credit"
    assert float(categories[0]["feeRatePercent"]) == 1.25
    assert categories[-1]["priority"] == 14
    assert categories[-1]["category"] == "Default Standard Category"


def test_classify_transaction_endpoint_returns_classification_result():
    response = client.post(
        "/classify-transaction",
        json={
            "transaction": {
                "transactionId": "txn-1",
                "merchantId": "merchant-1",
                "cardId": "card-1",
                "amount": "100.00",
                "currency": "EUR",
                "region": "EU",
                "channel": "eCommerce",
                "cardType": "Credit",
                "threeDS": True,
                "eci": "05",
                "mcc": "5411",
                "authDate": "2026-05-05T10:00:00Z",
                "clearingDate": "2026-05-06T10:00:00Z",
            }
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["result"]["transactionId"] == "txn-1"
    assert payload["result"]["categoryCode"] == "ECOM_SECURE_PREFERRED_CREDIT"
    assert payload["result"]["rulePriority"] == 1
    assert float(payload["result"]["confidence"]) == 1.0

    assert payload["factTransaction"]["transactionId"] == "txn-1"
    assert payload["factTransaction"]["categoryCode"] == "ECOM_SECURE_PREFERRED_CREDIT"
    assert payload["factTransaction"]["dimChannelKey"] == 2
    assert payload["factTransaction"]["dimRegionKey"] == 1
    assert payload["factTransaction"]["dimDateKey"] == 20260505

def test_classify_transaction_validates_request_body():
    response = client.post(
        "/classify-transaction",
        json={
            "invalid": "payload"
        },
    )

    assert response.status_code == 422