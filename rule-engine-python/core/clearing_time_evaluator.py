"""Clearing time evaluation logic.

Story 2.2.7: Clearing time evaluator with Python datetime.

For EU Phase 1:
- Clearing within 24 hours qualifies as <=24h.
- Clearing after 24 hours qualifies as >24h.
- Missing or invalid dates return Unknown.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from decimal import Decimal

from models import ClearingTimeBand, TransactionInput

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ClearingTimeEvaluation:
    """Derived clearing time band for a transaction."""

    band: ClearingTimeBand
    source: str
    elapsed_hours: Decimal | None = None
    reason_code: str | None = None
    message: str | None = None


class ClearingTimeEvaluator:
    """Evaluate clearing delay between authDate and clearingDate."""

    def evaluate(self, transaction: TransactionInput) -> ClearingTimeEvaluation:
        """Derive clearing time band from authDate and clearingDate."""

        if transaction.auth_date is None or transaction.clearing_date is None:
            logger.info(
                "Missing clearing dates for transaction_id=%s auth_date=%s clearing_date=%s",
                transaction.transaction_id,
                transaction.auth_date,
                transaction.clearing_date,
            )

            return ClearingTimeEvaluation(
                band=ClearingTimeBand.UNKNOWN,
                source="missing",
                reason_code="MISSING_CLEARING_TIME",
                message="authDate and clearingDate are required for clearing time evaluation.",
            )

        auth_datetime = self._to_datetime(transaction.auth_date)
        clearing_datetime = self._to_datetime(transaction.clearing_date)

        if clearing_datetime < auth_datetime:
            logger.warning(
                "clearingDate is before authDate for transaction_id=%s auth_date=%s clearing_date=%s",
                transaction.transaction_id,
                auth_datetime,
                clearing_datetime,
            )

            return ClearingTimeEvaluation(
                band=ClearingTimeBand.UNKNOWN,
                source="invalid",
                reason_code="INVALID_CLEARING_BEFORE_AUTH",
                message="clearingDate cannot be before authDate.",
            )

        elapsed_seconds = Decimal(str((clearing_datetime - auth_datetime).total_seconds()))
        elapsed_hours = elapsed_seconds / Decimal("3600")

        if elapsed_hours <= Decimal("24"):
            return ClearingTimeEvaluation(
                band=ClearingTimeBand.WITHIN_24H,
                source="datetime",
                elapsed_hours=elapsed_hours,
                reason_code="CLEARING_WITHIN_24H",
                message="Clearing completed within 24 hours.",
            )

        return ClearingTimeEvaluation(
            band=ClearingTimeBand.OVER_24H,
            source="datetime",
            elapsed_hours=elapsed_hours,
            reason_code="CLEARING_OVER_24H",
            message="Clearing completed after 24 hours.",
        )

    def _to_datetime(self, value: date | datetime) -> datetime:
        """Normalize date/datetime values to timezone-aware datetime.

        Date-only values are interpreted as midnight UTC.
        Naive datetimes are interpreted as UTC.
        Aware datetimes preserve their timezone information.
        """

        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc)

            return value

        return datetime.combine(value, time.min, tzinfo=timezone.utc)