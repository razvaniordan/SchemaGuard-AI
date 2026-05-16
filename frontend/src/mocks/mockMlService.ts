import { mockAnomalies } from './mockAnomalies.ts';
import { mockOptimizationReport } from './mockOptimizationReport.ts';
import { mockRecommendations } from './mockRecommendations.ts';
import { mockTransactions } from './mockTransactions.ts';

export const mockMlService = {
  async getTransactions(page = 1, pageSize = 10, search = '', channel = null, threeDs = null, status = null) {
    const normalizedSearch = search.trim().toLowerCase();

    const filteredBySearch = normalizedSearch.length
      ? mockTransactions.filter((transaction) => {
          return (
            transaction.transactionId.toLowerCase().includes(normalizedSearch) ||
            transaction.merchant.toLowerCase().includes(normalizedSearch) ||
            transaction.currency.toLowerCase().includes(normalizedSearch)
          );
        })
      : mockTransactions;

    const filtered = filteredBySearch.filter((transaction) => {
      if (channel && channel !== 'ALL' && transaction.channel !== channel) return false;
      if (threeDs && threeDs !== 'ALL') {
        const want = threeDs === 'YES';
        if (Boolean(transaction.threeDS) !== want) return false;
      }
      if (status && status !== 'ALL' && transaction.status !== status) return false;
      return true;
    });

    const startIndex = (page - 1) * pageSize;
    const rows = filtered.slice(startIndex, startIndex + pageSize);

    return {
      rows,
      total: filtered.length,
      page,
      pageSize,
      totalPages: Math.max(1, Math.ceil(filtered.length / pageSize)),
    };
  },

  async getTransactionById(transactionId: string) {
    return mockTransactions.find(
      (transaction) => transaction.transactionId === transactionId,
    );
  },

  async getOptimizationReport(transactionId: string) {
    return {
      ...mockOptimizationReport,
      transactionId,
      recommendations: mockRecommendations,
    };
  },

  async getRecommendations() {
    return [...mockRecommendations].sort((a, b) => b.score - a.score);
  },

  async getMissedConditions() {
    return mockOptimizationReport.missedConditions;
  },

  async getAnomalies() {
    return mockAnomalies;
  },

  async getPortfolioSummary() {
    const totalTransactions = mockTransactions.length;

    const totalCurrentFees = 12450.75;
    const totalOptimizedFees = 9870.25;
    const totalEstimatedSavings = totalCurrentFees - totalOptimizedFees;

    return {
      totalTransactions,
      totalCurrentFees,
      totalOptimizedFees,
      totalEstimatedSavings,
      averageFeeRate: 0.0164,
      anomalyCount: mockAnomalies.length,
      topRecommendationTypes: ['ENABLE_3DS', 'REDUCE_CLEARING_TIME', 'IMPROVE_ECI'],
    };
  },
};