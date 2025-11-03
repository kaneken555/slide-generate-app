import { useState } from 'react';
import { QueryClient, QueryClientProvider, useMutation, useQuery } from '@tanstack/react-query';
import { api } from './api';
import type { SlideRequest, JobStatusResponse } from './types';

// Create a client
const queryClient = new QueryClient();

function SlideGeneratorApp() {
  const [jobId, setJobId] = useState<string | null>(null);
  const [formData, setFormData] = useState<SlideRequest>({
    topic: '',
    n_slides: 5,
    language: 'Japanese',
  });

  // Mutation for creating slides
  const createSlidesMutation = useMutation({
    mutationFn: (data: SlideRequest) => api.createSlides(data),
    onSuccess: (response) => {
      setJobId(response.job_id);
    },
  });

  // Query for polling job status
  const { data: jobStatus, isLoading: isPolling } = useQuery({
    queryKey: ['jobStatus', jobId],
    queryFn: () => api.getJobStatus(jobId!),
    enabled: !!jobId,
    refetchInterval: (data) => {
      // Stop polling if completed or failed
      if (data?.status === 'completed' || data?.status === 'failed') {
        return false;
      }
      return 2000; // Poll every 2 seconds
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setJobId(null); // Reset job ID
    createSlidesMutation.mutate(formData);
  };

  const handleReset = () => {
    setJobId(null);
    createSlidesMutation.reset();
  };

  const isGenerating = createSlidesMutation.isPending || (jobId && jobStatus?.status !== 'completed' && jobStatus?.status !== 'failed');

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🎨 Slide Generator
          </h1>
          <p className="text-gray-600">
            AI-powered slide generation from any topic
          </p>
        </div>

        {/* Main Card */}
        <div className="bg-white rounded-lg shadow-xl p-8">
          {/* Form */}
          {!jobId && (
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="topic" className="block text-sm font-medium text-gray-700 mb-2">
                  Topic
                </label>
                <input
                  id="topic"
                  type="text"
                  value={formData.topic}
                  onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
                  placeholder="e.g., Machine Learning Basics"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                  disabled={isGenerating}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="n_slides" className="block text-sm font-medium text-gray-700 mb-2">
                    Number of Slides
                  </label>
                  <input
                    id="n_slides"
                    type="number"
                    min="1"
                    max="50"
                    value={formData.n_slides}
                    onChange={(e) => setFormData({ ...formData, n_slides: parseInt(e.target.value) })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                    disabled={isGenerating}
                  />
                </div>

                <div>
                  <label htmlFor="language" className="block text-sm font-medium text-gray-700 mb-2">
                    Language
                  </label>
                  <select
                    id="language"
                    value={formData.language}
                    onChange={(e) => setFormData({ ...formData, language: e.target.value })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    disabled={isGenerating}
                  >
                    <option value="Japanese">Japanese</option>
                    <option value="English">English</option>
                  </select>
                </div>
              </div>

              <button
                type="submit"
                disabled={isGenerating || !formData.topic}
                className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {isGenerating ? 'Generating...' : 'Generate Slides'}
              </button>

              {createSlidesMutation.isError && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                  Error: {createSlidesMutation.error instanceof Error ? createSlidesMutation.error.message : 'Failed to create slides'}
                </div>
              )}
            </form>
          )}

          {/* Job Status */}
          {jobId && jobStatus && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">
                  {jobStatus.status === 'completed' ? '✅ Completed!' :
                   jobStatus.status === 'failed' ? '❌ Failed' :
                   '⏳ Processing...'}
                </h2>
                <span className={`px-4 py-2 rounded-full text-sm font-medium ${
                  jobStatus.status === 'completed' ? 'bg-green-100 text-green-800' :
                  jobStatus.status === 'failed' ? 'bg-red-100 text-red-800' :
                  jobStatus.status === 'running' ? 'bg-blue-100 text-blue-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {jobStatus.status.toUpperCase()}
                </span>
              </div>

              {/* Progress */}
              {jobStatus.status !== 'completed' && jobStatus.status !== 'failed' && (
                <div className="space-y-2">
                  <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-600 animate-pulse" style={{ width: '50%' }}></div>
                  </div>
                  <p className="text-sm text-gray-600 text-center">
                    This may take up to 2 minutes...
                  </p>
                </div>
              )}

              {/* Steps */}
              {jobStatus.result?.steps && (
                <div className="space-y-3">
                  <h3 className="font-medium text-gray-900">Steps:</h3>
                  {jobStatus.result.steps.map((step, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <span className="text-xl">
                          {step.status === 'completed' ? '✓' : '⟳'}
                        </span>
                        <span className="font-medium capitalize">{step.name}</span>
                      </div>
                      <span className="text-sm text-gray-600">
                        {step.duration_ms ? `${(step.duration_ms / 1000).toFixed(1)}s` : ''}
                      </span>
                    </div>
                  ))}
                </div>
              )}

              {/* Result */}
              {jobStatus.status === 'completed' && jobStatus.result?.result && (
                <div className="space-y-4 p-6 bg-green-50 border border-green-200 rounded-lg">
                  <h3 className="font-bold text-lg text-green-900">Your slides are ready!</h3>
                  <div className="space-y-2 text-sm text-gray-700">
                    <p><strong>Topic:</strong> {jobStatus.result.result.topic}</p>
                    <p><strong>Slides:</strong> {jobStatus.result.result.n_slides}</p>
                    <p><strong>Presentation ID:</strong> {jobStatus.result.result.presentation_id}</p>
                  </div>
                  <div className="flex gap-3">
                    <button className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-green-700 transition-colors">
                      📥 Download
                    </button>
                    <button className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-blue-700 transition-colors">
                      ✏️ Edit
                    </button>
                  </div>
                </div>
              )}

              {/* Error */}
              {jobStatus.status === 'failed' && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                  <p className="font-medium">Error occurred:</p>
                  <p className="text-sm mt-1">{jobStatus.error || 'Unknown error'}</p>
                </div>
              )}

              {/* Reset Button */}
              {(jobStatus.status === 'completed' || jobStatus.status === 'failed') && (
                <button
                  onClick={handleReset}
                  className="w-full bg-gray-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-gray-700 transition-colors"
                >
                  Create New Slides
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <SlideGeneratorApp />
    </QueryClientProvider>
  );
}

export default App;
