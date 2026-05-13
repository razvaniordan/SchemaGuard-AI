import { useEffect, useState } from 'react';
import { mlService } from '../services/api/mlService';
import type { MockOptimizationReport } from '../mocks/mockOptimizationReport.ts';

type Props = {
  transactionId: string | null;
};

export function OptimizationReportPage({ transactionId }: Props) {
  const [report, setReport] = useState<MockOptimizationReport | null>(null);

  useEffect(() => {
    mlService
      .getOptimizationReport(transactionId)
      .then(setReport);
  }, [transactionId]);

  if (!report) {
    return (
      <section className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-semibold text-brand-text">
          Optimization Report
        </h1>
        <p className="mt-3 text-sm text-brand-muted">Loading report...</p>
      </section>
    );
  }

  const currentFee = report.currentClassification.feeAmount;
  const optimizedFee = report.optimizedClassification.feeAmount;
  const savings = report.savings.amount;

  return (
    <div className="grid gap-6">
      <section className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p className="text-sm font-medium uppercase tracking-wide text-brand-primary">
              Optimization Report
            </p>

            <h1 className="mt-2 text-2xl font-semibold text-brand-text sm:text-3xl">
              Fee Optimization Summary
            </h1>

            <p className="mt-3 max-w-3xl text-sm leading-6 text-brand-muted">
              Mock end-to-end report showing current fee, optimized fee,
              projected savings and ML status.
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <Badge
              label={
                report.ml.fallbackUsed ? 'Fallback ranking' : 'ML ranking'
              }
              tone={report.ml.fallbackUsed ? 'warning' : 'success'}
            />

            <Badge
              label={report.ml.modelVersion ?? 'No model version'}
              tone="neutral"
            />
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <MetricCard
          label="Current Fee"
          value={formatMoney(currentFee, 'EUR')}
          helper={report.currentClassification.category}
          tone="neutral"
        />

        <MetricCard
          label="Optimized Fee"
          value={formatMoney(optimizedFee, 'EUR')}
          helper={report.optimizedClassification.category}
          tone="success"
        />

        <MetricCard
          label="Estimated Saving"
          value={formatMoney(savings, 'EUR')}
          helper={`${report.savings.percentage.toFixed(2)}% lower fee`}
          tone="primary"
        />
      </section>

      <section className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
        <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
          <div>
            <h2 className="text-lg font-semibold text-brand-text">
              Current vs Optimized
            </h2>

            <p className="mt-2 text-sm leading-6 text-brand-muted">
              The optimized scenario reduces the transaction fee by applying
              better fee qualification conditions.
            </p>

            <div className="mt-6 grid gap-4 sm:grid-cols-2">
              <FeeBox
                title="Current Classification"
                category={report.currentClassification.category}
                feeRate={report.currentClassification.feeRate}
                feeAmount={report.currentClassification.feeAmount}
                appliedRule={report.currentClassification.appliedRule}
              />

              <FeeBox
                title="Optimized Classification"
                category={report.optimizedClassification.category}
                feeRate={report.optimizedClassification.feeRate}
                feeAmount={report.optimizedClassification.feeAmount}
                appliedRule={report.optimizedClassification.appliedRule}
              />
            </div>
          </div>

          <div className="rounded-2xl border border-blue-100 bg-blue-50 p-5">
            <p className="text-sm font-semibold uppercase tracking-wide text-brand-primary">
              ML Confidence
            </p>

            <p className="mt-3 text-4xl font-bold text-brand-primary">
              {(report.ml.confidence * 100).toFixed(0)}%
            </p>

            <div className="mt-4 h-3 overflow-hidden rounded-full bg-white">
              <div
                className="h-full rounded-full bg-blue-600"
                style={{ width: `${report.ml.confidence * 100}%` }}
              />
            </div>

            <p className="mt-4 text-sm leading-6 text-brand-muted">
              Model version:{' '}
              <span className="font-semibold text-brand-text">
                {report.ml.modelVersion ?? 'N/A'}
              </span>
            </p>

            <p className="mt-2 text-sm leading-6 text-brand-muted">
              Fallback:{' '}
              <span className="font-semibold text-brand-text">
                {report.ml.fallbackUsed ? 'Yes' : 'No'}
              </span>
            </p>
          </div>
        </div>
      </section>

      <section className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-brand-text">
          Business Explanation
        </h2>

        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          <ExplanationBox
            title="Current fee explanation"
            text={report.currentClassification.explanation}
          />

          <ExplanationBox
            title="Optimized fee explanation"
            text={report.optimizedClassification.explanation}
          />
        </div>
      </section>
    </div>
  );
}

function MetricCard({
  label,
  value,
  helper,
  tone,
}: {
  label: string;
  value: string;
  helper: string;
  tone: 'neutral' | 'success' | 'primary';
}) {
  const toneClass =
    tone === 'success'
      ? 'bg-green-50 text-green-700'
      : tone === 'primary'
        ? 'bg-blue-50 text-brand-primary'
        : 'bg-slate-50 text-brand-text';

  return (
    <div className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
      <div className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${toneClass}`}>
        {label}
      </div>

      <p className="mt-4 text-3xl font-bold text-brand-text">{value}</p>

      <p className="mt-2 text-sm text-brand-muted">{helper}</p>
    </div>
  );
}

function FeeBox({
  title,
  category,
  feeRate,
  feeAmount,
  appliedRule,
}: {
  title: string;
  category: string;
  feeRate: number;
  feeAmount: number;
  appliedRule: string;
}) {
  return (
    <div className="rounded-2xl border border-brand-border p-5">
      <h3 className="text-sm font-semibold text-brand-text">{title}</h3>

      <p className="mt-3 text-lg font-semibold text-brand-text">{category}</p>

      <div className="mt-4 grid gap-3">
        <Field label="Fee rate" value={`${(feeRate * 100).toFixed(2)}%`} />
        <Field label="Fee amount" value={formatMoney(feeAmount, 'EUR')} />
        <Field label="Applied rule" value={appliedRule} />
      </div>
    </div>
  );
}

function ExplanationBox({ title, text }: { title: string; text: string }) {
  return (
    <div className="rounded-2xl border border-brand-border bg-slate-50 p-5">
      <p className="text-sm font-semibold text-brand-text">{title}</p>
      <p className="mt-2 text-sm leading-6 text-brand-muted">{text}</p>
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs uppercase tracking-wide text-brand-muted">
        {label}
      </p>
      <p className="mt-1 break-words text-sm font-semibold text-brand-text">
        {value}
      </p>
    </div>
  );
}

function Badge({
  label,
  tone,
}: {
  label: string;
  tone: 'success' | 'warning' | 'neutral';
}) {
  const toneClass =
    tone === 'success'
      ? 'bg-green-50 text-green-700'
      : tone === 'warning'
        ? 'bg-orange-50 text-orange-700'
        : 'bg-slate-100 text-brand-text';

  return (
    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${toneClass}`}>
      {label}
    </span>
  );
}

function formatMoney(value: number, currency: string) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(value);
}