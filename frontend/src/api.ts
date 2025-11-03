// api.ts
// API client for Slide Generation backend

import axios from 'axios';
import type { SlideRequest, CreateSlideResponse, JobStatusResponse } from './types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  /**
   * Create a new slide generation job
   */
  createSlides: async (data: SlideRequest): Promise<CreateSlideResponse> => {
    const response = await apiClient.post<CreateSlideResponse>('/api/v1/slides', data);
    return response.data;
  },

  /**
   * Get job status
   */
  getJobStatus: async (jobId: string): Promise<JobStatusResponse> => {
    const response = await apiClient.get<JobStatusResponse>(`/api/v1/slides/${jobId}`);
    return response.data;
  },

  /**
   * Health check
   */
  healthCheck: async (): Promise<{ status: string }> => {
    const response = await apiClient.get('/health');
    return response.data;
  },
};
