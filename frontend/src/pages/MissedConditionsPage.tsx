import { useEffect, useState } from 'react';
import { mlService } from '../services/api/mlService';
import type {
  MissedConditionDto,
  OptimizationReportDto,
} from '../services/api/types';

type Props = {
  transactionId: string | null;
};

export function MissedConditionsPage({ transactionId }: Props) {
  const [report, setReport] = useState<OptimizationReportDto | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
  if (!transactionId) {
    return;
  }

  let isMounted = true;

  async function loadReport() {
    try {
      const response = await mlService.getOptimizationReport(transactionId);

      if (!isMounted) return;

      setReport(response);
      setErrorMessage(null);
    } catch (error) {
      if (!isMounted) return;

      console.error(error);
      setErrorMessage('Failed to load optimization report.');
    } finally {
      if (isMounted) {
        setIsLoading(false);
      }
    }
  }

  loadReport();

  return () => {
    isMounted = false;
  };
}, [transactionId]);

  if (!transactionId) {
    return (
      <section className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
        <p className="text-sm font-medium uppercase tracking-wide text-brand-primary">
          Explainability
        </p>

        <h1 className="mt-2 text-2xl font-semibold text-brand-text sm:text-3xl">
          Missed Conditions
        </h1>

        <p className="mt-3 max-w-3xl text-sm leading-6 text-brand-muted">
          Select a transaction first to see the conditions that prevented it
          from qualifying for a better fee category.
        </p>
      </section>
    );
  }

  if (isLoading) {
    return (
      <section className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-semibold text-brand-text">
          Missed Conditions
        </h1>
        <p className="mt-3 text-sm text-brand-muted">Loading conditions...</p>
      </section>
    );
  }

  if (errorMessage) {
    return (
      <section className="rounded-2xl border border-red-200 bg-red-50 p-6 shadow-sm">
        <h1 className="text-2xl font-semibold text-red-800">
          Missed Conditions
        </h1>
        <p className="mt-3 text-sm font-medium text-red-700">
          {errorMessage}
        </p>
      </section>
    );
  }

  if (!report) {
    return null;
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
              Conditions that prevented transaction #{report.transactionId} from
              qualifying for a better fee category.
            </p>
          </div>

          <div className="rounded-xl bg-orange-50 px-4 py-3 text-sm font-semibold text-orange-700">
            {report.missedConditions.length} missed conditions
          </div>
        </div>
      </section>

      {report.missedConditions.length === 0 ? (
        <section className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
          <p className="text-sm font-semibold text-brand-text">
            No missed conditions found for transaction #{report.transactionId}.
          </p>
          <p className="mt-2 text-sm text-brand-muted">
            The backend did not identify 3DS, clearing-time, category or other
            qualification blockers for this transaction.
          </p>
        </section>
      ) : (
        <section className="grid gap-5">
          {report.missedConditions.map((condition) => (
            <ConditionCard key={condition.id} condition={condition} />
          ))}
        </section>
      )}
    </div>
  );
}

function ConditionCard({ condition }: { condition: MissedConditionDto }) {
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
        <Field label="Impact" value={String(condition.impact)} />
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
