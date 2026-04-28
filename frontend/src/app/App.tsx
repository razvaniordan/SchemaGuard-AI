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
    <main style={{ maxWidth: '720px', margin: '0 auto', padding: '2rem' }}>
      <Card
        title="SchemeGuard AI"
        description="State management and API flow are configured."
      >
        <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '1rem' }}>
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

          <Button type="submit" disabled={status === 'loading'}>
            {status === 'loading' ? 'Calculating...' : 'Calculate fee'}
          </Button>

          {error ? (
            <p role="alert" style={{ color: 'var(--color-danger)' }}>
              {error}
            </p>
          ) : null}

          {result ? (
            <div>
              <strong>Result:</strong>
              <p>Interchange fee: {result.interchangeFee}</p>
              <p>Effective rate: {result.effectiveRate}</p>
              <p>Status: {result.qualificationStatus}</p>
            </div>
          ) : null}
        </form>
      </Card>
    </main>
  );
}