import { useEffect, useMemo, useState } from 'react';
import { mockMlService } from '../mocks/mockMlService.ts';
import type { MockRecommendation } from '../mocks/mockRecommendations.ts';

export function RecommendationsPage() {
  const [recommendations, setRecommendations] = useState<
    MockRecommendation[]
  >([]);

  useEffect(() => {
    mockMlService.getRecommendations().then(setRecommendations);
  }, []);

  const sortedRecommendations = useMemo(() => {
    return [...recommendations].sort((a, b) => b.score - a.score);
  }, [recommendations]);

  return (
    <div className="grid gap-6">
      <section className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p className="text-sm font-medium uppercase tracking-wide text-brand-primary">
              Recommendations
            </p>

            <h1 className="mt-2 text-2xl font-semibold text-brand-text sm:text-3xl">
              Optimization Recommendations
            </h1>

            <p className="mt-3 max-w-3xl text-sm leading-6 text-brand-muted">
              Ranked optimization recommendations generated from mock ML
              scoring logic.
            </p>
          </div>

          <div className="rounded-xl bg-blue-50 px-4 py-3 text-sm font-semibold text-brand-primary">
            {sortedRecommendations.length} recommendations
          </div>
        </div>
      </section>

      <section className="grid gap-5">
        {sortedRecommendations.map((recommendation) => (
          <RecommendationCard
            key={recommendation.id}
            recommendation={recommendation}
          />
        ))}
      </section>
    </div>
  );
}

function RecommendationCard({
  recommendation,
}: {
  recommendation: MockRecommendation;
}) {
  return (
    <article className="rounded-2xl border border-brand-border bg-white p-6 shadow-sm">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <Badge
              label={recommendation.priority}
              tone={
                recommendation.priority === 'HIGH'
                  ? 'danger'
                  : recommendation.priority === 'MEDIUM'
                    ? 'warning'
                    : 'neutral'
              }
            />

            <Badge
              label={recommendation.difficulty}
              tone={
                recommendation.difficulty === 'EASY'
                  ? 'success'
                  : recommendation.difficulty === 'MEDIUM'
                    ? 'warning'
                    : 'danger'
              }
            />

            <Badge
              label={
                recommendation.fallbackUsed
                  ? 'Fallback ranking'
                  : 'ML ranking'
              }
              tone={recommendation.fallbackUsed ? 'warning' : 'success'}
            />
          </div>

          <h2 className="mt-4 text-xl font-semibold text-brand-text">
            {recommendation.recommendationType}
          </h2>

          <p className="mt-2 text-sm leading-6 text-brand-muted">
            {recommendation.action}
          </p>
        </div>

        <div className="rounded-2xl bg-blue-50 px-5 py-4 text-center lg:min-w-[140px]">
          <p className="text-xs uppercase tracking-wide text-brand-primary">
            Score
          </p>

          <p className="mt-2 text-3xl font-bold text-brand-primary">
            {(recommendation.score * 100).toFixed(0)}
          </p>
        </div>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Field
          label="Current Value"
          value={recommendation.currentValue}
        />

        <Field
          label="Recommended Value"
          value={recommendation.recommendedValue}
        />

        <Field
          label="Expected Impact"
          value={recommendation.expectedImpact}
        />

        <Field
          label="Priority"
          value={recommendation.priority}
        />
      </div>

      <div className="mt-6 rounded-xl border border-brand-border bg-slate-50 p-4">
        <p className="text-sm font-semibold text-brand-text">
          Ranking Reason
        </p>

        <p className="mt-2 text-sm leading-6 text-brand-muted">
          {recommendation.rankingReason}
        </p>
      </div>
    </article>
  );
}

function Field({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
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

function Badge({
  label,
  tone,
}: {
  label: string;
  tone: 'success' | 'warning' | 'danger' | 'neutral';
}) {
  const toneClass =
    tone === 'success'
      ? 'bg-green-50 text-green-700'
      : tone === 'warning'
        ? 'bg-orange-50 text-orange-700'
        : tone === 'danger'
          ? 'bg-red-50 text-red-700'
          : 'bg-slate-100 text-brand-text';

  return (
    <span
      className={`rounded-full px-3 py-1 text-xs font-semibold ${toneClass}`}
    >
      {label}
    </span>
  );
}