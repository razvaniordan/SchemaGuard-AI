import { apiClient } from './client';
import type { DashboardOverviewDto } from './types';

export const dashboardService = {
  getOverview(): Promise<DashboardOverviewDto> {
    return apiClient<DashboardOverviewDto>('/dashboard/overview');
  },
};
