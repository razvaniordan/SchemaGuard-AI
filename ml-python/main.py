from fastapi import FastAPI
from typing import List
from core.transaction_simulator import TransactionSimulator
from core.missed_condition_detector import MissedConditionDetector
from core.change_suggestion_engine import ChangeSuggestionEngine
from core.ml_core import MLCore
from core.engines.ml_analytics_engine import MLAnalyticsEngine
from models.analysis_models import MLAnalyticsRequest, MLAnalyticsResponse
from models.analysis_models import MLCoreRequest, MLCoreResponse
from fastapi.responses import FileResponse
from core.engines.fee_comparison_engine import FeeComparisonEngine
from models.analysis_models import FeeComparisonRequest, FeeComparisonResponse
from core.exporters.pdf_report_exporter import PDFReportExporter
from core.engines.ai_report_generation_engine import AIReportGenerationEngine
from models.analysis_models import AIReportRequest, AIReportResponse
from core.engines.recommendation_prioritization_engine import RecommendationPrioritizationEngine
from models.analysis_models import (
    RecommendationPrioritizationRequest,
    RecommendationPrioritizationResponse,
)
from models.analysis_models import (
    RuleEngineResult,
    MissedConditionAnalysis,
    ChangeSuggestionResponse,
    TransactionSimulationRequest,
    TransactionSimulationResponse,
    PortfolioPatternResponse,
    AnomalyDetectionResponse,
    BulkSimulationRequest,
    BulkSimulationResponse,
    RootCauseAnalysisResponse,
)


app = FastAPI(title="SchemeGuard AI ML Service")

# Create service instances
detector = MissedConditionDetector()
suggestion_engine = ChangeSuggestionEngine()
simulator = TransactionSimulator()
ml_core = MLCore()
recommendation_prioritization_engine = RecommendationPrioritizationEngine()
ai_report_generation_engine = AIReportGenerationEngine()
pdf_report_exporter = PDFReportExporter()
ml_analytics_engine = MLAnalyticsEngine()
fee_comparison_engine = FeeComparisonEngine()

@app.post("/missed-conditions", response_model=MissedConditionAnalysis)
def analyze_missed_conditions(
    currentResult: RuleEngineResult,
    optimalResult: RuleEngineResult,
):
    # Compare current and optimal result
    return detector.analyze(currentResult, optimalResult)


@app.post("/change-suggestions", response_model=ChangeSuggestionResponse)
def generate_change_suggestions(
    currentResult: RuleEngineResult,
    optimalResult: RuleEngineResult,
):
    # First detect missed conditions
    analysis = detector.analyze(currentResult, optimalResult)

    # Then convert missed conditions into actionable suggestions
    suggestions = suggestion_engine.generate_suggestions(analysis.missedConditions)

    # Return sorted suggestions
    return ChangeSuggestionResponse(suggestions=suggestions)

@app.post("/simulate-transaction", response_model=TransactionSimulationResponse)
def simulate_transaction(request: TransactionSimulationRequest):
    # Apply suggestions to transaction and return simulated result
    return simulator.simulate(request.transaction, request.suggestions)

@app.post("/ml-core/analyze", response_model=MLCoreResponse)
def analyze_with_ml_core(request: MLCoreRequest):
    # Run full ML pipeline:
    # missed condition detection -> suggestion generation -> simulation -> scoring
    return ml_core.analyze_transaction(
        request.currentResult,
        request.optimalResult,
    )

@app.post("/ml-core/analyze-portfolio", response_model=PortfolioPatternResponse)
def analyze_portfolio(
    analyses: List[MissedConditionAnalysis],
):
    """
    Analyze a portfolio of transaction analyses.

    This endpoint aggregates missed conditions across multiple transactions
    and returns high-level insights such as:
    - Most common issue
    - Highest impact driver
    - Total savings opportunity
    """

    return ml_core.analyze_portfolio(analyses)

@app.post("/ml-core/detect-anomalies", response_model=AnomalyDetectionResponse)
def detect_anomalies(
    results: List[RuleEngineResult],
):
    """
    Detect abnormal transactions across multiple rule engine results.

    This endpoint identifies:
    - Fee outliers
    - Category mismatches
    - Timing anomalies
    """

    return ml_core.detect_anomalies(results)

@app.post("/ml-core/simulate-bulk", response_model=BulkSimulationResponse)
def simulate_bulk_scenarios(
    request: BulkSimulationRequest,
):
    """
    Simulate applying top recommendations across many transactions.

    Returns total current fees, estimated simulated fees, total savings,
    and savings grouped by recommendation type.
    """

    return ml_core.simulate_bulk_scenarios(request)

@app.post("/ml-core/root-causes", response_model=RootCauseAnalysisResponse)
def analyze_root_causes(
    analyses: List[MissedConditionAnalysis],
):
    """
    Analyze missed conditions across a portfolio and return ranked root causes.

    This helps identify systemic optimization issues rather than isolated
    transaction-level problems.
    """

    return ml_core.analyze_root_causes(analyses)

@app.post(
    "/ml-core/prioritize-recommendations",
    response_model=RecommendationPrioritizationResponse,
)
def prioritize_recommendations(request: RecommendationPrioritizationRequest):
    # Rank optimization recommendations using heuristic or ML ranking.
    return recommendation_prioritization_engine.prioritize(request)

@app.post("/ml-core/generate-report", response_model=AIReportResponse)
def generate_ai_report(request: AIReportRequest):
    # Generate a portfolio-level AI report using ML recommendations, anomalies, and root causes.
    return ai_report_generation_engine.generate_report(request)

@app.post("/ml-core/generate-report/pdf")
def generate_ai_report_pdf(request: AIReportRequest):
    # Generate the report data first.
    report = ai_report_generation_engine.generate_report(request)

    # Export the structured report to PDF.
    output_path = f"reports/generated/{report.reportId}.pdf"
    pdf_path = pdf_report_exporter.export(report, output_path)

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"{report.summary.reportName}.pdf",
    )

@app.post("/ml-core/analytics/portfolio", response_model=MLAnalyticsResponse)
def analyze_ml_portfolio(request: MLAnalyticsRequest):
    # Generate portfolio-level ML analytics and transaction drill-down insights.
    return ml_analytics_engine.analyze_portfolio(request)

@app.post("/ml-core/compare-fees", response_model=FeeComparisonResponse)
def compare_fees(request: FeeComparisonRequest):
    # Compare current and optimized fees using deterministic and ML-assisted savings.
    return fee_comparison_engine.compare_fees(request)