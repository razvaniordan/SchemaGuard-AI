from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List

from core.transaction_schema import (
    REQUIRED_TRANSACTION_FIELDS,
    VALID_CARD_TYPES,
    VALID_CHANNELS,
    normalize_transaction,
)

from models.analysis_models import (
    ChangeSuggestion,
    TransactionChange,
    TransactionSimulationResponse,
)


class TransactionSimulator:
    def simulate(
        self,
        transaction: Dict[str, Any],
        suggestions: List[ChangeSuggestion],
    ) -> TransactionSimulationResponse:
        original_transaction = normalize_transaction(deepcopy(transaction))
        simulated_transaction = normalize_transaction(deepcopy(transaction))

        audit_trail = []

        for suggestion in suggestions:
            change = self._apply_suggestion(simulated_transaction, suggestion)

            if change is not None:
                audit_trail.append(change)

        simulated_transaction = normalize_transaction(simulated_transaction)

        validation_messages = self._validate_transaction(simulated_transaction)
        is_valid = len(validation_messages) == 0

        return TransactionSimulationResponse(
            originalTransaction=original_transaction,
            simulatedTransaction=simulated_transaction,
            auditTrail=audit_trail,
            valid=is_valid,
            validationMessages=validation_messages,
        )

    def _apply_suggestion(
        self,
        transaction: Dict[str, Any],
        suggestion: ChangeSuggestion,
    ) -> TransactionChange | None:
        field = suggestion.field

        if field not in transaction:
            return None

        original_value = transaction.get(field)
        new_value = suggestion.suggestedValue

        if original_value == new_value:
            return None

        transaction[field] = new_value

        return TransactionChange(
            field=field,
            originalValue=original_value,
            newValue=new_value,
            suggestionType=suggestion.suggestionType,
            reason=suggestion.description,
        )

    def _validate_transaction(
        self,
        transaction: Dict[str, Any],
    ) -> List[str]:
        messages = []

        for field in REQUIRED_TRANSACTION_FIELDS:
            if field not in transaction or transaction.get(field) is None:
                messages.append(f"Missing required field: {field}")

        amount = transaction.get("amount")

        if amount is None:
            messages.append("Amount is required")
        elif not isinstance(amount, (int, float)):
            messages.append("Amount must be a number")
        elif amount <= 0:
            messages.append("Amount must be greater than zero")

        if "threeDS" in transaction and not isinstance(transaction["threeDS"], bool):
            messages.append("threeDS must be true or false")

        auth_date = transaction.get("authDate")
        clearing_date = transaction.get("clearingDate")

        if auth_date and clearing_date:
            try:
                auth_dt = datetime.fromisoformat(str(auth_date))
                clearing_dt = datetime.fromisoformat(str(clearing_date))

                if clearing_dt < auth_dt:
                    messages.append("Clearing date cannot be before authorization date")
            except ValueError:
                messages.append("authDate and clearingDate must use ISO format")

        card_type = transaction.get("cardType")

        if card_type and card_type not in VALID_CARD_TYPES:
            messages.append("cardType must be Credit, Debit, Prepaid, or Commercial")

        channel = transaction.get("channel")

        if channel and channel not in VALID_CHANNELS:
            messages.append("channel must be eCommerce, POS, or MOTO")

        card_presence = transaction.get("cardPresence")

        if card_presence and card_presence not in {"card_present", "card_not_present"}:
            messages.append("cardPresence must be card_present or card_not_present")

        currency = transaction.get("currency")

        if currency and not isinstance(currency, str):
            messages.append("currency must be a string")

        merchant_country = transaction.get("merchantCountry")
        issuer_country = transaction.get("issuerCountry")

        if merchant_country and not isinstance(merchant_country, str):
            messages.append("merchantCountry must be a string")

        if issuer_country and not isinstance(issuer_country, str):
            messages.append("issuerCountry must be a string")

        mcc = transaction.get("mcc")

        if mcc and not isinstance(mcc, str):
            messages.append("mcc must be a string")

        clearing_delay_days = transaction.get("clearingDelayDays")

        if clearing_delay_days is not None:
            if not isinstance(clearing_delay_days, int):
                messages.append("clearingDelayDays must be an integer")
            elif clearing_delay_days < 0:
                messages.append("clearingDelayDays cannot be negative")

        return messages