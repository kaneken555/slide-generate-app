// types.ts
// TypeScript type definitions for API

export interface SlideRequest {
  topic: string;
  n_slides: number;
  language: string;
  template?: string;
  export_as?: string;
  refine_temperature?: number;
  custom_instructions?: string;
}

export interface CreateSlideResponse {
  job_id: string;
  status: string;
  status_url: string;
}

export type JobStatus = 'pending' | 'running' | 'completed' | 'failed';

export interface StepInfo {
  name: string;
  status: string;
  duration_ms: number;
}

export interface WorkflowResult {
  success: boolean;
  steps: StepInfo[];
  workflow: {
    id: string;
    name: string;
  };
  result: {
    topic: string;
    n_slides: number;
    outline: string;
    outline_length: number;
    presentation_id: string;
    file_path: string;
    download_url: string;
    status: string;
  };
}

export interface JobStatusResponse {
  job_id: string;
  workflow_id: string;
  status: JobStatus;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  result: WorkflowResult | null;
  error: string | null;
}
