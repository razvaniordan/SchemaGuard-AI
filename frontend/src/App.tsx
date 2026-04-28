import { Button, Card, Input } from './components/ui';

export default function App() {
  return (
    <main style={{ maxWidth: '720px', margin: '0 auto', padding: '2rem' }}>
      <Card
        title="SchemeGuard AI"
        description="Reusable UI components are configured successfully."
        footer={<Button>Continue</Button>}
      >
        <Input
          label="Merchant name"
          name="merchantName"
          placeholder="Enter merchant name"
        />
      </Card>
    </main>
  );
}
