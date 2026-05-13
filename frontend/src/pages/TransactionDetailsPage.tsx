import { useEffect, useState } from 'react';
import { mlService, type TransactionClassification } from '../services/api/mlService';
import type { MockTransaction } from '../mocks/mockTransactions.ts';

type Props = {
  transactionId: string | null;
};


export function TransactionDetailsPage({ transactionId }: Props) {
  const [transaction, setTransaction] = useState<MockTransaction | null>(null);

  const [classification, setClassification] =
    useState<TransactionClassification | null>(null);

  useEffect(() => {
    if (!transactionId) return;

    mlService.getTransactionById(transactionId).then((result) => {
      setTransaction(result ?? null);
    });

    mlService.getClassification(transactionId).then((result) => {
      setClassification(result);
    });
  }, [transactionId]);

  const renderValue = (value?: string | number | boolean | null) => {
    if (value === undefined || value === null || value === '') {
      return 'N/A';
    }

    if (typeof value === 'boolean') {
      return value ? 'Yes' : 'No';
    }

    return value;
  };

  if (!transactionId) {
    return (
      <section className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-semibold text-brand-text">
          Transaction Details
        </h1>

        <p className="mt-3 text-sm text-brand-muted">
          No transaction selected yet.
        </p>
      </section>
    );
  }

  if (!transaction) {
    return (
      <section className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-semibold text-brand-text">
          Transaction Details
        </h1>

        <p className="mt-3 text-sm text-brand-muted">
          Loading transaction...
        </p>
      </section>
    );
  }

  return (
    <div className="grid gap-6">
      <section className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-sm font-medium uppercase tracking-wide text-brand-primary">
              Transaction Details
            </p>

            <h1 className="mt-2 text-2xl font-semibold text-brand-text">
              {transaction.transactionId}
            </h1>

            <p className="mt-2 text-sm text-brand-muted">
              Detailed transaction context and fee qualification inputs.
            </p>
          </div>

          <div className="rounded-xl bg-slate-100 px-4 py-3 text-sm font-semibold text-brand-text">
            {transaction.status}
          </div>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-brand-text">
            Transaction Information
          </h2>

          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            <Field
              label="Amount"
              value={`${transaction.amount.toFixed(2)} ${transaction.currency}`}
            />

            <Field
              label="Merchant"
              value={renderValue(transaction.merchant)}
            />

            <Field
              label="Merchant Country"
              value={renderValue(transaction.merchantCountry)}
            />

            <Field
              label="Merchant ID"
              value={renderValue(transaction.merchantId)}
            />

            <Field label="MCC" value={renderValue(transaction.mcc)} />

            <Field
              label="Region"
              value={renderValue(transaction.region)}
            />
          </div>
        </div>

        <div className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-brand-text">
            Card & Network Details
          </h2>

          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            <Field
              label="Card Network"
              value={renderValue(transaction.cardNetwork)}
            />

            <Field
              label="Card Type"
              value={renderValue(transaction.cardType)}
            />

            <Field
              label="Channel"
              value={renderValue(transaction.channel)}
            />

            <Field label="3DS" value={renderValue(transaction.threeDS)} />

            <Field label="ECI" value={renderValue(transaction.eci)} />

            <Field
              label="Issuer Country"
              value={renderValue(transaction.issuerCountry)}
            />

            <Field
              label="Acquirer Country"
              value={renderValue(transaction.acquirerCountry)}
            />
          </div>
        </div>
      </section>

      <section className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-brand-text">
          Timing Information
        </h2>

        <div className="mt-6 grid gap-4 sm:grid-cols-3">
          <Field
            label="Authorization Date"
            value={renderValue(transaction.authorizationDate)}
          />

          <Field
            label="Clearing Date"
            value={renderValue(transaction.clearingDate)}
          />

          <Field
            label="Clearing Delay"
            value={
              transaction.clearingDelayDays !== undefined
                ? `${transaction.clearingDelayDays} days`
                : 'N/A'
            }
          />
        </div>
      </section>

      <section className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-sm font-medium uppercase tracking-wide text-brand-primary">
              Current Classification
            </p>

            <h2 className="mt-2 text-2xl font-semibold text-brand-text">
              {classification?.category ?? 'N/A'}
            </h2>
          </div>

          <div className="rounded-xl bg-blue-50 px-4 py-3 text-right">
            <p className="text-xs uppercase tracking-wide text-brand-primary">
              Fee Rate
            </p>

            <p className="mt-1 text-lg font-semibold text-brand-primary">
              {classification
                ? `${classification.feeRatePercent.toFixed(2)}%`
                : 'N/A'}
            </p>
          </div>
        </div>

        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          <Field
            label="Fee Amount"
            value={
              classification
                ? `${classification.feeAmount.toFixed(2)} ${classification.currency}`
                : 'N/A'
            }
          />

          <Field
            label="Category Code"
            value={classification?.categoryCode ?? 'N/A'}
          />

          <Field
            label="Rule Priority"
            value={classification?.rulePriority ?? 'N/A'}
          />

          <Field
            label="Confidence"
            value={
              classification
                ? `${(classification.confidence * 100).toFixed(0)}%`
                : 'N/A'
            }
          />
        </div>

        <div className="mt-6 rounded-xl border border-brand-border bg-slate-50 p-4">
          <p className="text-sm font-semibold text-brand-text">
            Explanation
          </p>

          <p className="mt-2 text-sm leading-6 text-brand-muted">
            {classification?.explanation ?? 'No explanation available.'}
          </p>

          <p className="mt-4 text-sm font-semibold text-brand-text">
            Fee Calculation
          </p>

          <p className="mt-2 text-sm leading-6 text-brand-muted">
            {classification?.calculationMethod ?? 'N/A'}
          </p>
        </div>

        <div className="mt-6">
          <h3 className="text-sm font-semibold text-brand-text">
            Condition Results
          </h3>

          <div className="mt-3 grid gap-3">
            {classification?.conditionResults.length ? (
              classification.conditionResults.map((condition) => (
                <div
                  key={`${condition.field}-${condition.outcome}`}
                  className="rounded-xl border border-brand-border p-4"
                >
                  <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                    <p className="text-sm font-semibold text-brand-text">
                      {condition.field}
                    </p>

                    <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-brand-text">
                      {condition.outcome}
                    </span>
                  </div>

                  <div className="mt-3 grid gap-3 sm:grid-cols-2">
                    <Field label="Expected" value={condition.expected} />
                    <Field label="Actual" value={condition.actual} />
                  </div>

                  {condition.message ? (
                    <p className="mt-3 text-sm text-brand-muted">
                      {condition.message}
                    </p>
                  ) : null}
                </div>
              ))
            ) : (
              <p className="text-sm text-brand-muted">
                No condition details available.
              </p>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}

type FieldProps = {
  label: string;
  value: string | number;
};

function Field({ label, value }: FieldProps) {
  return (
    <div className="rounded-xl border border-brand-border p-4">
      <p className="text-xs uppercase tracking-wide text-brand-muted">
        {label}
      </p>

      <p className="mt-2 text-sm font-semibold text-brand-text">
        {value}
      </p>
    </div>
  );
}