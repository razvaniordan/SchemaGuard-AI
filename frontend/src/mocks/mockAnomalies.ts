export type AnomalySeverity = 'LOW' | 'MEDIUM' | 'HIGH';

export type MockAnomaly = {
  id: string;
  transactionId: string;
  anomalyType: string;
  severity: AnomalySeverity;
  explanation: string;
};

export const mockAnomalies: MockAnomaly[] = [
  {
    id: 'AN-001',
    transactionId: 'TX-1004',
    anomalyType: 'HIGH_CLEARING_DELAY',
    severity: 'HIGH',
    explanation:
      'Transaction has a clearing delay of 3 days, which may prevent optimal fee qualification.',
  },
  {
    id: 'AN-002',
    transactionId: 'TX-1001',
    anomalyType: 'MISSING_3DS',
    severity: 'MEDIUM',
    explanation:
      'Ecommerce transaction does not use 3DS authentication.',
  },
];