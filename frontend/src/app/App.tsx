import { Button, Card, Input } from '../components/ui';
import { usePreferencesStore, useTransactionStore } from '../store';

export default function App() {
  const draft = useTransactionStore((state) => state.draft);
  const result = useTransactionStore((state) => state.result);
  const status = useTransactionStore((state) => state.status);
  const error = useTransactionStore((state) => state.error);
  const updateDraft = useTransactionStore((state) => state.updateDraft);
  const calculateFee = useTransactionStore((state) => state.calculateFee);

  const setPreferredCurrency = usePreferencesStore(
    (state) => state.setPreferredCurrency,
  );

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    void calculateFee();
  };

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-6 sm:px-6 lg:px-8">
      <section className="mx-auto flex w-full max-w-5xl flex-col gap-6">
        <div className="flex flex-col gap-2 text-center sm:text-left">
          <p className="text-sm font-medium uppercase tracking-wide text-brand-muted">
            SchemeGuard AI
          </p>
          <h1 className="text-3xl font-semibold text-brand-text sm:text-4xl">
            Fee qualification dashboard
          </h1>
          <p className="max-w-2xl text-sm text-brand-muted sm:text-base">
            Responsive frontend shell with Tailwind CSS, reusable UI components,
            and state-managed transaction flow.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,2fr)_minmax(280px,1fr)]">
          <Card
            title="Transaction details"
            description="Enter transaction data to calculate interchange fee qualification."
          >
            <form onSubmit={handleSubmit} className="grid gap-4">
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <Input
                  label="Merchant name"
                  name="merchantName"
                  placeholder="Enter merchant name"
                  value={draft.merchantName}
                  onChange={(event) => updateDraft('merchantName', event.target.value)}
                />

                <Input
                  label="Amount"
                  name="amount"
                  type="number"
                  placeholder="100.00"
                  value={draft.amount}
                  onChange={(event) => updateDraft('amount', event.target.value)}
                />

                <Input
                  label="Currency"
                  name="currency"
                  placeholder="USD"
                  value={draft.currency}
                  onChange={(event) => {
                    updateDraft('currency', event.target.value);
                    setPreferredCurrency(event.target.value);
                  }}
                />

                <Input
                  label="MCC"
                  name="mcc"
                  placeholder="5411"
                  value={draft.mcc}
                  onChange={(event) => updateDraft('mcc', event.target.value)}
                />
              </div>

              <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
                <Button type="submit" disabled={status === 'loading'}>
                  {status === 'loading' ? 'Calculating...' : 'Calculate fee'}
                </Button>

                <Button type="button" variant="secondary">
                  Save draft
                </Button>
              </div>

              {error ? (
                <p role="alert" className="text-sm text-brand-danger">
                  {error}
                </p>
              ) : null}
            </form>
          </Card>

          <Card
            title="Calculation result"
            description="Result summary will appear after API calculation."
          >
            {result ? (
              <div className="grid gap-3 text-sm">
                <p>
                  <span className="font-medium">Interchange fee:</span>{' '}
                  {result.interchangeFee}
                </p>
                <p>
                  <span className="font-medium">Effective rate:</span>{' '}
                  {result.effectiveRate}
                </p>
                <p>
                  <span className="font-medium">Status:</span>{' '}
                  {result.qualificationStatus}
                </p>
              </div>
            ) : (
              <p className="text-sm text-brand-muted">
                No calculation result yet.
              </p>
            )}
          </Card>
        </div>
      </section>
    </main>
  );
}