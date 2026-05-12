import { useEffect, useState } from 'react';
import { mockMlService } from '../mocks/mockMlService.ts';
import type {
  MissedCondition,
  MockOptimizationReport,
} from '../mocks/mockOptimizationReport.ts';

type Props = {
  transactionId: string | null;
};

export function MissedConditionsPage({ transactionId }: Props) {
  const [report, setReport] = useState<MockOptimizationReport | null>(null);

  useEffect(() => {
    mockMlService
      .getOptimizationReport(transactionId ?? 'TX-1001')
      .then(setReport);
  }, [transactionId]);

  if (!report) {
    return (
      <section className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-semibold text-brand-text">
          Missed Conditions
        </h1>
        <p className="mt-3 text-sm text-brand-muted">Loading conditions...</p>
      </section>
    );
  }

  return (
    <div className="grid gap-6">
      <section className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p className="text-sm font-medium uppercase tracking-wide text-brand-primary">
              Explainability
            </p>

            <h1 className="mt-2 text-2xl font-semibold text-brand-text sm:text-3xl">
              Missed Conditions
            </h1>

            <p className="mt-3 max-w-3xl text-sm leading-6 text-brand-muted">
              Conditions that prevented the transaction from qualifying for a
              better fee category.
            </p>
          </div>

          <div className="rounded-xl bg-orange-50 px-4 py-3 text-sm font-semibold text-orange-700">
            {report.missedConditions.length} missed conditions
          </div>
        </div>
      </section>

      <section className="grid gap-5">
        {report.missedConditions.map((condition) => (
          <ConditionCard key={condition.id} condition={condition} />
        ))}
      </section>
    </div>
  );
}

function ConditionCard({ condition }: { condition: MissedCondition }) {
  return (
    <article className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="text-sm font-medium uppercase tracking-wide text-brand-primary">
            {condition.condition}
          </p>

          <h2 className="mt-2 text-xl font-semibold text-brand-text">
            Optimization condition not met
          </h2>

          <p className="mt-2 text-sm leading-6 text-brand-muted">
            {condition.explanation}
          </p>
        </div>

        <div className="rounded-2xl bg-blue-50 px-5 py-4 text-center lg:min-w-[140px]">
          <p className="text-xs uppercase tracking-wide text-brand-primary">
            Confidence
          </p>

          <p className="mt-2 text-3xl font-bold text-brand-primary">
            {(condition.confidence * 100).toFixed(0)}%
          </p>
        </div>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-3">
        <Field label="Current Value" value={condition.currentValue} />
        <Field label="Optimal Value" value={condition.optimalValue} />
        <Field label="Impact" value={condition.impact} />
      </div>
    </article>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-brand-border p-4">
      <p className="text-xs uppercase tracking-wide text-brand-muted">
        {label}
      </p>

      <p className="mt-2 text-sm font-semibold text-brand-text">{value}</p>
    </div>
  );
}