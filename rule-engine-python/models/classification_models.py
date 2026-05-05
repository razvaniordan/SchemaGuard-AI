"""Pydantic contracts for transaction classification.

These models define the public contract between the Java backend and the
Python rule engine."""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Channel(str, Enum):
    POS = "POS"
    ECOMMERCE = "eCommerce"
    MOTO = "MOTO"
    ANY = "Any"
    UNKNOWN = "Unknown"


class AuthStatus(str, Enum):
    SECURE = "Secure"
    NON_SECURE = "Non-Secure"
    NOT_APPLICABLE = "N/A"
    ANY = "Any"
    UNKNOWN = "Unknown"


class ClearingTimeBand(str, Enum):
    WITHIN_24H = "<=24h"
    OVER_24H = ">24h"
    ANY = "Any"
    UNKNOWN = "Unknown"


class CardType(str, Enum):
    CREDIT = "Credit"
    DEBIT = "Debit"
    COMMERCIAL = "Commercial"
    PREPAID = "Prepaid"
    ANY = "Any"
    UNKNOWN = "Unknown"


class Region(str, Enum):
    EU = "EU"
    CROSS_BORDER = "Cross-Border"
    ANY = "Any"
    UNKNOWN = "Unknown"


class ConditionOutcome(str, Enum):
    MATCHED = "MATCHED"
    NOT_MATCHED = "NOT_MATCHED"
    MISSING = "MISSING"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class InterchangeCategory(str, Enum):
    ECOM_SECURE_PREFERRED_CREDIT = "Ecom Secure Preferred Credit"
    ECOM_SECURE_NON_PREFERRED_CREDIT = "Ecom Secure Non-Preferred Credit"
    ECOM_NON_SECURE_CREDIT = "Ecom Non-Secure Credit"
    ECOM_SECURE_DEBIT = "Ecom Secure Debit"
    ECOM_NON_SECURE_DEBIT = "Ecom Non-Secure Debit"
    POS_DEBIT_REGULATED = "POS Debit Regulated"
    POS_CREDIT = "POS Credit"
    MOTO_CREDIT = "MOTO Credit"
    MOTO_DEBIT = "MOTO Debit"
    CROSS_BORDER_CREDIT = "Cross-Border Credit"
    CROSS_BORDER_DEBIT = "Cross-Border Debit"
    COMMERCIAL_CARD = "Commercial Card"
    MCC_PREFERRED_GROCERY = "MCC Preferred (Grocery)"
    DEFAULT_STANDARD_CATEGORY = "Default Standard Category"


class TransactionInput(BaseModel):
    """Canonical input accepted by ClassificationEngine.classify().

    This model is intentionally permissive. Missing fields are allowed because
    later subtasks will handle defaults, logging, and confidence penalties.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
        json_encoders={Decimal: lambda value: float(value)},
    )

    transaction_id: Optional[str] = Field(default=None, alias="transactionId")
    merchant_id: Optional[str] = Field(default=None, alias="merchantId")
    card_id: Optional[str] = Field(default=None, alias="cardId")

    amount: Optional[Decimal] = None
    currency: Optional[str] = None

    # Backward-compatible with current Java Transaction.country
    country: Optional[str] = None

    merchant_country: Optional[str] = Field(default=None, alias="merchantCountry")
    issuer_country: Optional[str] = Field(default=None, alias="issuerCountry")
    region: Optional[Region] = None

    card_type: Optional[CardType] = Field(default=None, alias="cardType")
    card_brand: Optional[str] = Field(default=None, alias="cardBrand")
    card_presence: Optional[str] = Field(default=None, alias="cardPresence")

    channel: Optional[Channel] = None
    mcc: Optional[str] = None
    transaction_type: Optional[str] = Field(default=None, alias="transactionType")

    three_ds: Optional[bool] = Field(default=None, alias="threeDS")
    eci: Optional[str] = None

    auth_date: Optional[date | datetime] = Field(default=None, alias="authDate")
    clearing_date: Optional[date | datetime] = Field(default=None, alias="clearingDate")

    @field_validator("currency", "country", "merchant_country", "issuer_country", mode="before")
    @classmethod
    def normalize_uppercase_strings(cls, value: Any) -> Any:
        if value is None or value == "":
            return None
        return str(value).strip().upper()

    @field_validator("mcc", mode="before")
    @classmethod
    def normalize_mcc(cls, value: Any) -> Optional[str]:
        if value is None or value == "":
            return None

        normalized = str(value).strip()

        if normalized.isdigit():
            return normalized.zfill(4)

        return normalized

    @field_validator("eci", mode="before")
    @classmethod
    def normalize_eci(cls, value: Any) -> Optional[str]:
        if value is None or value == "":
            return None

        normalized = str(value).strip()

        if normalized.isdigit():
            return normalized.zfill(2)

        return normalized

    @field_validator("channel", mode="before")
    @classmethod
    def normalize_channel(cls, value: Any) -> Optional[Channel]:
        if value is None or value == "":
            return None

        normalized = str(value).strip().lower().replace("-", "_").replace(" ", "_")

        channel_map = {
            "pos": Channel.POS,
            "card_present": Channel.POS,
            "cardpresent": Channel.POS,
            "ecommerce": Channel.ECOMMERCE,
            "e_commerce": Channel.ECOMMERCE,
            "ecom": Channel.ECOMMERCE,
            "online": Channel.ECOMMERCE,
            "moto": Channel.MOTO,
            "mail_order_telephone_order": Channel.MOTO,
            "any": Channel.ANY,
            "unknown": Channel.UNKNOWN,
        }

        return channel_map.get(normalized, Channel.UNKNOWN)

    @field_validator("card_type", mode="before")
    @classmethod
    def normalize_card_type(cls, value: Any) -> Optional[CardType]:
        if value is None or value == "":
            return None

        normalized = str(value).strip().lower().replace("-", "_").replace(" ", "_")

        card_type_map = {
            "credit": CardType.CREDIT,
            "consumer_credit": CardType.CREDIT,
            "debit": CardType.DEBIT,
            "consumer_debit": CardType.DEBIT,
            "commercial": CardType.COMMERCIAL,
            "business": CardType.COMMERCIAL,
            "corporate": CardType.COMMERCIAL,
            "purchasing": CardType.COMMERCIAL,
            "prepaid": CardType.PREPAID,
            "any": CardType.ANY,
            "unknown": CardType.UNKNOWN,
        }

        return card_type_map.get(normalized, CardType.UNKNOWN)

    @field_validator("region", mode="before")
    @classmethod
    def normalize_region(cls, value: Any) -> Optional[Region]:
        if value is None or value == "":
            return None

        normalized = str(value).strip().lower().replace("_", "-")

        region_map = {
            "eu": Region.EU,
            "europe": Region.EU,
            "cross-border": Region.CROSS_BORDER,
            "crossborder": Region.CROSS_BORDER,
            "international": Region.CROSS_BORDER,
            "any": Region.ANY,
            "unknown": Region.UNKNOWN,
        }

        return region_map.get(normalized, Region.UNKNOWN)


class ClassificationConditionResult(BaseModel):
    """One condition-level result used for auditability and confidence scoring."""

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
        json_encoders={Decimal: lambda value: float(value)},
    )

    field: str
    expected: Optional[Any] = None
    actual: Optional[Any] = None
    outcome: ConditionOutcome
    reason_code: Optional[str] = Field(default=None, alias="reasonCode")
    message: Optional[str] = None


class ClassificationResult(BaseModel):
    """Public output returned by ClassificationEngine.classify()."""

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
        json_encoders={Decimal: lambda value: float(value)},
    )

    transaction_id: Optional[str] = Field(default=None, alias="transactionId")

    category: InterchangeCategory
    category_code: str = Field(alias="categoryCode")
    rule_priority: int = Field(alias="rulePriority", ge=1, le=14)

    # feeRate is decimal fraction: 1.25% = 0.0125
    fee_rate: Decimal = Field(alias="feeRate", ge=Decimal("0"))
    fee_rate_percent: Decimal = Field(alias="feeRatePercent", ge=Decimal("0"))
    fee_rate_bps: int = Field(alias="feeRateBps", ge=0)

    confidence: Decimal = Field(ge=Decimal("0"), le=Decimal("1"))

    matched_conditions: list[str] = Field(default_factory=list, alias="matchedConditions")
    missing_fields: list[str] = Field(default_factory=list, alias="missingFields")
    reason_codes: list[str] = Field(default_factory=list, alias="reasonCodes")

    condition_results: list[ClassificationConditionResult] = Field(
        default_factory=list,
        alias="conditionResults",
    )

    explanation: str
    classified_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        alias="classifiedAt",
    )


class CategoryDefinition(BaseModel):
    """Configuration contract for a priority-based interchange category."""

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
        json_encoders={Decimal: lambda value: float(value)},
    )

    priority: int = Field(ge=1, le=14)
    channel: Channel
    auth_status: AuthStatus = Field(alias="authStatus")
    clearing_time: ClearingTimeBand = Field(alias="clearingTime")
    card_type: CardType = Field(alias="cardType")
    region: Region
    mcc: str = "Any"

    category: InterchangeCategory
    category_code: str = Field(alias="categoryCode")

    fee_rate: Decimal = Field(alias="feeRate", ge=Decimal("0"))
    fee_rate_percent: Decimal = Field(alias="feeRatePercent", ge=Decimal("0"))
    fee_rate_bps: int = Field(alias="feeRateBps", ge=0)


class FactTransactionRecord(BaseModel):
    """Future fact_transactions shape for the star schema ETL step.

    This only defines the contract. The actual ETL will be implemented later.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
        json_encoders={Decimal: lambda value: float(value)},
    )

    fact_transaction_id: Optional[str] = Field(default=None, alias="factTransactionId")
    transaction_id: Optional[str] = Field(default=None, alias="transactionId")

    dim_merchant_key: Optional[int] = Field(default=None, alias="dimMerchantKey")
    dim_card_key: Optional[int] = Field(default=None, alias="dimCardKey")
    dim_channel_key: Optional[int] = Field(default=None, alias="dimChannelKey")
    dim_region_key: Optional[int] = Field(default=None, alias="dimRegionKey")
    dim_date_key: Optional[int] = Field(default=None, alias="dimDateKey")
    dim_category_key: Optional[int] = Field(default=None, alias="dimCategoryKey")

    amount: Optional[Decimal] = None
    currency: Optional[str] = None

    category_code: str = Field(alias="categoryCode")
    fee_rate: Decimal = Field(alias="feeRate")
    confidence: Decimal
    rule_priority: int = Field(alias="rulePriority")
    classified_at: datetime = Field(alias="classifiedAt")


class ClassificationRequest(BaseModel):
    """REST request wrapper for future Java backend integration."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    transaction: TransactionInput


class ClassificationResponse(BaseModel):
    """REST response wrapper for future Java backend integration."""

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
        json_encoders={Decimal: lambda value: float(value)},
    )

    result: ClassificationResult
    fact_transaction: Optional[FactTransactionRecord] = Field(
        default=None,
        alias="factTransaction",
    )


def _category(
    *,
    priority: int,
    channel: Channel,
    auth_status: AuthStatus,
    clearing_time: ClearingTimeBand,
    card_type: CardType,
    region: Region,
    category: InterchangeCategory,
    category_code: str,
    fee_rate: str,
    fee_rate_percent: str,
    fee_rate_bps: int,
    mcc: str = "Any",
) -> CategoryDefinition:
    return CategoryDefinition(
        priority=priority,
        channel=channel,
        authStatus=auth_status,
        clearingTime=clearing_time,
        cardType=card_type,
        region=region,
        mcc=mcc,
        category=category,
        categoryCode=category_code,
        feeRate=Decimal(fee_rate),
        feeRatePercent=Decimal(fee_rate_percent),
        feeRateBps=fee_rate_bps,
    )


EU_PHASE_1_CATEGORY_DEFINITIONS: tuple[CategoryDefinition, ...] = (
    _category(
        priority=1,
        channel=Channel.ECOMMERCE,
        auth_status=AuthStatus.SECURE,
        clearing_time=ClearingTimeBand.WITHIN_24H,
        card_type=CardType.CREDIT,
        region=Region.EU,
        category=InterchangeCategory.ECOM_SECURE_PREFERRED_CREDIT,
        category_code="ECOM_SECURE_PREFERRED_CREDIT",
        fee_rate="0.0125",
        fee_rate_percent="1.25",
        fee_rate_bps=125,
    ),
    _category(
        priority=2,
        channel=Channel.ECOMMERCE,
        auth_status=AuthStatus.SECURE,
        clearing_time=ClearingTimeBand.OVER_24H,
        card_type=CardType.CREDIT,
        region=Region.EU,
        category=InterchangeCategory.ECOM_SECURE_NON_PREFERRED_CREDIT,
        category_code="ECOM_SECURE_NON_PREFERRED_CREDIT",
        fee_rate="0.0150",
        fee_rate_percent="1.50",
        fee_rate_bps=150,
    ),
    _category(
        priority=3,
        channel=Channel.ECOMMERCE,
        auth_status=AuthStatus.NON_SECURE,
        clearing_time=ClearingTimeBand.ANY,
        card_type=CardType.CREDIT,
        region=Region.EU,
        category=InterchangeCategory.ECOM_NON_SECURE_CREDIT,
        category_code="ECOM_NON_SECURE_CREDIT",
        fee_rate="0.0185",
        fee_rate_percent="1.85",
        fee_rate_bps=185,
    ),
    _category(
        priority=4,
        channel=Channel.ECOMMERCE,
        auth_status=AuthStatus.SECURE,
        clearing_time=ClearingTimeBand.ANY,
        card_type=CardType.DEBIT,
        region=Region.EU,
        category=InterchangeCategory.ECOM_SECURE_DEBIT,
        category_code="ECOM_SECURE_DEBIT",
        fee_rate="0.0020",
        fee_rate_percent="0.20",
        fee_rate_bps=20,
    ),
    _category(
        priority=5,
        channel=Channel.ECOMMERCE,
        auth_status=AuthStatus.NON_SECURE,
        clearing_time=ClearingTimeBand.ANY,
        card_type=CardType.DEBIT,
        region=Region.EU,
        category=InterchangeCategory.ECOM_NON_SECURE_DEBIT,
        category_code="ECOM_NON_SECURE_DEBIT",
        fee_rate="0.0030",
        fee_rate_percent="0.30",
        fee_rate_bps=30,
    ),
    _category(
        priority=6,
        channel=Channel.POS,
        auth_status=AuthStatus.NOT_APPLICABLE,
        clearing_time=ClearingTimeBand.WITHIN_24H,
        card_type=CardType.DEBIT,
        region=Region.EU,
        category=InterchangeCategory.POS_DEBIT_REGULATED,
        category_code="POS_DEBIT_REGULATED",
        fee_rate="0.0020",
        fee_rate_percent="0.20",
        fee_rate_bps=20,
    ),
    _category(
        priority=7,
        channel=Channel.POS,
        auth_status=AuthStatus.NOT_APPLICABLE,
        clearing_time=ClearingTimeBand.WITHIN_24H,
        card_type=CardType.CREDIT,
        region=Region.EU,
        category=InterchangeCategory.POS_CREDIT,
        category_code="POS_CREDIT",
        fee_rate="0.0090",
        fee_rate_percent="0.90",
        fee_rate_bps=90,
    ),
    _category(
        priority=8,
        channel=Channel.MOTO,
        auth_status=AuthStatus.NOT_APPLICABLE,
        clearing_time=ClearingTimeBand.ANY,
        card_type=CardType.CREDIT,
        region=Region.ANY,
        category=InterchangeCategory.MOTO_CREDIT,
        category_code="MOTO_CREDIT",
        fee_rate="0.0190",
        fee_rate_percent="1.90",
        fee_rate_bps=190,
    ),
    _category(
        priority=9,
        channel=Channel.MOTO,
        auth_status=AuthStatus.NOT_APPLICABLE,
        clearing_time=ClearingTimeBand.ANY,
        card_type=CardType.DEBIT,
        region=Region.ANY,
        category=InterchangeCategory.MOTO_DEBIT,
        category_code="MOTO_DEBIT",
        fee_rate="0.0035",
        fee_rate_percent="0.35",
        fee_rate_bps=35,
    ),
    _category(
        priority=10,
        channel=Channel.ANY,
        auth_status=AuthStatus.ANY,
        clearing_time=ClearingTimeBand.ANY,
        card_type=CardType.CREDIT,
        region=Region.CROSS_BORDER,
        category=InterchangeCategory.CROSS_BORDER_CREDIT,
        category_code="CROSS_BORDER_CREDIT",
        fee_rate="0.0250",
        fee_rate_percent="2.50",
        fee_rate_bps=250,
    ),
    _category(
        priority=11,
        channel=Channel.ANY,
        auth_status=AuthStatus.ANY,
        clearing_time=ClearingTimeBand.ANY,
        card_type=CardType.DEBIT,
        region=Region.CROSS_BORDER,
        category=InterchangeCategory.CROSS_BORDER_DEBIT,
        category_code="CROSS_BORDER_DEBIT",
        fee_rate="0.0100",
        fee_rate_percent="1.00",
        fee_rate_bps=100,
    ),
    _category(
        priority=12,
        channel=Channel.ANY,
        auth_status=AuthStatus.ANY,
        clearing_time=ClearingTimeBand.ANY,
        card_type=CardType.COMMERCIAL,
        region=Region.ANY,
        category=InterchangeCategory.COMMERCIAL_CARD,
        category_code="COMMERCIAL_CARD",
        fee_rate="0.0220",
        fee_rate_percent="2.20",
        fee_rate_bps=220,
    ),
    _category(
        priority=13,
        channel=Channel.ANY,
        auth_status=AuthStatus.ANY,
        clearing_time=ClearingTimeBand.ANY,
        card_type=CardType.ANY,
        region=Region.EU,
        mcc="5411",
        category=InterchangeCategory.MCC_PREFERRED_GROCERY,
        category_code="MCC_PREFERRED_GROCERY",
        fee_rate="0.0015",
        fee_rate_percent="0.15",
        fee_rate_bps=15,
    ),
    _category(
        priority=14,
        channel=Channel.ANY,
        auth_status=AuthStatus.ANY,
        clearing_time=ClearingTimeBand.ANY,
        card_type=CardType.ANY,
        region=Region.ANY,
        category=InterchangeCategory.DEFAULT_STANDARD_CATEGORY,
        category_code="DEFAULT_STANDARD_CATEGORY",
        fee_rate="0.0175",
        fee_rate_percent="1.75",
        fee_rate_bps=175,
    ),
)