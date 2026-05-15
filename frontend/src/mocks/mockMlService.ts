import { mockAnomalies } from './mockAnomalies.ts';
import { mockOptimizationReport } from './mockOptimizationReport.ts';
import { mockRecommendations } from './mockRecommendations.ts';
import { mockTransactions } from './mockTransactions.ts';

export const mockMlService = {
  async getTransactions(page = 1, pageSize = 10) {
    const startIndex = (page - 1) * pageSize;
    const rows = mockTransactions.slice(startIndex, startIndex + pageSize);

    return {
      rows,
      total: mockTransactions.length,
      page,
      pageSize,
      totalPages: Math.max(1, Math.ceil(mockTransactions.length / pageSize)),
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