from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List

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
        # Keep the original transaction unchanged
        original_transaction = deepcopy(transaction)

        # Create a copy that we are allowed to modify
        simulated_transaction = deepcopy(transaction)

        # Store every change made during simulation
        audit_trail = []

        # Apply each suggestion one by one
        for suggestion in suggestions:
            change = self._apply_suggestion(simulated_transaction, suggestion)

            # Only store changes that were actually applied
            if change is not None:
                audit_trail.append(change)

        # Validate the simulated transaction after all changes
        validation_messages = self._validate_transaction(simulated_transaction)

        # Transaction is valid if there are no validation messages
        is_valid = len(validation_messages) == 0

        # Return original, modified version, audit trail, and validation result
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
        # Field to update, for example "threeDS" or "clearingDate"
        field = suggestion.field

        # If the field does not exist, skip this suggestion
        if field not in transaction:
            return None

        # Current value before change
        original_value = transaction.get(field)

        # New value recommended by the suggestion
        new_value = suggestion.suggestedValue

        # If value is already correct, no change is needed
        if original_value == new_value:
            return None

        # Apply the suggested value
        transaction[field] = new_value

        # Return audit information about this change
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
        # Store validation messages here
        messages = []

        # Required transaction fields from the project scope
        required_fields = [
            "amount",
            "currency",
            "country",
            "cardType",
            "channel",
            "mcc",
            "threeDS",
            "authDate",
            "clearingDate",
            "cardBrand",
            "cardPresence",
            "transactionType",
        ]

        # Check if required fields are present
        for field in required_fields:
            if field not in transaction:
                messages.append(f"Missing required field: {field}")

        # Validate transaction amount
        amount = transaction.get("amount")

        if amount is None:
            messages.append("Amount is required")
        elif not isinstance(amount, (int, float)):
            messages.append("Amount must be a number")
        elif amount <= 0:
            messages.append("Amount must be greater than zero")

        # Validate 3DS value
        if "threeDS" in transaction and not isinstance(transaction["threeDS"], bool):
            messages.append("threeDS must be true or false")

        # Validate dates
        auth_date = transaction.get("authDate")
        clearing_date = transaction.get("clearingDate")

        if auth_date and clearing_date:
            try:
                auth_dt = datetime.fromisoformat(auth_date)
                clearing_dt = datetime.fromisoformat(clearing_date)

                if clearing_dt < auth_dt:
                    messages.append("Clearing date cannot be before authorization date")
            except ValueError:
                messages.append("authDate and clearingDate must use ISO format YYYY-MM-DD")

        # Validate card type
        valid_card_types = {"Credit", "Debit", "Prepaid", "Commercial"}
        card_type = transaction.get("cardType")

        if card_type and card_type not in valid_card_types:
            messages.append("cardType must be Credit, Debit, Prepaid, or Commercial")

        # Validate channel
        valid_channels = {"eCommerce", "POS", "MOTO"}
        channel = transaction.get("channel")

        if channel and channel not in valid_channels:
            messages.append("channel must be eCommerce, POS, or MOTO")

        return messages