"""FastAPI skeleton for the SchemeGuard rule engine service.

Story 2.2.2: rule-engine-python structure + FastAPI skeleton.

This service exposes the initial REST contract for transaction classification.
The actual ClassificationEngine implementation will be added in later subtasks.
"""

from __future__ import annotations
from core import ClassificationEngine, FeeCalculationService, StarSchemaETL
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import (
    CardType,
    Channel,
    ClassificationRequest,
    ClassificationResponse,
    FeeCalculationRequest,
    FeeCalculationResult,
    Region,
)

from rules import EU_PHASE_1_RULE_CATALOGUE

APP_NAME = "SchemeGuard Rule Engine"
APP_VERSION = "0.1.0"
PHASE = "EU Phase 1"
classification_engine = ClassificationEngine()
star_schema_etl = StarSchemaETL()
fee_calculation_service = FeeCalculationService()

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "Python rule engine service for transaction classification, "
        "interchange category selection, and future scheme compliance checks."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:4200",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:4200",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    """Simple healthcheck endpoint for local dev, CI, and Java integration."""

    return {
        "status": "UP",
        "service": APP_NAME,
        "version": APP_VERSION,
    }


@app.get("/metadata", tags=["system"])
def metadata() -> dict[str, object]:
    """Return service metadata and supported classification dimensions."""

    return {
        "service": APP_NAME,
        "version": APP_VERSION,
        "phase": PHASE,
        "supportedPriorities": {
            "min": 1,
            "max": 14,
        },
        "supportedChannels": [
            Channel.POS.value,
            Channel.ECOMMERCE.value,
            Channel.MOTO.value,
        ],
        "supportedCardTypes": [
            CardType.CREDIT.value,
            CardType.DEBIT.value,
            CardType.COMMERCIAL.value,
            CardType.PREPAID.value,
        ],
        "supportedRegions": [
            Region.EU.value,
            Region.CROSS_BORDER.value,
        ],
    }


@app.get("/categories", tags=["classification"])
def categories() -> list[dict[str, object]]:
    """Return the configured EU Phase 1 classification categories.

    This is useful for UI debugging and Java backend integration checks.
    """

    return EU_PHASE_1_RULE_CATALOGUE.as_api_response()


@app.post(
    "/classify-transaction",
    response_model=ClassificationResponse,
    tags=["classification"],
)
def classify_transaction(request: ClassificationRequest) -> ClassificationResponse:
    """Classify one transaction and return analytics-ready fact DTO.

    This endpoint is intended for Java backend integration.
    """

    classification_result = classification_engine.classify(request.transaction)

    fact_transaction = star_schema_etl.to_fact_transaction(
        transaction=request.transaction,
        classification=classification_result,
    )

    fee_calculation = fee_calculation_service.calculate_for_classification(
        transaction=request.transaction,
        classification=classification_result,
    )

    return ClassificationResponse(
        result=classification_result,
        factTransaction=fact_transaction,
        feeCalculation=fee_calculation,
    )

@app.post(
    "/calculate-fee",
    response_model=FeeCalculationResult,
    tags=["fees"],
)
def calculate_fee(request: FeeCalculationRequest) -> FeeCalculationResult:
    """Calculate a fee directly from amount, feeRate, currency, and optional caps."""

    return fee_calculation_service.calculate(request)