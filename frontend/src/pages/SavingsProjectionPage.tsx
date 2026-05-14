import { useEffect, useState } from 'react';
import { mlService } from '../services/api/mlService';
import type { OptimizationReportDto } from '../services/api/types';

type Props = {
  transactionId: string | null;
};

export function SavingsProjectionPage({ transactionId }: Props) {
  const [report, setReport] = useState<OptimizationReportDto | null>(null);

  useEffect(() => {
    mlService
      .getOptimizationReport(transactionId)
      .then(setReport);
  }, [transactionId]);

  if (!report) {
    return (
      <section className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-semibold text-brand-text">
          Savings Projections
        </h1>
        <p className="mt-3 text-sm text-brand-muted">Loading projections...</p>
      </section>
    );
  }

  return (
    <div className="grid gap-6">
      <section className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
        <p className="text-sm font-medium uppercase tracking-wide text-brand-primary">
          Savings Projection
        </p>

        <h1 className="mt-2 text-2xl font-semibold text-brand-text sm:text-3xl">
          Projected Optimization Value
        </h1>

        <p className="mt-3 max-w-3xl text-sm leading-6 text-brand-muted">
          Shows estimated savings based on the backend optimization report for the selected transaction.
        </p>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <ProjectionCard
          title="Per Transaction Saving"
          value={formatMoney(report.savings.perTransactionSaving, 'EUR')}
          description="Estimated saving for the selected transaction."
        />

        <ProjectionCard
          title="Monthly Projected Savings"
          value={formatMoney(report.savings.monthlyProjectedSavings, 'EUR')}
          description="Estimated saving if similar optimizations are applied monthly."
        />

        <ProjectionCard
          title="Yearly Projected Savings"
          value={formatMoney(report.savings.yearlyProjectedSavings, 'EUR')}
          description="Estimated annualized optimization value."
        />
      </section>

      <section className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-brand-text">
          Projection Explanation
        </h2>

        <p className="mt-3 text-sm leading-6 text-brand-muted">
          The per-transaction value shows the saving for one optimized
          transaction. Monthly and yearly values estimate how much the business
          could save if similar optimization opportunities are applied across a
          larger transaction portfolio.
        </p>

        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          <InfoBox
            label="Current Fee"
            value={formatMoney(report.currentClassification.feeAmount, 'EUR')}
          />

          <InfoBox
            label="Optimized Fee"
            value={formatMoney(report.optimizedClassification.feeAmount, 'EUR')}
          />

          <InfoBox
            label="Savings Percentage"
            value={`${report.savings.percentage.toFixed(2)}%`}
          />

          <InfoBox
            label="ML Confidence"
            value={`${(report.ml.confidence * 100).toFixed(0)}%`}
          />
        </div>
      </section>
    </div>
  );
}

function ProjectionCard({
  title,
  value,
  description,
}: {
  title: string;
  value: string;
  description: string;
}) {
  return (
    <div className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
      <p className="text-sm font-semibold text-brand-muted">{title}</p>

      <p className="mt-4 text-3xl font-bold text-brand-primary">{value}</p>

      <p className="mt-3 text-sm leading-6 text-brand-muted">
        {description}
      </p>
    </div>
  );
}

function InfoBox({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-brand-border bg-slate-50 p-4">
      <p className="text-xs uppercase tracking-wide text-brand-muted">
        {label}
      </p>

      <p className="mt-2 text-sm font-semibold text-brand-text">{value}</p>
    </div>
  );
}

function formatMoney(value: number, currency: string) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(value);
}