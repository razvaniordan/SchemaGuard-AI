export type CardNetwork = 'visa' | 'mastercard';

export type TransactionChannel = 'online' | 'in_person' | 'contactless' | 'mobile';

export type TransactionDraft = {
  amount: string;
  currency: string;
  merchantName: string;
  mcc: string;
  cardNetwork: CardNetwork;
  channel: TransactionChannel;
};

export type FeeCalculationResult = {
  interchangeFee: number;
  effectiveRate: number;
  qualificationStatus: 'qualified' | 'downgraded' | 'unknown';
  recommendations: string[];
};