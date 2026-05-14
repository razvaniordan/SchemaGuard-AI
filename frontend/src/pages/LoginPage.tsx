import { useState } from 'react';
import type { FormEvent } from 'react';
import { Button, Card, Input } from '../components/ui';
import { login } from '../services/api/auth';

type LoginPageProps = {
  onLogin: (token: string) => void;
};

export function LoginPage({ onLogin }: LoginPageProps) {
  const [username, setUsername] = useState('demo');
  const [password, setPassword] = useState('password');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const response = await login(username, password);
      onLogin(response.token);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-50 px-4 py-10 text-brand-text">
      <div className="w-full max-w-md">
        <div className="mb-6 text-center">
          <p className="text-xs font-semibold uppercase tracking-wide text-brand-primary">
            SchemeGuard AI
          </p>

          <h1 className="mt-2 text-3xl font-semibold text-brand-text">
            Sign in
          </h1>

          <p className="mt-2 text-sm text-brand-muted">
            Use the existing demo account to access the frontend MVP.
          </p>
        </div>

        <Card
          title="Demo login"
          description="Credentials are prefilled for local development."
        >
          <form className="grid gap-4" onSubmit={handleSubmit}>
            <Input
              label="Username"
              name="username"
              autoComplete="username"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              disabled={isSubmitting}
            />

            <Input
              label="Password"
              name="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              disabled={isSubmitting}
            />

            {error ? (
              <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-brand-danger">
                {error}
              </p>
            ) : null}

            <Button type="submit" size="lg" disabled={isSubmitting}>
              {isSubmitting ? 'Signing in...' : 'Sign in'}
            </Button>
          </form>
        </Card>
      </div>
    </main>
  );
}