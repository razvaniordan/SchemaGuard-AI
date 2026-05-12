import { useEffect, useMemo, useState } from 'react';
import { mockMlService } from '../mocks/mockMlService.ts';
import type {
  MockTransaction,
  TransactionChannel,
  TransactionStatus,
} from '../mocks/mockTransactions.ts';

type Props = {
  onSelectTransaction: (transactionId: string) => void;
};

export function TransactionsPage({ onSelectTransaction }: Props) {
  const [transactions, setTransactions] = useState<MockTransaction[]>([]);
  const [search, setSearch] = useState('');
  const [channelFilter, setChannelFilter] = useState<'ALL' | TransactionChannel>('ALL');
  const [threeDsFilter, setThreeDsFilter] = useState<'ALL' | 'YES' | 'NO'>('ALL');
  const [statusFilter, setStatusFilter] = useState<'ALL' | TransactionStatus>('ALL');

  useEffect(() => {
    mockMlService.getTransactions().then(setTransactions);
  }, []);

  const filteredTransactions = useMemo(() => {
    return transactions.filter((transaction) => {
      const searchValue = search.toLowerCase();

      const matchesSearch =
        transaction.transactionId.toLowerCase().includes(searchValue) ||
        transaction.merchant.toLowerCase().includes(searchValue) ||
        transaction.currency.toLowerCase().includes(searchValue);

      const matchesChannel =
        channelFilter === 'ALL' || transaction.channel === channelFilter;

      const matchesThreeDs =
        threeDsFilter === 'ALL' ||
        (threeDsFilter === 'YES' && transaction.threeDS) ||
        (threeDsFilter === 'NO' && !transaction.threeDS);

      const matchesStatus =
        statusFilter === 'ALL' || transaction.status === statusFilter;

      return matchesSearch && matchesChannel && matchesThreeDs && matchesStatus;
    });
  }, [transactions, search, channelFilter, threeDsFilter, statusFilter]);

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
            Listă mock de tranzacții cu search și filtre basic.
          </p>
        </div>

        <div className="rounded-xl bg-blue-50 px-4 py-3 text-sm font-semibold text-brand-primary">
          {filteredTransactions.length} rezultate
        </div>
      </div>

      <div className="mt-6 grid gap-3 md:grid-cols-4">
        <input
          value={search}
          onChange={(event) => setSearch(event.target.value)}
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
          <option value="ATM">ATM</option>
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
          <option value="PENDING">Pending</option>
          <option value="DECLINED">Declined</option>
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
              <tr>
                <td colSpan={10} className="px-4 py-10 text-center text-brand-muted">
                  Nu există tranzacții pentru filtrele selectate.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}