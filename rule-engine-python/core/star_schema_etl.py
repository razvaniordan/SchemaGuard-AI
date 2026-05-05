"""Star-schema ETL mapper for fact_transactions.

Story 2.2.10: Star-schema ETL DTO for fact_transactions.

This module transforms operational classification data into an analytics-ready
fact transaction DTO. It does not persist data to a database yet.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any

from models import (
    Channel,
    ClassificationResult,
    FactTransactionRecord,
    Region,
    TransactionInput,
)

logger = logging.getLogger(__name__)


UNKNOWN_DIMENSION_KEY = 0

CHANNEL_DIMENSION_KEYS: dict[Channel, int] = {
    Channel.UNKNOWN: 0,
    Channel.POS: 1,
    Channel.ECOMMERCE: 2,
    Channel.MOTO: 3,
    Channel.ANY: 4,
}

REGION_DIMENSION_KEYS: dict[Region, int] = {
    Region.UNKNOWN: 0,
    Region.EU: 1,
    Region.CROSS_BORDER: 2,
    Region.ANY: 3,
}


class StarSchemaETL:
    """Transform classification output into fact_transactions shape."""

    def to_fact_transaction(
        self,
        *,
        transaction: TransactionInput,
        classification: ClassificationResult,
    ) -> FactTransactionRecord:
        """Create a FactTransactionRecord from transaction and classification data."""

        transaction_id = (
            classification.transaction_id
            or transaction.transaction_id
        )

        fact_transaction_id = self._fact_transaction_id(transaction_id)

        dim_date_key = self._date_key(
            transaction.auth_date
            or classification.classified_at
        )

        return FactTransactionRecord(
            factTransactionId=fact_transaction_id,
            transactionId=transaction_id,
            dimMerchantKey=self._deterministic_key(transaction.merchant_id),
            dimCardKey=self._deterministic_key(transaction.card_id),
            dimChannelKey=self._channel_key(transaction.channel),
            dimRegionKey=self._region_key(transaction.region),
            dimDateKey=dim_date_key,
            dimCategoryKey=self._deterministic_key(classification.category_code),
            amount=transaction.amount,
            currency=transaction.currency,
            categoryCode=classification.category_code,
            feeRate=classification.fee_rate,
            confidence=classification.confidence,
            rulePriority=classification.rule_priority,
            classifiedAt=classification.classified_at,
        )

    def _fact_transaction_id(self, transaction_id: str | None) -> str:
        if transaction_id:
            return f"fact-{transaction_id}"

        logger.info("Missing transaction_id while building fact transaction ID.")
        return f"fact-generated-{self._deterministic_key('missing-transaction-id')}"

    def _channel_key(self, channel: Channel | None) -> int:
        if channel is None:
            logger.info("Missing channel while building dimChannelKey.")
            return UNKNOWN_DIMENSION_KEY

        return CHANNEL_DIMENSION_KEYS.get(channel, UNKNOWN_DIMENSION_KEY)

    def _region_key(self, region: Region | None) -> int:
        if region is None:
            logger.info("Missing region while building dimRegionKey.")
            return UNKNOWN_DIMENSION_KEY

        return REGION_DIMENSION_KEYS.get(region, UNKNOWN_DIMENSION_KEY)

    def _date_key(self, value: date | datetime | None) -> int:
        """Convert date/datetime into YYYYMMDD integer key."""

        if value is None:
            logger.info("Missing date while building dimDateKey.")
            return UNKNOWN_DIMENSION_KEY

        if isinstance(value, datetime):
            normalized = value

            if normalized.tzinfo is None:
                normalized = normalized.replace(tzinfo=timezone.utc)

            return int(normalized.strftime("%Y%m%d"))

        return int(value.strftime("%Y%m%d"))

    def _deterministic_key(self, value: Any) -> int:
        """Return stable positive integer key for a dimension natural key.

        Python's built-in hash() is intentionally not used because it is not
        stable across interpreter sessions.
        """

        if value is None or value == "":
            return UNKNOWN_DIMENSION_KEY

        normalized = str(value).strip().lower()

        digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()

        # Keep the key in a signed 32-bit friendly range.
        return int(digest[:8], 16) % 2_147_483_647