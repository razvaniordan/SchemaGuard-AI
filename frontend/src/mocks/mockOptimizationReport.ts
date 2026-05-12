import type { MockRecommendation } from './mockRecommendations.ts';

export type MissedCondition = {
  id: string;
  condition: string;
  currentValue: string;
  optimalValue: string;
  impact: string;
  confidence: number;
  explanation: string;
};

export type MockOptimizationReport = {
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
  missedConditions: MissedCondition[];
  recommendations: MockRecommendation[];
};

export const mockOptimizationReport: MockOptimizationReport = {
  transactionId: 'TX-1001',
  currentClassification: {
    category: 'Standard Ecommerce',
    feeRate: 0.0185,
    feeAmount: 2.3,
    appliedRule: 'RULE_ECOM_NO_3DS_DELAYED_CLEARING',
    explanation:
      'Transaction is ecommerce, not authenticated with 3DS, and clearing delay is above optimal threshold.',
  },
  optimizedClassification: {
    category: 'Secure Optimized Ecommerce',
    feeRate: 0.0125,
    feeAmount: 1.56,
    appliedRule: 'RULE_ECOM_3DS_FAST_CLEARING',
    explanation:
      'Transaction qualifies for a better fee category when 3DS is enabled and clearing happens faster.',
  },
  savings: {
    amount: 0.74,
    percentage: 32.17,
    monthlyProjectedSavings: 1480,
    yearlyProjectedSavings: 17760,
    perTransactionSaving: 0.74,
  },
  ml: {
    confidence: 0.91,
    modelVersion: 'mock-ranking-model-v1',
    fallbackUsed: false,
  },
  missedConditions: [
    {
      id: 'COND-001',
      condition: '3DS authentication',
      currentValue: 'Disabled',
      optimalValue: 'Enabled',
      impact: 'Could qualify transaction for secure ecommerce pricing.',
      confidence: 0.93,
      explanation:
        'The transaction is ecommerce but does not use 3DS authentication.',
    },
    {
      id: 'COND-002',
      condition: 'Clearing time',
      currentValue: '2 days',
      optimalValue: '0 days',
      impact: 'Faster clearing can improve fee qualification.',
      confidence: 0.87,
      explanation:
        'The clearing delay is higher than the optimal value for this fee rule.',
    },
    {
      id: 'COND-003',
      condition: 'ECI',
      currentValue: '07',
      optimalValue: '05',
      impact: 'Authenticated ECI may improve classification.',
      confidence: 0.81,
      explanation:
        'Current ECI does not indicate successful 3DS authentication.',
    },
  ],
  recommendations: [],
};