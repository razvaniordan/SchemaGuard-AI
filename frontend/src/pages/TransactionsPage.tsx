import { useEffect, useMemo, useState } from 'react';
import { mlService } from '../services/api/mlService';
import type {
  TransactionChannel,
  TransactionStatus,
  TransactionPageDto,
} from '../services/api/types';

type Props = {
  onSelectTransaction: (transactionId: string) => void;
};

export function TransactionsPage({ onSelectTransaction }: Props) {
  const [transactionPage, setTransactionPage] = useState<TransactionPageDto | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [channelFilter, setChannelFilter] = useState<'ALL' | TransactionChannel>('ALL');
  const [threeDsFilter, setThreeDsFilter] = useState<'ALL' | 'YES' | 'NO'>('ALL');
  const [statusFilter, setStatusFilter] = useState<'ALL' | TransactionStatus>('ALL');

  useEffect(() => {
    let isActive = true;
    setIsLoading(true);

    mlService
      .getTransactions(currentPage, 10, search, channelFilter, threeDsFilter, statusFilter)
      .then((response) => {
        if (isActive) {
          setTransactionPage(response);
          setIsLoading(false);
        }
      })
      .catch((err) => {
        console.error('Failed to load transactions', err);
        if (isActive) setIsLoading(false);
      });

    return () => {
      isActive = false;
    };
  }, [currentPage, search, channelFilter, threeDsFilter, statusFilter]);

  useEffect(() => {
    setCurrentPage(1);
  }, [channelFilter, threeDsFilter, statusFilter]);

  const filteredTransactions = useMemo(() => transactionPage?.rows ?? [], [transactionPage]);

  const totalTransactions = transactionPage?.total ?? 0;
  const totalPages = transactionPage?.totalPages ?? 1;
  const canGoPrevious = currentPage > 1 && !isLoading;
  const canGoNext = currentPage < totalPages && !isLoading;

  return (
    <section className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-sm font-medium uppercase tracking-wide text-brand-primary">
            Transactions
          </p>
          <h1 className="mt-2 text-2xl font-semibold text-brand-text">
            Transactions List
          </h1>
          <p className="mt-2 text-sm text-brand-muted">
            Listă de tranzacții încărcate din backend, cu search și filtre basic.
          </p>
        </div>

        <div className="rounded-xl bg-blue-50 px-4 py-3 text-sm font-semibold text-brand-primary">
          {totalTransactions} total, pagina {currentPage} din {totalPages}
        </div>
      </div>

      <div className="mt-6 grid gap-3 md:grid-cols-4">
        <input
          value={search}
          onChange={(event) => {
            setSearch(event.target.value);
            setCurrentPage(1);
          }}
          placeholder="Search transaction or merchant..."
          className="rounded-xl border border-brand-border px-4 py-3 text-sm outline-none focus:border-brand-primary md:col-span-1"
        />

        <select
          value={channelFilter}
          onChange={(event) =>
            setChannelFilter(event.target.value as 'ALL' | TransactionChannel)
          }
          className="rounded-xl border border-brand-border px-4 py-3 text-sm outline-none focus:border-brand-primary"
        >
          <option value="ALL">All channels</option>
          <option value="ECOMMERCE">Ecommerce</option>
          <option value="POS">POS</option>
          <option value="MOTO">MOTO</option>
          <option value="CONTACTLESS">Contactless</option>
        </select>

        <select
          value={threeDsFilter}
          onChange={(event) =>
            setThreeDsFilter(event.target.value as 'ALL' | 'YES' | 'NO')
          }
          className="rounded-xl border border-brand-border px-4 py-3 text-sm outline-none focus:border-brand-primary"
        >
          <option value="ALL">All 3DS</option>
          <option value="YES">3DS enabled</option>
          <option value="NO">3DS disabled</option>
        </select>

        <select
          value={statusFilter}
          onChange={(event) =>
            setStatusFilter(event.target.value as 'ALL' | TransactionStatus)
          }
          className="rounded-xl border border-brand-border px-4 py-3 text-sm outline-none focus:border-brand-primary"
        >
          <option value="ALL">All statuses</option>
          <option value="APPROVED">Approved</option>
          <option value="DECLINED">Declined</option>
          <option value="SETTLED">Settled</option>
        </select>
      </div>

      <div className="mt-6 overflow-x-auto rounded-xl border border-brand-border">
        <table className="min-w-[1000px] w-full border-collapse text-left text-sm">
          <thead className="bg-slate-50 text-xs uppercase tracking-wide text-brand-muted">
            <tr>
              <th className="px-4 py-3">Transaction ID</th>
              <th className="px-4 py-3">Amount</th>
              <th className="px-4 py-3">Currency</th>
              <th className="px-4 py-3">Merchant</th>
              <th className="px-4 py-3">Card Network</th>
              <th className="px-4 py-3">Card Type</th>
              <th className="px-4 py-3">Channel</th>
              <th className="px-4 py-3">3DS</th>
              <th className="px-4 py-3">Clearing Delay</th>
              <th className="px-4 py-3">Status</th>
            </tr>
          </thead>

          <tbody>
            {isLoading && (
              <tr>
                <td colSpan={10} className="px-4 py-10 text-center text-brand-muted">
                  Loading transactions...
                </td>
              </tr>
            )}

            {filteredTransactions.map((transaction) => (
              <tr
                key={transaction.transactionId}
                onClick={() => onSelectTransaction(transaction.transactionId)}
                className="cursor-pointer border-t border-brand-border transition hover:bg-blue-50"
              >
                <td className="px-4 py-4 font-semibold text-brand-primary">
                  {transaction.transactionId}
                </td>
                <td className="px-4 py-4">{transaction.amount.toFixed(2)}</td>
                <td className="px-4 py-4">{transaction.currency}</td>
                <td className="px-4 py-4">{transaction.merchant}</td>
                <td className="px-4 py-4">{transaction.cardNetwork}</td>
                <td className="px-4 py-4">{transaction.cardType}</td>
                <td className="px-4 py-4">{transaction.channel}</td>
                <td className="px-4 py-4">
                  <span
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${
                      transaction.threeDS
                        ? 'bg-green-50 text-green-700'
                        : 'bg-orange-50 text-orange-700'
                    }`}
                  >
                    {transaction.threeDS ? 'Yes' : 'No'}
                  </span>
                </td>
                <td className="px-4 py-4">
                  {transaction.clearingDelayDays ?? 'N/A'}
                </td>
                <td className="px-4 py-4">
                  <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-brand-text">
                    {transaction.status}
                  </span>
                </td>
              </tr>
            ))}

            {filteredTransactions.length === 0 && (
              !isLoading && (
              <tr>
                <td colSpan={10} className="px-4 py-10 text-center text-brand-muted">
                  Nu există tranzacții pentru filtrele selectate.
                </td>
              </tr>
              )
            )}
          </tbody>
        </table>
      </div>

      <div className="mt-5 flex items-center justify-between gap-3">
        <p className="text-sm text-brand-muted">
                Showing {transactionPage?.rows.length ?? 0} transaction(s) on the current page.
              </p>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setCurrentPage((value) => Math.max(1, value - 1))}
            disabled={!canGoPrevious}
            className="rounded-lg border border-brand-border px-4 py-2 text-sm font-medium text-brand-text transition disabled:cursor-not-allowed disabled:opacity-50"
          >
            Previous
          </button>

          <button
            type="button"
            onClick={() => setCurrentPage((value) => Math.min(totalPages, value + 1))}
            disabled={!canGoNext}
            className="rounded-lg border border-brand-border px-4 py-2 text-sm font-medium text-brand-text transition disabled:cursor-not-allowed disabled:opacity-50"
          >
            Next
          </button>
        </div>
      </div>
    </section>
  );
}