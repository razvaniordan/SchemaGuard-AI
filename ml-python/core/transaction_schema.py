from datetime import datetime
from typing import Any, Dict, Optional


CANONICAL_TRANSACTION_FIELDS = [
    "transactionId",
    "amount",
    "currency",
    "merchantCountry",
    "issuerCountry",
    "region",
    "cardType",
    "cardBrand",
    "cardPresence",
    "channel",
    "mcc",
    "threeDS",
    "eci",
    "authDate",
    "clearingDate",
    "clearingDelayDays",
]


REQUIRED_TRANSACTION_FIELDS = [
    "amount",
    "currency",
    "merchantCountry",
    "issuerCountry",
    "region",
    "cardType",
    "channel",
    "mcc",
    "threeDS",
    "authDate",
    "clearingDate",
    "cardBrand",
    "cardPresence",
]


VALID_CHANNELS = {"eCommerce", "POS", "MOTO"}
VALID_CARD_TYPES = {"Credit", "Debit", "Prepaid", "Commercial"}


def get_transaction_id(transaction: Dict[str, Any]) -> str:
    return str(
        transaction.get("transactionId")
        or transaction.get("id")
        or "UNKNOWN"
    )


def get_payment_channel(transaction: Dict[str, Any]) -> Optional[str]:
    return transaction.get("paymentChannel") or transaction.get("channel")


def calculate_clearing_delay_days(transaction: Dict[str, Any]) -> Optional[int]:
    existing_value = transaction.get("clearingDelayDays")

    if existing_value is not None:
        try:
            return int(existing_value)
        except (TypeError, ValueError):
            return None

    auth_date = transaction.get("authDate")
    clearing_date = transaction.get("clearingDate")

    if not auth_date or not clearing_date:
        return None

    try:
        auth_dt = datetime.fromisoformat(str(auth_date))
        clearing_dt = datetime.fromisoformat(str(clearing_date))
        return max((clearing_dt - auth_dt).days, 0)
    except ValueError:
        return None


def normalize_transaction(transaction: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(transaction)

    if "paymentChannel" not in normalized and normalized.get("channel") is not None:
        normalized["paymentChannel"] = normalized.get("channel")

    if "clearingDelayDays" not in normalized or normalized.get("clearingDelayDays") is None:
        normalized["clearingDelayDays"] = calculate_clearing_delay_days(normalized)

    return normalized


def build_ml_feature_row(
    transaction: Dict[str, Any],
    category: str,
    fee_rate: float,
    fee_amount: float,
) -> Dict[str, Any]:
    transaction = normalize_transaction(transaction)

    return {
        "transactionId": get_transaction_id(transaction),
        "amount": transaction.get("amount"),
        "feeRate": fee_rate,
        "feeAmount": fee_amount,
        "clearingDelayDays": transaction.get("clearingDelayDays"),
        "category": category,
        "paymentChannel": get_payment_channel(transaction),
        "threeDS": transaction.get("threeDS"),
        "mcc": transaction.get("mcc"),
    }