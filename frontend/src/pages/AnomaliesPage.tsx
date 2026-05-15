import { useEffect, useState } from 'react';
import { mlService } from '../services/api/mlService';
import type { AnomalyDto } from '../services/api/types';

function severityClass(severity: AnomalyDto['severity']) {
  switch (severity) {
    case 'HIGH':
      return 'bg-red-50 text-red-700 border-red-200';
    case 'MEDIUM':
      return 'bg-yellow-50 text-yellow-700 border-yellow-200';
    case 'LOW':
      return 'bg-green-50 text-green-700 border-green-200';
    default:
      return 'bg-gray-50 text-gray-700 border-gray-200';
  }
}

function AnomalyCard({ anomaly }: { anomaly: AnomalyDto }) {
  return (
    <article className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <div className="flex flex-wrap items-center gap-3">
            <span
              className={`rounded-full border px-3 py-1 text-xs font-semibold ${severityClass(
                anomaly.severity,
              )}`}
            >
              {anomaly.severity}
            </span>

            <span className="text-xs font-medium uppercase tracking-wide text-brand-muted">
              Transaction #{anomaly.transactionId}
            </span>
          </div>

          <h3 className="mt-4 text-lg font-semibold text-brand-primary">
            {anomaly.anomalyType}
          </h3>

          <p className="mt-2 text-sm leading-6 text-brand-muted">
            {anomaly.explanation}
          </p>
        </div>
      </div>
    </article>
  );
}

export function AnomaliesPage() {
  const [anomalies, setAnomalies] = useState<AnomalyDto[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

 useEffect(() => {
  let isMounted = true;

  mlService
    .getAnomalies()
    .then((result) => {
      if (!isMounted) return;
      setAnomalies(result);
    })
    .catch((error) => {
      if (!isMounted) return;

      console.error('Failed to load anomalies:', error);
      setErrorMessage(
        'Could not load anomalies from the backend. Please try again.',
      );
    })
    .finally(() => {
      if (!isMounted) return;
      setIsLoading(false);
    });

  return () => {
    isMounted = false;
  };
}, []);

  return (
    <div className="space-y-6">
      <section className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-wide text-brand-accent">
          Portfolio Anomalies
        </p>

        <h1 className="mt-2 text-3xl font-bold text-brand-primary">
          Anomaly Insights
        </h1>

        <p className="mt-3 max-w-3xl text-sm leading-6 text-brand-muted">
          Detected anomalies from backend portfolio analysis, grouped by
          severity, transaction and anomaly type.
        </p>
      </section>

      {isLoading && (
        <section className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
          <p className="text-sm text-brand-muted">Loading anomalies...</p>
        </section>
      )}

      {!isLoading && errorMessage && (
        <section className="rounded-2xl border border-red-200 bg-red-50 p-6 shadow-sm">
          <p className="text-sm font-medium text-red-700">{errorMessage}</p>
        </section>
      )}

      {!isLoading && !errorMessage && anomalies.length === 0 && (
        <section className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
          <p className="text-sm font-medium text-brand-primary">
            No anomalies detected.
          </p>
          <p className="mt-2 text-sm text-brand-muted">
            The backend did not return any portfolio anomalies.
          </p>
        </section>
      )}

      {!isLoading && !errorMessage && anomalies.length > 0 && (
        <section className="grid gap-4">
          {anomalies.map((anomaly) => (
            <AnomalyCard key={anomaly.id} anomaly={anomaly} />
          ))}
        </section>
      )}
    </div>
  );
}