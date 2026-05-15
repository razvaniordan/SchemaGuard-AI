import { useMemo, useState } from 'react';
import { TransactionDetailsPage } from '../pages/TransactionDetailsPage';
import { TransactionsPage } from '../pages/TransactionsPage';
import { OptimizationReportPage } from '../pages/OptimizationReportPage';
import { SavingsProjectionPage } from '../pages/SavingsProjectionPage';
import { RecommendationsPage } from '../pages/RecommendationsPage';
import { MissedConditionsPage } from '../pages/MissedConditionsPage';
import { AnomaliesPage } from '../pages/AnomaliesPage';
import { LoginPage } from '../pages/LoginPage';
import { DashboardPage } from '../pages/DashboardPage';
import {
  clearAuthToken,
  getAuthToken,
  saveAuthToken,
} from '../services/api/authStorage';

type PageKey =
  | 'dashboard'
  | 'transactions'
  | 'transaction-details'
  | 'optimization-report'
  | 'savings-projections'
  | 'recommendations'
  | 'missed-conditions'
  | 'anomalies'
  | 'settings';

type NavItem = {
  key: PageKey;
  label: string;
  description: string;
};

const navItems: NavItem[] = [
  {
    key: 'dashboard',
    label: 'Dashboard',
    description: 'Portfolio overview and optimization value.',
  },
  {
    key: 'transactions',
    label: 'Transactions',
    description: 'Transaction list with filters.',
  },
  {
    key: 'transaction-details',
    label: 'Transaction Details',
    description: 'Detailed transaction context and fee inputs.',
  },
  {
    key: 'optimization-report',
    label: 'Optimization Report',
    description: 'Current fee, optimized fee, savings and projections.',
  },
  {
    key: 'recommendations',
    label: 'Recommendations',
    description: 'Ranked optimization recommendations.',
  },
  {
    key: 'missed-conditions',
    label: 'Missed Conditions',
    description: 'Explain why better fee qualification was missed.',
  },
  {
    key: 'savings-projections',
    label: 'Savings Projections',
    description: 'Monthly, yearly and per-transaction savings.',
  },
  {
    key: 'anomalies',
    label: 'Anomalies',
    description: 'Detected anomalies and explanations.',
  },
  {
    key: 'settings',
    label: 'Settings',
    description: 'Application configuration.',
  },
];

function PlaceholderPage({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <section className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
      <p className="text-sm font-medium uppercase tracking-wide text-brand-primary">
        SchemeGuard AI
      </p>

      <h1 className="mt-2 text-2xl font-semibold text-brand-text sm:text-3xl">
        {title}
      </h1>

      <p className="mt-3 max-w-3xl text-sm leading-6 text-brand-muted sm:text-base">
        {description}
      </p>

      <div className="mt-6 rounded-xl border border-dashed border-brand-border bg-slate-50 p-5">
        <p className="text-sm font-medium text-brand-text">UI placeholder</p>
        <p className="mt-1 text-sm text-brand-muted">
          Această pagină este pregătită pentru următoarele story-uri UI.
        </p>
      </div>
    </section>
  );
}

export default function App() {
  const [authToken, setAuthToken] = useState<string | null>(() => getAuthToken());
  const [activePage, setActivePage] = useState<PageKey>('dashboard');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [selectedTransactionId, setSelectedTransactionId] = useState<
    string | null
  >(null);

  const currentPage = useMemo<NavItem>(
    () =>
      navItems.find((item) => item.key === activePage) ?? {
        key: 'dashboard',
        label: 'Dashboard',
        description: 'Portfolio overview and optimization value.',
      },
    [activePage],
  );

  const handleLogin = (token: string) => {
    saveAuthToken(token);
    setAuthToken(token);
    setActivePage('dashboard');
  };

  const handleLogout = () => {
    clearAuthToken();
    setAuthToken(null);
    setActivePage('dashboard');
    setSelectedTransactionId(null);
    setIsMobileMenuOpen(false);
  };

  const handleNavigate = (page: PageKey) => {
    setActivePage(page);
    setIsMobileMenuOpen(false);
  };

  if (!authToken) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return (
    <div className="min-h-screen bg-slate-50 text-brand-text">
      <header className="sticky top-0 z-20 border-b border-brand-border bg-white/95 backdrop-blur lg:hidden">
        <div className="flex items-center justify-between px-4 py-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-brand-primary">
              SchemeGuard AI
            </p>
            <p className="text-sm font-medium text-brand-text">
              {currentPage.label}
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleLogout}
              className="rounded-lg border border-brand-border px-3 py-2 text-sm font-medium text-brand-muted"
            >
              Logout
            </button>

            <button
              type="button"
              onClick={() => setIsMobileMenuOpen((value) => !value)}
              className="rounded-lg border border-brand-border px-3 py-2 text-sm font-medium text-brand-text"
            >
              Menu
            </button>
          </div>
        </div>

        {isMobileMenuOpen && (
          <nav className="border-t border-brand-border bg-white px-4 py-3">
            <div className="grid gap-2">
              {navItems.map((item) => (
                <button
                  key={item.key}
                  type="button"
                  onClick={() => handleNavigate(item.key)}
                  className={`rounded-lg px-3 py-2 text-left text-sm font-medium transition ${
                    activePage === item.key
                      ? 'bg-blue-50 text-brand-primary'
                      : 'text-brand-muted hover:bg-slate-100 hover:text-brand-text'
                  }`}
                >
                  {item.label}
                </button>
              ))}
            </div>
          </nav>
        )}
      </header>

      <div className="lg:grid lg:grid-cols-[280px_1fr]">
        <aside className="hidden min-h-screen border-r border-brand-border bg-white p-5 lg:block">
          <div className="mb-8">
            <p className="text-xs font-semibold uppercase tracking-wide text-brand-primary">
              SchemeGuard AI
            </p>
            <h2 className="mt-2 text-xl font-semibold text-brand-text">
              Fee Optimization
            </h2>
            <p className="mt-1 text-sm text-brand-muted">
              Frontend MVP with backend navigation.
            </p>
          </div>

          <nav className="grid gap-2">
            {navItems.map((item) => (
              <button
                key={item.key}
                type="button"
                onClick={() => handleNavigate(item.key)}
                className={`rounded-xl px-4 py-3 text-left transition ${
                  activePage === item.key
                    ? 'bg-blue-50 text-brand-primary shadow-sm'
                    : 'text-brand-muted hover:bg-slate-100 hover:text-brand-text'
                }`}
              >
                <span className="block text-sm font-semibold">
                  {item.label}
                </span>
                <span className="mt-1 block text-xs leading-5">
                  {item.description}
                </span>
              </button>
            ))}
          </nav>

          <button
            type="button"
            onClick={handleLogout}
            className="mt-8 w-full rounded-xl border border-brand-border px-4 py-3 text-left text-sm font-semibold text-brand-muted transition hover:bg-slate-100 hover:text-brand-text"
          >
            Logout
          </button>
        </aside>

        <main className="p-4 sm:p-6 lg:p-8">
          {activePage === 'dashboard' ? (
            <DashboardPage />
          ) : activePage === 'transactions' ? (
            <TransactionsPage
              onSelectTransaction={(transactionId) => {
                setSelectedTransactionId(transactionId);
                setActivePage('transaction-details');
              }}
            />
          ) : activePage === 'transaction-details' ? (
            <TransactionDetailsPage transactionId={selectedTransactionId} />
          ) : activePage === 'optimization-report' ? (
            <OptimizationReportPage transactionId={selectedTransactionId} />
          ) : activePage === 'savings-projections' ? (
            <SavingsProjectionPage transactionId={selectedTransactionId} />
          ) : activePage === 'recommendations' ? (
            <RecommendationsPage transactionId={selectedTransactionId} />
          ) : activePage === 'missed-conditions' ? (
            <MissedConditionsPage transactionId={selectedTransactionId} />
          )  : activePage === 'anomalies' ? (
            <AnomaliesPage />
          ) : (
            <PlaceholderPage
              title={currentPage.label}
              description={currentPage.description}
            />
          )}
        </main>
      </div>
    </div>
  );
}