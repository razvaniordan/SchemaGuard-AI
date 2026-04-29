import { create } from 'zustand';
import type {
  FeeCalculationResult,
  TransactionDraft,
} from '../features/transactions/types';
import { calculateTransactionFee } from '../services/api/transactions';

type RequestStatus = 'idle' | 'loading' | 'success' | 'error';

type TransactionStore = {
  draft: TransactionDraft;
  result: FeeCalculationResult | null;
  status: RequestStatus;
  error: string | null;

  updateDraft: <TKey extends keyof TransactionDraft>(
    field: TKey,
    value: TransactionDraft[TKey],
  ) => void;
  resetDraft: () => void;
  clearResult: () => void;
  calculateFee: () => Promise<void>;
};

const initialDraft: TransactionDraft = {
  amount: '',
  currency: 'USD',
  merchantName: '',
  mcc: '',
  cardNetwork: 'visa',
  channel: 'online',
};

export const useTransactionStore = create<TransactionStore>((set, get) => ({
  draft: initialDraft,
  result: null,
  status: 'idle',
  error: null,

  updateDraft: (field, value) => {
    set((state) => ({
      draft: {
        ...state.draft,
        [field]: value,
      },
    }));
  },

  resetDraft: () => {
    set({
      draft: initialDraft,
      result: null,
      status: 'idle',
      error: null,
    });
  },

  clearResult: () => {
    set({
      result: null,
      status: 'idle',
      error: null,
    });
  },

  calculateFee: async () => {
    set({
      status: 'loading',
      error: null,
    });

    try {
      const result = await calculateTransactionFee(get().draft);

      set({
        result,
        status: 'success',
      });
    } catch (error) {
      set({
        status: 'error',
        error: error instanceof Error ? error.message : 'Unexpected error occurred.',
      });
    }
  },
}));