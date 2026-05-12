export type RecommendationPriority = 'HIGH' | 'MEDIUM' | 'LOW';
export type RecommendationDifficulty = 'EASY' | 'MEDIUM' | 'HARD';

export type MockRecommendation = {
  id: string;
  recommendationType: string;
  action: string;
  currentValue: string;
  recommendedValue: string;
  expectedImpact: string;
  score: number;
  priority: RecommendationPriority;
  rankingReason: string;
  difficulty: RecommendationDifficulty;
  fallbackUsed: boolean;
};

export const mockRecommendations: MockRecommendation[] = [
  {
    id: 'REC-001',
    recommendationType: 'ENABLE_3DS',
    action: 'Enable 3DS authentication',
    currentValue: '3DS disabled',
    recommendedValue: '3DS enabled',
    expectedImpact: 'Lower ecommerce interchange fee',
    score: 0.94,
    priority: 'HIGH',
    rankingReason: 'High impact and easy to apply for ecommerce transactions.',
    difficulty: 'EASY',
    fallbackUsed: false,
  },
  {
    id: 'REC-002',
    recommendationType: 'REDUCE_CLEARING_TIME',
    action: 'Clear transaction faster',
    currentValue: '2 days',
    recommendedValue: '0 days',
    expectedImpact: 'Improves fee qualification category',
    score: 0.88,
    priority: 'HIGH',
    rankingReason: 'Delayed clearing prevents optimal fee classification.',
    difficulty: 'MEDIUM',
    fallbackUsed: false,
  },
  {
    id: 'REC-003',
    recommendationType: 'IMPROVE_ECI',
    action: 'Use authenticated ECI value',
    currentValue: '07',
    recommendedValue: '05',
    expectedImpact: 'Signals secure authenticated ecommerce transaction',
    score: 0.73,
    priority: 'MEDIUM',
    rankingReason: 'ECI value does not currently indicate successful authentication.',
    difficulty: 'EASY',
    fallbackUsed: true,
  },
];