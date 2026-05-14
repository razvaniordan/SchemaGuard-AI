export type TransactionStatus = 'APPROVED' | 'DECLINED' | 'PENDING';
export type TransactionChannel = 'ECOMMERCE' | 'POS' | 'ATM';

export type TransactionDto = {
  transactionId: string;
  amount: number;
  currency: string;
  merchant: string;
  merchantCountry?: string;
  merchantId?: string;
  mcc?: string;
  cardNetwork: 'VISA' | 'MASTERCARD';
  cardType: 'CREDIT' | 'DEBIT';
  channel: TransactionChannel;
  threeDS: boolean;
  eci?: string;
  issuerCountry?: string;
  acquirerCountry?: string;
  region?: string;
  authorizationDate?: string;
  clearingDate?: string;
  clearingDelayDays?: number;
  status: TransactionStatus;
};

export type RecommendationPriority = 'HIGH' | 'MEDIUM' | 'LOW';
export type RecommendationDifficulty = 'EASY' | 'MEDIUM' | 'HARD';

export type RecommendationDto = {
  id: string;
  recommendationType: string;
  action: string;
  currentValue: string;
  recommendedValue: string;
  expectedImpact: string;
  score: number;
  priority: RecommendationPriority;
  rankingReason: string;
  difficulty: RecommendationDifficulty;
  fallbackUsed: boolean;
};

export type MissedConditionDto = {
  id: string;
  condition: string;
  currentValue: string;
  optimalValue: string;
  impact: string;
  confidence: number;
  explanation: string;
};

export type OptimizationReportDto = {
  transactionId: string;
  currentClassification: {
    category: string;
    feeRate: number;
    feeAmount: number;
    appliedRule: string;
    explanation: string;
  };
  optimizedClassification: {
    category: string;
    feeRate: number;
    feeAmount: number;
    appliedRule: string;
    explanation: string;
  };
  savings: {
    amount: number;
    percentage: number;
    monthlyProjectedSavings: number;
    yearlyProjectedSavings: number;
    perTransactionSaving: number;
  };
  ml: {
    confidence: number;
    modelVersion: string | null;
    fallbackUsed: boolean;
  };
  missedConditions: MissedConditionDto[];
  recommendations: RecommendationDto[];
};

export type AnomalySeverity = 'LOW' | 'MEDIUM' | 'HIGH';

export type AnomalyDto = {
  id: string;
  transactionId: string;
  anomalyType: string;
  severity: AnomalySeverity;
  explanation: string;
};