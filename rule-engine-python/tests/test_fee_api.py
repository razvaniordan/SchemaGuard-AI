from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_calculate_fee_endpoint_returns_fee_result():
    response = client.post(
        "/calculate-fee",
        json={
            "amount": "100.00",
            "feeRate": "0.0125",
            "currency": "EUR",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["amount"] == 100.0
    assert payload["feeRate"] == 0.0125
    assert payload["rawFee"] == 1.25
    assert payload["finalFee"] == 1.25
    assert payload["currency"] == "EUR"
    assert payload["capApplied"] is None


def test_calculate_fee_endpoint_applies_min_cap():
    response = client.post(
        "/calculate-fee",
        json={
            "amount": "100.00",
            "feeRate": "0.01",
            "currency": "EUR",
            "cap": {
                "minFee": "2.00",
                "maxFee": "10.00",
            },
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["rawFee"] == 1.0
    assert payload["finalFee"] == 2.0
    assert payload["capApplied"] == "MIN_FEE"


def test_classify_transaction_response_includes_fee_calculation():
    response = client.post(
        "/classify-transaction",
        json={
            "transaction": {
                "transactionId": "txn-fee-api",
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

    assert payload["result"]["categoryCode"] == "ECOM_SECURE_PREFERRED_CREDIT"
    assert payload["result"]["feeRate"] == 0.0125

    assert payload["feeCalculation"] is not None
    assert payload["feeCalculation"]["amount"] == 100.0
    assert payload["feeCalculation"]["feeRate"] == 0.0125
    assert payload["feeCalculation"]["rawFee"] == 1.25
    assert payload["feeCalculation"]["finalFee"] == 1.25
    assert payload["feeCalculation"]["currency"] == "EUR"


def test_classify_transaction_fee_calculation_is_null_when_amount_missing():
    response = client.post(
        "/classify-transaction",
        json={
            "transaction": {
                "transactionId": "txn-no-amount",
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

    assert payload["result"]["categoryCode"] == "ECOM_SECURE_PREFERRED_CREDIT"
    assert payload["feeCalculation"] is None


def test_calculate_fee_rejects_negative_amount():
    response = client.post(
        "/calculate-fee",
        json={
            "amount": "-100.00",
            "feeRate": "0.0125",
            "currency": "EUR",
        },
    )

    assert response.status_code == 422