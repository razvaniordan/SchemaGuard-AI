import type {
  FeeCalculationResult,
  TransactionDraft,
} from '../../features/transactions/types';
import { apiClient } from './client';

export async function calculateTransactionFee(
  transaction: TransactionDraft,
): Promise<FeeCalculationResult> {
  return apiClient<FeeCalculationResult>('/transactions/calculate', {
    method: 'POST',
    body: JSON.stringify({
      ...transaction,
      amount: Number(transaction.amount),
    }),
  });
}