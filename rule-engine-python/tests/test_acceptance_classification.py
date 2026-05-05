"""Acceptance tests for Story 2.2 Transaction Classification Logic.

These tests validate the main story acceptance criteria end-to-end through
the REST API exposed for Java backend integration.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def _classify(transaction: dict) -> dict:
    response = client.post(
        "/classify-transaction",
        json={
            "transaction": transaction,
        },
    )

    assert response.status_code == 200

    return response.json()


@pytest.mark.parametrize(
    "transaction, expected_priority, expected_category_code, expected_fee_rate_percent",
    [
        (
            {
                "transactionId": "acc-priority-1",
                "amount": "100.00",
                "currency": "EUR",
                "region": "EU",
                "channel": "eCommerce",
                "cardType": "Credit",
                "eci": "05",
                "mcc": "5812",
                "authDate": "2026-05-05T10:00:00Z",
                "clearingDate": "2026-05-06T10:00:00Z",
            },
            1,
            "ECOM_SECURE_PREFERRED_CREDIT",
            1.25,
        ),
        (
            {
                "transactionId": "acc-priority-2",
                "amount": "100.00",
                "currency": "EUR",
                "region": "EU",
                "channel": "eCommerce",
                "cardType": "Credit",
                "eci": "05",
                "mcc": "5812",
                "authDate": "2026-05-05T10:00:00Z",
                "clearingDate": "2026-05-06T10:00:01Z",
            },
            2,
            "ECOM_SECURE_NON_PREFERRED_CREDIT",
            1.50,
        ),
        (
            {
                "transactionId": "acc-priority-3",
                "amount": "100.00",
                "currency": "EUR",
                "region": "EU",
                "channel": "eCommerce",
                "cardType": "Credit",
                "eci": "07",
                "mcc": "5812",
                "authDate": "2026-05-05T10:00:00Z",
                "clearingDate": "2026-05-06T10:00:00Z",
            },
            3,
            "ECOM_NON_SECURE_CREDIT",
            1.85,
        ),
        (
            {
                "transactionId": "acc-priority-4",
                "amount": "100.00",
                "currency": "EUR",
                "region": "EU",
                "channel": "eCommerce",
                "cardType": "Debit",
                "eci": "06",
                "mcc": "5812",
                "authDate": "2026-05-05T10:00:00Z",
                "clearingDate": "2026-05-07T10:00:00Z",
            },
            4,
            "ECOM_SECURE_DEBIT",
            0.20,
        ),
        (
            {
                "transactionId": "acc-priority-5",
                "amount": "100.00",
                "currency": "EUR",
                "region": "EU",
                "channel": "eCommerce",
                "cardType": "Debit",
                "eci": "07",
                "mcc": "5812",
                "authDate": "2026-05-05T10:00:00Z",
                "clearingDate": "2026-05-07T10:00:00Z",
            },
            5,
            "ECOM_NON_SECURE_DEBIT",
            0.30,
        ),
        (
            {
                "transactionId": "acc-priority-6",
                "amount": "100.00",
                "currency": "EUR",
                "region": "EU",
                "channel": "POS",
                "cardType": "Debit",
                "mcc": "5812",
                "authDate": "2026-05-05T10:00:00Z",
                "clearingDate": "2026-05-06T10:00:00Z",
            },
            6,
            "POS_DEBIT_REGULATED",
            0.20,
        ),
        (
            {
                "transactionId": "acc-priority-7",
                "amount": "100.00",
                "currency": "EUR",
                "region": "EU",
                "channel": "POS",
                "cardType": "Credit",
                "mcc": "5812",
                "authDate": "2026-05-05T10:00:00Z",
                "clearingDate": "2026-05-06T10:00:00Z",
            },
            7,
            "POS_CREDIT",
            0.90,
        ),
        (
            {
                "transactionId": "acc-priority-8",
                "amount": "100.00",
                "currency": "EUR",
                "region": "EU",
                "channel": "MOTO",
                "cardType": "Credit",
                "mcc": "5812",
            },
            8,
            "MOTO_CREDIT",
            1.90,
        ),
        (
            {
                "transactionId": "acc-priority-9",
                "amount": "100.00",
                "currency": "EUR",
                "region": "EU",
                "channel": "MOTO",
                "cardType": "Debit",
                "mcc": "5812",
            },
            9,
            "MOTO_DEBIT",
            0.35,
        ),
        (
            {
                "transactionId": "acc-priority-10",
                "amount": "100.00",
                "currency": "EUR",
                "region": "Cross-Border",
                "channel": "POS",
                "cardType": "Credit",
                "mcc": "5812",
                "authDate": "2026-05-05T10:00:00Z",
                "clearingDate": "2026-05-07T10:00:00Z",
            },
            10,
            "CROSS_BORDER_CREDIT",
            2.50,
        ),
        (
            {
                "transactionId": "acc-priority-11",
                "amount": "100.00",
                "currency": "EUR",
                "region": "Cross-Border",
                "channel": "POS",
                "cardType": "Debit",
                "mcc": "5812",
                "authDate": "2026-05-05T10:00:00Z",
                "clearingDate": "2026-05-07T10:00:00Z",
            },
            11,
            "CROSS_BORDER_DEBIT",
            1.00,
        ),
        (
            {
                "transactionId": "acc-priority-12",
                "amount": "100.00",
                "currency": "EUR",
                "region": "EU",
                "channel": "eCommerce",
                "cardType": "Commercial",
                "eci": "05",
                "mcc": "5812",
                "authDate": "2026-05-05T10:00:00Z",
                "clearingDate": "2026-05-06T10:00:00Z",
            },
            12,
            "COMMERCIAL_CARD",
            2.20,
        ),
        (
            {
                "transactionId": "acc-priority-13",
                "amount": "100.00",
                "currency": "EUR",
                "region": "EU",
                "channel": "POS",
                "cardType": "Prepaid",
                "mcc": "5411",
                "authDate": "2026-05-05T10:00:00Z",
                "clearingDate": "2026-05-06T10:00:00Z",
            },
            13,
            "MCC_PREFERRED_GROCERY",
            0.15,
        ),
        (
            {
                "transactionId": "acc-priority-14",
                "amount": "100.00",
                "currency": "EUR",
            },
            14,
            "DEFAULT_STANDARD_CATEGORY",
            1.75,
        ),
    ],
)
def test_acceptance_priority_based_classification_1_to_14(
    transaction,
    expected_priority,
    expected_category_code,
    expected_fee_rate_percent,
):
    payload = _classify(transaction)

    result = payload["result"]
    fact = payload["factTransaction"]

    assert result["rulePriority"] == expected_priority
    assert result["categoryCode"] == expected_category_code
    assert result["feeRatePercent"] == expected_fee_rate_percent

    assert fact["transactionId"] == transaction["transactionId"]
    assert fact["categoryCode"] == expected_category_code
    assert fact["rulePriority"] == expected_priority


@pytest.mark.parametrize(
    "channel, expected_category_code, expected_channel_key",
    [
        ("POS", "POS_CREDIT", 1),
        ("eCommerce", "ECOM_SECURE_PREFERRED_CREDIT", 2),
        ("MOTO", "MOTO_CREDIT", 3),
    ],
)
def test_acceptance_handles_all_transaction_channels(
    channel,
    expected_category_code,
    expected_channel_key,
):
    transaction = {
        "transactionId": f"acc-channel-{channel}",
        "amount": "100.00",
        "currency": "EUR",
        "region": "EU",
        "channel": channel,
        "cardType": "Credit",
        "eci": "05",
        "mcc": "5812",
        "authDate": "2026-05-05T10:00:00Z",
        "clearingDate": "2026-05-06T10:00:00Z",
    }

    payload = _classify(transaction)

    assert payload["result"]["categoryCode"] == expected_category_code
    assert payload["factTransaction"]["dimChannelKey"] == expected_channel_key


@pytest.mark.parametrize(
    "eci, three_ds, expected_category_code",
    [
        ("05", False, "ECOM_SECURE_PREFERRED_CREDIT"),
        ("06", False, "ECOM_SECURE_PREFERRED_CREDIT"),
        ("07", True, "ECOM_NON_SECURE_CREDIT"),
        (None, True, "ECOM_SECURE_PREFERRED_CREDIT"),
        (None, False, "ECOM_NON_SECURE_CREDIT"),
    ],
)
def test_acceptance_evaluates_3ds_and_eci_correctly(
    eci,
    three_ds,
    expected_category_code,
):
    transaction = {
        "transactionId": f"acc-auth-{eci}-{three_ds}",
        "amount": "100.00",
        "currency": "EUR",
        "region": "EU",
        "channel": "eCommerce",
        "cardType": "Credit",
        "threeDS": three_ds,
        "mcc": "5812",
        "authDate": "2026-05-05T10:00:00Z",
        "clearingDate": "2026-05-06T10:00:00Z",
    }

    if eci is not None:
        transaction["eci"] = eci

    payload = _classify(transaction)

    assert payload["result"]["categoryCode"] == expected_category_code


def test_acceptance_clearing_time_boundary_exactly_24h_is_preferred():
    payload = _classify(
        {
            "transactionId": "acc-clearing-24h",
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
    )

    assert payload["result"]["categoryCode"] == "ECOM_SECURE_PREFERRED_CREDIT"
    assert payload["result"]["rulePriority"] == 1


def test_acceptance_clearing_time_over_24h_is_non_preferred():
    payload = _classify(
        {
            "transactionId": "acc-clearing-over-24h",
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
    )

    assert payload["result"]["categoryCode"] == "ECOM_SECURE_NON_PREFERRED_CREDIT"
    assert payload["result"]["rulePriority"] == 2


def test_acceptance_considers_card_type_region_and_clearing_time_together():
    payload = _classify(
        {
            "transactionId": "acc-combined-criteria",
            "amount": "100.00",
            "currency": "EUR",
            "region": "Cross-Border",
            "channel": "eCommerce",
            "cardType": "Debit",
            "eci": "05",
            "mcc": "5812",
            "authDate": "2026-05-05T10:00:00Z",
            "clearingDate": "2026-05-07T10:00:00Z",
        }
    )

    result = payload["result"]
    fact = payload["factTransaction"]

    assert result["categoryCode"] == "CROSS_BORDER_DEBIT"
    assert result["rulePriority"] == 11
    assert fact["dimRegionKey"] == 2


def test_acceptance_returns_classification_and_confidence_score():
    payload = _classify(
        {
            "transactionId": "acc-confidence",
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
    )

    result = payload["result"]

    assert result["category"] == "Ecom Secure Preferred Credit"
    assert result["categoryCode"] == "ECOM_SECURE_PREFERRED_CREDIT"
    assert result["confidence"] == 1.0
    assert result["matchedConditions"]


def test_acceptance_handles_missing_data_with_default_category():
    payload = _classify(
        {
            "transactionId": "acc-missing-data",
            "amount": "100.00",
            "currency": "EUR",
        }
    )

    result = payload["result"]
    fact = payload["factTransaction"]

    assert result["categoryCode"] == "DEFAULT_STANDARD_CATEGORY"
    assert result["rulePriority"] == 14
    assert result["confidence"] == 0.5

    assert fact["dimChannelKey"] == 0
    assert fact["dimRegionKey"] == 0


def test_acceptance_invalid_request_returns_422():
    response = client.post(
        "/classify-transaction",
        json={
            "invalid": "payload"
        },
    )

    assert response.status_code == 422