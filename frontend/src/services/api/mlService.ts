import type {
  AnomalyDto,
  MissedConditionDto,
  OptimizationReportDto,
  RecommendationDto,
  TransactionPageDto,
  TransactionDto,
} from './types';
import { apiClient } from './client';
type BackendTransaction = {
  transactionId: number;
  clientId?: number;
  clientName?: string;
  merchantId?: number;
  merchantName?: string;
  merchantCountryCode?: string;
  merchantCountryName?: string;
  mccCode?: string;
  cardId?: number;
  acquiringPartnerId?: number;
  acquiringPartnerName?: string;
  acquirerCountryCode?: string;
  acquirerCountryName?: string;
  issuerBankId?: number;
  issuerBankName?: string;
  issuerCountryCode?: string;
  issuerCountryName?: string;
  cardNetworkId?: number;
  cardNetworkName?: string;
  transactionAmount?: number | string;
  transactionCurrency?: string;
  transactionChannel?: 'ECOMMERCE' | 'POS' | 'ATM' | string;
  authorizationDatetime?: string | null;
  clearingDatetime?: string | null;
  transactionStatus?: 'APPROVED' | 'DECLINED' | 'PENDING' | string;
  is3dsAuthenticated?: 'Y' | 'N' | string | null;
  eciValue?: string | null;
  regionCode?: string;
};

type BackendTransactionPage = {
  rows?: BackendTransaction[];
  content?: BackendTransaction[];
  data?: BackendTransaction[];
  items?: BackendTransaction[];
  transactions?: BackendTransaction[];
  total?: number;
  page?: number;
  pageSize?: number;
  totalPages?: number;
};



type BackendClassificationResponse = {
  result?: {
    transactionId?: string | number;
    category?: string;
    categoryCode?: string;
    rulePriority?: number;
    feeRate?: number;
    feeRatePercent?: number;
    feeRateBps?: number;
    confidence?: number;
    matchedConditions?: string[];
    missingFields?: string[];
    reasonCodes?: string[];
    conditionResults?: Array<{
      field?: string;
      expected?: string;
      actual?: string;
      outcome?: string;
      reasonCode?: string | null;
      message?: string;
    }>;
    explanation?: string;
    classifiedAt?: string;
  };
  factTransaction?: {
    factTransactionId?: string;
    transactionId?: string | number;
    amount?: number;
    currency?: string;
    categoryCode?: string;
    feeRate?: number;
    confidence?: number;
    rulePriority?: number;
    classifiedAt?: string;
  };
  feeCalculation?: {
    amount?: number;
    feeRate?: number;
    rawFee?: number;
    finalFee?: number;
    currency?: string;
    capApplied?: string | null;
    calculationMethod?: string;
    finalFeeEur?: number | null;
  };
};

export type TransactionClassification = {
  transactionId: string;
  category: string;
  categoryCode: string;
  rulePriority: number | null;
  feeRate: number;
  feeRatePercent: number;
  feeAmount: number;
  currency: string;
  confidence: number;
  matchedConditions: string[];
  missingFields: string[];
  reasonCodes: string[];
  conditionResults: Array<{
    field: string;
    expected: string;
    actual: string;
    outcome: string;
    reasonCode?: string | null;
    message: string;
  }>;
  explanation: string;
  calculationMethod: string;
  classifiedAt?: string;
};

type BackendOptimizationReport = {
  transactionId: number;
  summary?: string;
  feeComparison?: Record<string, unknown>;
  savingsProjections?: Record<string, unknown>;
  missedConditions?: Record<string, unknown> | unknown[];
  rankedRecommendations?: Record<string, unknown> | unknown[];
  anomalyInsights?: Record<string, unknown> | unknown[];
};

type BackendMissedConditionsResponse = {
  missedConditions?: unknown[];
  conditions?: unknown[];
};

const DEFAULT_TRANSACTION_ID = '1';

function backendId(transactionId?: string | null): string {
  if (!transactionId) return DEFAULT_TRANSACTION_ID;
  const numericId = transactionId.match(/\d+/)?.[0];
  return numericId ?? DEFAULT_TRANSACTION_ID;
}

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : {};
}

function asNumber(value: unknown, fallback = 0): number {
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  if (typeof value === 'string' && value.trim() !== '') {
    const parsed = Number(value);
    if (Number.isFinite(parsed)) return parsed;
  }
  return fallback;
}

function asString(value: unknown, fallback = 'N/A'): string {
  return typeof value === 'string' && value.length > 0 ? value : fallback;
}

function firstNumber(source: Record<string, unknown>, keys: string[], fallback = 0): number {
  for (const key of keys) {
    if (source[key] !== undefined && source[key] !== null) {
      return asNumber(source[key], fallback);
    }
  }
  return fallback;
}

function firstString(source: Record<string, unknown>, keys: string[], fallback = 'N/A'): string {
  for (const key of keys) {
    if (source[key] !== undefined && source[key] !== null) {
      return asString(source[key], fallback);
    }
  }
  return fallback;
}

function firstValue(source: Record<string, unknown>, keys: string[]): unknown {
  for (const key of keys) {
    if (source[key] !== undefined && source[key] !== null) {
      return source[key];
    }
  }

  return undefined;
}

function displayValue(value: unknown, fallback = 'N/A'): string {
  if (typeof value === 'string' && value.length > 0) return value;
  if (typeof value === 'number' && Number.isFinite(value)) return String(value);
  if (typeof value === 'boolean') return value ? 'Yes' : 'No';

  return fallback;
}

function displayImpact(value: unknown): string {
  if (typeof value === 'number' && Number.isFinite(value)) {
    if (value === 0) return 'No measurable fee-rate impact';

    return `${(value * 100).toFixed(2)} pp fee-rate opportunity`;
  }

  return displayValue(value, 'May prevent optimal fee qualification.');
}

function nestedRecord(source: Record<string, unknown>, keys: string[]): Record<string, unknown> {
  for (const key of keys) {
    const candidate = asRecord(source[key]);
    if (Object.keys(candidate).length > 0) return candidate;
  }
  return {};
}

function listFrom(value: unknown, keys: string[]): unknown[] {
  if (Array.isArray(value)) return value;

  const record = asRecord(value);
  for (const key of keys) {
    const candidate = record[key];
    if (Array.isArray(candidate)) return candidate;
  }

  return [];
}

function daysBetween(start?: string | null, end?: string | null): number | undefined {
  if (!start || !end) return undefined;

  const startDate = new Date(start);
  const endDate = new Date(end);
  if (Number.isNaN(startDate.getTime()) || Number.isNaN(endDate.getTime())) {
    return undefined;
  }

  return Math.max(
    0,
    Math.round((endDate.getTime() - startDate.getTime()) / 86_400_000),
  );
}

function mapTransaction(transaction: BackendTransaction): TransactionDto {
  return {
    transactionId: String(transaction.transactionId),
    amount: asNumber(transaction.transactionAmount),
    currency: transaction.transactionCurrency ?? 'EUR',
    merchant: transaction.merchantName ?? 'Unknown merchant',
    merchantCountry: transaction.merchantCountryCode ?? transaction.merchantCountryName,
    merchantId: transaction.merchantId ? String(transaction.merchantId) : undefined,
    mcc: transaction.mccCode,
    cardNetwork:
      transaction.cardNetworkName?.toUpperCase().includes('MASTER') || transaction.cardNetworkId === 2
        ? 'MASTERCARD'
        : 'VISA',
    cardType: 'CREDIT',
    channel:
      transaction.transactionChannel === 'POS' || transaction.transactionChannel === 'ATM'
        ? transaction.transactionChannel
        : 'ECOMMERCE',
    threeDS: transaction.is3dsAuthenticated === 'Y',
    eci: transaction.eciValue ?? undefined,
    issuerCountry: transaction.issuerCountryCode ?? transaction.issuerCountryName,
    acquirerCountry: transaction.acquirerCountryCode ?? transaction.acquirerCountryName,
    region: transaction.regionCode,
    authorizationDate: transaction.authorizationDatetime ?? undefined,
    clearingDate: transaction.clearingDatetime ?? undefined,
    clearingDelayDays: daysBetween(
      transaction.authorizationDatetime,
      transaction.clearingDatetime,
    ),
    status:
      transaction.transactionStatus === 'DECLINED' || transaction.transactionStatus === 'PENDING'
        ? transaction.transactionStatus
        : 'APPROVED',
  };
}

function mapRecommendation(value: unknown, index: number): RecommendationDto {
  const recommendation = asRecord(value);
  const score = firstNumber(recommendation, ['score', 'mlScore', 'priorityScore', 'confidence'], 0.5);
  const priority = asString(recommendation.priority, score >= 0.8 ? 'HIGH' : score >= 0.5 ? 'MEDIUM' : 'LOW');
  const difficulty = asString(recommendation.difficulty, 'MEDIUM');

  return {
    id: firstString(recommendation, ['id', 'recommendationId'], `REC-${index + 1}`),
    recommendationType: firstString(recommendation, ['recommendationType', 'type', 'code'], 'OPTIMIZE_TRANSACTION'),
    action: firstString(recommendation, ['action', 'title', 'message', 'recommendation'], 'Review transaction optimization opportunity'),
    currentValue: firstString(recommendation, ['currentValue', 'from'], 'Current setup'),
    recommendedValue: firstString(recommendation, ['recommendedValue', 'targetValue', 'to'], 'Optimized setup'),
    expectedImpact: firstString(recommendation, ['expectedImpact', 'impact'], 'Potential fee reduction'),
    score,
    priority: priority === 'HIGH' || priority === 'LOW' ? priority : 'MEDIUM',
    rankingReason: firstString(recommendation, ['rankingReason', 'reason', 'explanation'], 'Recommended by optimization service.'),
    difficulty: difficulty === 'EASY' || difficulty === 'HARD' ? difficulty : 'MEDIUM',
    fallbackUsed: Boolean(recommendation.fallbackUsed),
  };
}

function mapMissedConditionDto(value: unknown, index: number): MissedConditionDto {
  const condition = asRecord(value);
  const impact = firstValue(condition, ['impact', 'expectedImpact']);

  return {
    id: firstString(condition, ['id', 'conditionId'], `COND-${index + 1}`),
    condition: firstString(
      condition,
      ['condition', 'conditionName', 'type'],
      'Optimization condition',
    ),
    currentValue: displayValue(
      firstValue(condition, ['currentValue', 'actualValue']),
    ),
    optimalValue: displayValue(
      firstValue(condition, ['optimalValue', 'recommendedValue', 'expectedValue']),
    ),
    impact: displayImpact(impact),
    confidence: firstNumber(condition, ['confidence', 'score'], 0.75),
    explanation: firstString(
      condition,
      ['explanation', 'reason'],
      'This condition was not met for the selected transaction.',
    ),
  };
}

function mapAnomaly(value: unknown, index: number): AnomalyDto {
  const anomaly = asRecord(value);
  const severity = asString(anomaly.severity, 'MEDIUM');

  return {
    id: firstString(anomaly, ['id', 'anomalyId'], `AN-${index + 1}`),
    transactionId: String(firstNumber(anomaly, ['transactionId'], index + 1)),
    anomalyType: firstString(anomaly, ['anomalyType', 'type'], 'ANOMALY'),
    severity: severity === 'LOW' || severity === 'HIGH' ? severity : 'MEDIUM',
    explanation: firstString(anomaly, ['explanation', 'reason', 'message'], 'Anomaly detected by optimization service.'),
  };
}


function mapClassification(response: BackendClassificationResponse): TransactionClassification {
  const result = response.result ?? {};
  const feeCalculation = response.feeCalculation ?? {};
  const factTransaction = response.factTransaction ?? {};

  const feeRate = asNumber(result.feeRate ?? feeCalculation.feeRate ?? factTransaction.feeRate);
  const feeRatePercent = asNumber(result.feeRatePercent, feeRate * 100);

  return {
    transactionId: String(result.transactionId ?? factTransaction.transactionId ?? DEFAULT_TRANSACTION_ID),
    category: asString(result.category, 'N/A'),
    categoryCode: asString(result.categoryCode ?? factTransaction.categoryCode, 'N/A'),
    rulePriority:
      result.rulePriority ?? factTransaction.rulePriority ?? null,
    feeRate,
    feeRatePercent,
    feeAmount: asNumber(feeCalculation.finalFee ?? feeCalculation.rawFee),
    currency: asString(feeCalculation.currency ?? factTransaction.currency, 'EUR'),
    confidence: asNumber(result.confidence ?? factTransaction.confidence),
    matchedConditions: Array.isArray(result.matchedConditions) ? result.matchedConditions : [],
    missingFields: Array.isArray(result.missingFields) ? result.missingFields : [],
    reasonCodes: Array.isArray(result.reasonCodes) ? result.reasonCodes : [],
    conditionResults: Array.isArray(result.conditionResults)
      ? result.conditionResults.map((condition) => ({
          field: asString(condition.field, 'N/A'),
          expected: asString(condition.expected, 'N/A'),
          actual: asString(condition.actual, 'N/A'),
          outcome: asString(condition.outcome, 'N/A'),
          reasonCode: condition.reasonCode ?? null,
          message: asString(condition.message, ''),
        }))
      : [],
    explanation: asString(result.explanation, 'No explanation available.'),
    calculationMethod: asString(feeCalculation.calculationMethod, 'N/A'),
    classifiedAt: result.classifiedAt ?? factTransaction.classifiedAt,
  };
}

function mapReport(report: BackendOptimizationReport): OptimizationReportDto {
  const feeComparison = asRecord(report.feeComparison);
  const savingsProjections = asRecord(report.savingsProjections);

  const current = nestedRecord(feeComparison, ['currentClassification', 'current', 'currentFee']);
  const optimized = nestedRecord(feeComparison, ['optimizedClassification', 'optimized', 'optimalFee']);

  const currentFeeRate = firstNumber(current, ['feeRate', 'rate'], firstNumber(feeComparison, ['currentFeeRate'], 0));
  const optimizedFeeRate = firstNumber(optimized, ['feeRate', 'rate'], firstNumber(feeComparison, ['optimizedFeeRate', 'optimalFeeRate'], 0));
  const currentFeeAmount = firstNumber(current, ['feeAmount', 'amount'], firstNumber(feeComparison, ['currentFee', 'currentFeeAmount'], 0));
  const optimizedFeeAmount = firstNumber(optimized, ['feeAmount', 'amount'], firstNumber(feeComparison, ['optimizedFee', 'optimalFee', 'optimizedFeeAmount'], 0));
  const savingsAmount = firstNumber(feeComparison, ['absoluteSavings', 'savingsAmount'], Math.max(0, currentFeeAmount - optimizedFeeAmount));
  const percentageSavings = firstNumber(feeComparison, ['percentageSavings', 'savingsPercentage'], currentFeeAmount ? (savingsAmount / currentFeeAmount) * 100 : 0);

  const missedConditions = listFrom(report.missedConditions, [
  'missedConditions',
  'conditions',
]).map(mapMissedConditionDto);
  const recommendations = listFrom(report.rankedRecommendations, ['recommendations', 'rankedRecommendations']).map(mapRecommendation);

  return {
    transactionId: String(report.transactionId),
    currentClassification: {
      category: firstString(current, ['category', 'classification'], firstString(feeComparison, ['currentCategory'], 'Current classification')),
      feeRate: currentFeeRate,
      feeAmount: currentFeeAmount,
      appliedRule: firstString(current, ['appliedRule', 'ruleCode'], firstString(feeComparison, ['currentAppliedRule'], 'N/A')),
      explanation: firstString(current, ['explanation'], report.summary ?? 'Current transaction classification.'),
    },
    optimizedClassification: {
      category: firstString(optimized, ['category', 'classification'], firstString(feeComparison, ['optimizedCategory', 'optimalCategory'], 'Optimized classification')),
      feeRate: optimizedFeeRate,
      feeAmount: optimizedFeeAmount,
      appliedRule: firstString(optimized, ['appliedRule', 'ruleCode'], firstString(feeComparison, ['optimizedAppliedRule', 'optimalAppliedRule'], 'N/A')),
      explanation: firstString(optimized, ['explanation'], 'Optimized classification after recommended changes.'),
    },
    savings: {
      amount: savingsAmount,
      percentage: percentageSavings,
      monthlyProjectedSavings: firstNumber(savingsProjections, ['monthlyProjectedSavings'], firstNumber(feeComparison, ['monthlyProjectedSavings'], savingsAmount * 1000)),
      yearlyProjectedSavings: firstNumber(savingsProjections, ['yearlyProjectedSavings'], firstNumber(feeComparison, ['yearlyProjectedSavings'], savingsAmount * 12000)),
      perTransactionSaving: firstNumber(savingsProjections, ['mlPredictedSavings'], savingsAmount),
    },
    ml: {
      confidence: firstNumber(savingsProjections, ['mlConfidence'], firstNumber(feeComparison, ['mlConfidence', 'confidence'], 0.75)),
      modelVersion: asString(feeComparison.modelVersion, 'backend-ml-service'),
      fallbackUsed: Boolean(feeComparison.fallbackUsed),
    },
      missedConditions,
    recommendations,
  };
}

export const mlService = {
  async getTransactions(page = 1, pageSize = 10): Promise<TransactionPageDto> {
  const response = await apiClient<BackendTransactionPage | BackendTransaction[]>(
    `/transactions?page=${page}&pageSize=${pageSize}`,
  );

  const rows = Array.isArray(response)
    ? response
    : response.rows ??
      response.content ??
      response.data ??
      response.items ??
      response.transactions ??
      [];

  return {
    rows: rows.map(mapTransaction),
    total: Array.isArray(response) ? rows.length : response.total ?? rows.length,
    page: Array.isArray(response) ? page : response.page ?? page,
    pageSize: Array.isArray(response) ? pageSize : response.pageSize ?? pageSize,
    totalPages: Array.isArray(response)
      ? Math.max(1, Math.ceil(rows.length / pageSize))
      : response.totalPages ?? Math.max(1, Math.ceil((response.total ?? rows.length) / pageSize)),
  };
},

  async getTransactionById(transactionId: string | null): Promise<TransactionDto | undefined> {
    const transaction = await apiClient<BackendTransaction>(`/transactions/${backendId(transactionId)}`);
    return mapTransaction(transaction);
  },

  async getOptimizationReport(transactionId: string | null): Promise<OptimizationReportDto> {
    const report = await apiClient<BackendOptimizationReport>(
      `/ml/transactions/${backendId(transactionId)}/optimization-report`,
    );

    return mapReport(report);
  },

  async getMissedConditions(
  transactionId: string | null,
): Promise<MissedConditionDto[]> {
  if (!transactionId) {
    return [];
  }

    const root = await apiClient<BackendMissedConditionsResponse | unknown[]>(
      `/ml/transactions/${backendId(transactionId)}/missed-conditions`,
    );

  return listFrom(root, ['missedConditions', 'conditions']).map(
    mapMissedConditionDto,
  );
},

  async getClassification(transactionId: string | null): Promise<TransactionClassification> {
    const response = await apiClient<BackendClassificationResponse>(
      `/transactions/${backendId(transactionId)}/classify`,
      {
        method: 'POST',
      },
    );

    return mapClassification(response);
  },

  async getRecommendations(transactionId: string | null): Promise<RecommendationDto[]> {
    const root = await apiClient<unknown>(`/ml/transactions/${backendId(transactionId)}/recommendations`);
    return listFrom(root, ['recommendations', 'rankedRecommendations'])
      .map(mapRecommendation)
      .sort((a, b) => b.score - a.score);
  },

  async getAnomalies(): Promise<AnomalyDto[]> {
    const root = await apiClient<unknown>('/ml/transactions/portfolio/anomalies');
    return listFrom(root, ['anomalies', 'anomalyInsights']).map(mapAnomaly);
  },

  async getPortfolioSummary() {
    const transactions = await this.getTransactions(1, 1);
    const anomalies = await this.getAnomalies();

    return {
      totalTransactions: transactions.total,
      totalCurrentFees: 0,
      totalOptimizedFees: 0,
      totalEstimatedSavings: 0,
      averageFeeRate: 0,
      anomalyCount: anomalies.length,
      topRecommendationTypes: [],
    };
  },
};