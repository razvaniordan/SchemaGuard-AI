import { useEffect, useMemo, useState, type ReactNode } from 'react';
import { dashboardService } from '../services/api/dashboard';
import type {
  CategoryTransitionDto,
  DashboardOverviewDto,
  MerchantOptimizationDto,
  MonthlySavingsDto,
} from '../services/api/types';

export function DashboardPage() {
  const [dashboard, setDashboard] = useState<DashboardOverviewDto | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    setIsLoading(true);
    dashboardService
      .getOverview()
      .then((data) => {
        if (!isMounted) return;
        setDashboard(data);
        setError(null);
      })
      .catch((err: unknown) => {
        if (!isMounted) return;
        setError(err instanceof Error ? err.message : 'Failed to load dashboard');
      })
      .finally(() => {
        if (isMounted) setIsLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const maxMonthlySaving = useMemo(() => {
    if (!dashboard?.monthlySavings.length) return 0;
    return Math.max(...dashboard.monthlySavings.map((item) => item.totalSavingAmount));
  }, [dashboard]);

  if (isLoading) {
    return <Shell title="Dashboard" subtitle="Loading STAR schema metrics..." />;
  }

  if (error) {
    return (
      <Shell title="Dashboard" subtitle="Unable to load analytics data.">
        <div className="rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">
          {error}
        </div>
      </Shell>
    );
  }

  if (!dashboard) {
    return <Shell title="Dashboard" subtitle="No dashboard data returned." />;
  }

  return (
    <Shell
      title="Transaction Fee Monitoring Dashboard"
      subtitle="Live reporting from analytics.fact_transaction_analysis and related STAR dimensions."
    >
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        <MetricCard label="Transactions" value={formatInteger(dashboard.kpis.transactionCount)} />
        <MetricCard label="Transaction Volume" value={formatMoney(dashboard.kpis.totalTransactionAmount)} />
        <MetricCard label="Current Fees" value={formatMoney(dashboard.kpis.totalCurrentFeeAmount)} />
        <MetricCard label="Optimal Fees" value={formatMoney(dashboard.kpis.totalOptimalFeeAmount)} />
        <MetricCard
          label="Total Savings"
          value={formatMoney(dashboard.kpis.totalSavingAmount)}
          helper={`${formatPercent(dashboard.kpis.avgSavingPercentage)} avg saving`}
          highlight
        />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.25fr_0.75fr]">
        <div className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2 className="text-lg font-semibold text-brand-text">Monthly fee savings</h2>
              <p className="mt-1 text-sm text-brand-muted">Grouped by authorization date through analytics.dim_date.</p>
            </div>
          </div>

          {dashboard.monthlySavings.length === 0 ? (
            <EmptyState message="No monthly savings data is available yet." />
          ) : (
            <div className="mt-6 grid gap-3">
              {dashboard.monthlySavings.map((month) => (
                <MonthlyBar key={`${month.yearNumber}-${month.monthNumber}`} month={month} max={maxMonthlySaving} />
              ))}
            </div>
          )}
        </div>

        <div className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-brand-text">Category transitions</h2>
          <p className="mt-1 text-sm text-brand-muted">Where transactions are now versus their optimal category.</p>

          {dashboard.categoryTransitions.length === 0 ? (
            <EmptyState message="No category transitions are available yet." />
          ) : (
            <div className="mt-5 grid gap-4">
              {dashboard.categoryTransitions.map((transition) => (
                <TransitionCard key={`${transition.currentCategoryKey}-${transition.optimalCategoryKey}`} transition={transition} />
              ))}
            </div>
          )}
        </div>
      </section>

      <section className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-brand-text">Top merchant optimization opportunities</h2>
        <p className="mt-1 text-sm text-brand-muted">Ranked by total saving amount using the historical merchant dimension version.</p>

        {dashboard.topMerchants.length === 0 ? (
          <EmptyState message="No merchant optimization data is available yet." />
        ) : (
          <div className="mt-5 overflow-x-auto">
            <table className="min-w-full divide-y divide-brand-border text-sm">
              <thead>
                <tr className="text-left text-xs uppercase tracking-wide text-brand-muted">
                  <th className="py-3 pr-4 font-semibold">Merchant</th>
                  <th className="px-4 py-3 font-semibold">MCC</th>
                  <th className="px-4 py-3 text-right font-semibold">Transactions</th>
                  <th className="px-4 py-3 text-right font-semibold">Current fee</th>
                  <th className="px-4 py-3 text-right font-semibold">Optimal fee</th>
                  <th className="py-3 pl-4 text-right font-semibold">Saving</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-brand-border">
                {dashboard.topMerchants.map((merchant) => (
                  <MerchantRow key={merchant.merchantKey} merchant={merchant} />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </Shell>
  );
}

function Shell({ title, subtitle, children }: { title: string; subtitle: string; children?: ReactNode }) {
  return (
    <div className="grid gap-6">
      <section className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
        <p className="text-sm font-medium uppercase tracking-wide text-brand-primary">SchemeGuard AI</p>
        <h1 className="mt-2 text-2xl font-semibold text-brand-text sm:text-3xl">{title}</h1>
        <p className="mt-3 max-w-3xl text-sm leading-6 text-brand-muted sm:text-base">{subtitle}</p>
      </section>
      {children}
    </div>
  );
}

function MetricCard({ label, value, helper, highlight = false }: { label: string; value: string; helper?: string; highlight?: boolean }) {
  return (
    <div className={`rounded-2xl border p-5 shadow-sm ${highlight ? 'border-blue-100 bg-blue-50' : 'border-brand-border bg-white'}`}>
      <p className="text-xs font-semibold uppercase tracking-wide text-brand-muted">{label}</p>
      <p className="mt-3 text-2xl font-bold text-brand-text">{value}</p>
      {helper ? <p className="mt-2 text-sm text-brand-muted">{helper}</p> : null}
    </div>
  );
}

function MonthlyBar({ month, max }: { month: MonthlySavingsDto; max: number }) {
  const width = max > 0 ? Math.max(6, (month.totalSavingAmount / max) * 100) : 0;

  return (
    <div className="grid gap-2 sm:grid-cols-[120px_1fr_140px] sm:items-center">
      <div>
        <p className="text-sm font-semibold text-brand-text">{month.monthName} {month.yearNumber}</p>
        <p className="text-xs text-brand-muted">{formatInteger(month.transactionCount)} txns</p>
      </div>
      <div className="h-3 overflow-hidden rounded-full bg-slate-100">
        <div className="h-full rounded-full bg-blue-600" style={{ width: `${width}%` }} />
      </div>
      <p className="text-sm font-semibold text-brand-text sm:text-right">{formatMoney(month.totalSavingAmount)}</p>
    </div>
  );
}

function TransitionCard({ transition }: { transition: CategoryTransitionDto }) {
  return (
    <div className="rounded-xl border border-brand-border p-4">
      <p className="text-sm font-semibold text-brand-text">{transition.currentCategoryName}</p>
      <p className="mt-1 text-xs uppercase tracking-wide text-brand-muted">to</p>
      <p className="mt-1 text-sm font-semibold text-brand-primary">{transition.optimalCategoryName}</p>
      <div className="mt-4 flex items-center justify-between gap-3 text-sm">
        <span className="text-brand-muted">{formatInteger(transition.transactionCount)} txns</span>
        <span className="font-semibold text-brand-text">{formatMoney(transition.totalSavingAmount)}</span>
      </div>
    </div>
  );
}

function MerchantRow({ merchant }: { merchant: MerchantOptimizationDto }) {
  return (
    <tr className="align-top">
      <td className="py-4 pr-4">
        <p className="font-semibold text-brand-text">{merchant.merchantName}</p>
        <p className="mt-1 text-xs text-brand-muted">Source ID {merchant.sourceMerchantId}</p>
      </td>
      <td className="px-4 py-4 text-brand-muted">
        <span className="font-semibold text-brand-text">{merchant.mccCode}</span>
        {merchant.mccDescription ? <span className="block text-xs">{merchant.mccDescription}</span> : null}
      </td>
      <td className="px-4 py-4 text-right text-brand-text">{formatInteger(merchant.transactionCount)}</td>
      <td className="px-4 py-4 text-right text-brand-text">{formatMoney(merchant.totalCurrentFeeAmount)}</td>
      <td className="px-4 py-4 text-right text-brand-text">{formatMoney(merchant.totalOptimalFeeAmount)}</td>
      <td className="py-4 pl-4 text-right font-semibold text-brand-primary">{formatMoney(merchant.totalSavingAmount)}</td>
    </tr>
  );
}

function EmptyState({ message }: { message: string }) {
  return <div className="mt-5 rounded-xl border border-dashed border-brand-border bg-slate-50 p-5 text-sm text-brand-muted">{message}</div>;
}

function formatMoney(value: number, currency = 'EUR') {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency, maximumFractionDigits: 2 }).format(Number(value || 0));
}

function formatInteger(value: number) {
  return new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(Number(value || 0));
}

function formatPercent(value: number) {
  return `${Number(value || 0).toFixed(2)}%`;
}
