export type TransactionStatus = 'APPROVED' | 'DECLINED' | 'SETTLED';
export type TransactionChannel = 'ECOMMERCE' | 'POS' | 'MOTO' | 'CONTACTLESS';

export type MockTransaction = {
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

export const mockTransactions: MockTransaction[] = [
  {
    transactionId: 'TX-1001',
    amount: 124.5,
    currency: 'EUR',
    merchant: 'Fashion Store',
    merchantCountry: 'RO',
    merchantId: 'M-001',
    mcc: '5651',
    cardNetwork: 'VISA',
    cardType: 'CREDIT',
    channel: 'ECOMMERCE',
    threeDS: false,
    eci: '07',
    issuerCountry: 'RO',
    acquirerCountry: 'RO',
    region: 'Domestic',
    authorizationDate: '2026-05-01',
    clearingDate: '2026-05-03',
    clearingDelayDays: 2,
    status: 'APPROVED',
  },
  {
    transactionId: 'TX-1002',
    amount: 89.99,
    currency: 'EUR',
    merchant: 'Electronics Hub',
    merchantCountry: 'DE',
    merchantId: 'M-002',
    mcc: '5732',
    cardNetwork: 'MASTERCARD',
    cardType: 'DEBIT',
    channel: 'ECOMMERCE',
    threeDS: true,
    eci: '05',
    issuerCountry: 'RO',
    acquirerCountry: 'DE',
    region: 'Intra-European',
    authorizationDate: '2026-05-02',
    clearingDate: '2026-05-02',
    clearingDelayDays: 0,
    status: 'APPROVED',
  },
  {
    transactionId: 'TX-1003',
    amount: 45.2,
    currency: 'RON',
    merchant: 'Local Grocery',
    merchantCountry: 'RO',
    merchantId: 'M-003',
    mcc: '5411',
    cardNetwork: 'VISA',
    cardType: 'DEBIT',
    channel: 'POS',
    threeDS: false,
    issuerCountry: 'RO',
    acquirerCountry: 'RO',
    region: 'Domestic',
    authorizationDate: '2026-05-03',
    clearingDate: '2026-05-04',
    clearingDelayDays: 1,
    status: 'APPROVED',
  },
  {
    transactionId: 'TX-1004',
    amount: 250,
    currency: 'EUR',
    merchant: 'Travel Booking',
    merchantCountry: 'FR',
    merchantId: 'M-004',
    mcc: '4722',
    cardNetwork: 'MASTERCARD',
    cardType: 'CREDIT',
    channel: 'ECOMMERCE',
    threeDS: false,
    eci: '07',
    issuerCountry: 'RO',
    acquirerCountry: 'FR',
    region: 'Intra-European',
    authorizationDate: '2026-05-04',
    clearingDate: '2026-05-07',
    clearingDelayDays: 3,
    status: 'SETTLED',
  },
  {
    transactionId: 'TX-1005',
    amount: 30,
    currency: 'EUR',
    merchant: 'ATM Withdrawal',
    merchantCountry: 'RO',
    merchantId: 'M-005',
    mcc: '6011',
    cardNetwork: 'VISA',
    cardType: 'DEBIT',
    channel: 'CONTACTLESS',
    threeDS: false,
    issuerCountry: 'RO',
    acquirerCountry: 'RO',
    region: 'Domestic',
    authorizationDate: '2026-05-05',
    clearingDate: undefined,
    clearingDelayDays: undefined,
    status: 'DECLINED',
  },
];