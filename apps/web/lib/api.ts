import {
  AnalysisResponse,
  AnalysisListItem,
  ModelVersionData,
  UserProfile,
  AnalyticsOverview,
  SystemHealthData,
  AuditLogItem,
} from '../types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1';

class APIClient {
  private getAuthHeader(): Record<string, string> {
    if (typeof window === 'undefined') return {};
    const token = localStorage.getItem('truthlens_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...this.getAuthHeader(),
      ...((options.headers as Record<string, string>) || {}),
    };

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      let json: any = null;
      try {
        json = await response.json();
      } catch {
        const text = await response.text().catch(() => '');
        const err = new Error(text || `Request failed with HTTP status ${response.status}`) as any;
        err.status = response.status;
        throw err;
      }

      if (!response.ok || (json && json.success === false)) {
        if (response.status === 401 && typeof window !== 'undefined') {
          localStorage.removeItem('truthlens_token');
        }
        const errorMsg = json?.error?.message || json?.detail || 'An unexpected error occurred.';
        const err = new Error(errorMsg) as any;
        err.code = json?.error?.code;
        err.status = response.status;
        err.details = json?.error?.details;
        throw err;
      }

      return json.data as T;
    } catch (err: any) {
      if (!err.status && err.message?.includes('Failed to fetch')) {
        throw new Error('Could not connect to the TruthLens backend service. Please verify that the API server is running on port 8000.');
      }
      throw err;
    }
  }

  // Auth Endpoints
  async register(email: string, password: string):Promise<{ access_token: string }> {
    const data = await this.request<{ access_token: string }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    if (typeof window !== 'undefined') {
      localStorage.setItem('truthlens_token', data.access_token);
    }
    return data;
  }

  async login(email: string, password: string): Promise<{ access_token: string }> {
    const data = await this.request<{ access_token: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    if (typeof window !== 'undefined') {
      localStorage.setItem('truthlens_token', data.access_token);
    }
    return data;
  }

  logout(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('truthlens_token');
    }
  }

  async getMe(): Promise<UserProfile> {
    return this.request<UserProfile>('/auth/me');
  }

  // Analysis Endpoints
  async analyzeText(payload: { text: string; headline?: string; input_type?: string }): Promise<AnalysisResponse> {
    return this.request<AnalysisResponse>('/analysis', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async analyzeURL(url: string): Promise<AnalysisResponse> {
    return this.request<AnalysisResponse>('/analysis/url', {
      method: 'POST',
      body: JSON.stringify({ url }),
    });
  }

  async getAnalysis(id: string): Promise<AnalysisResponse> {
    return this.request<AnalysisResponse>(`/analysis/${id}`);
  }

  async deleteAnalysis(id: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/analysis/${id}`, {
      method: 'DELETE',
    });
  }

  async listAnalyses(params: {
    page?: number;
    page_size?: number;
    assessment?: string;
    input_type?: string;
    search?: string;
  } = {}): Promise<AnalysisListItem[]> {
    const query = new URLSearchParams();
    if (params.page) query.append('page', params.page.toString());
    if (params.page_size) query.append('page_size', params.page_size.toString());
    if (params.assessment) query.append('assessment', params.assessment);
    if (params.input_type) query.append('input_type', params.input_type);
    if (params.search) query.append('search', params.search);

    const qs = query.toString();
    return this.request<AnalysisListItem[]>(`/analysis${qs ? `?${qs}` : ''}`);
  }

  async submitFeedback(
    analysisId: string,
    feedback: { is_useful: boolean; feedback_category?: string; comment?: string }
  ): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/analysis/${analysisId}/feedback`, {
      method: 'POST',
      body: JSON.stringify(feedback),
    });
  }

  // Models Endpoint
  async getModels(): Promise<ModelVersionData[]> {
    return this.request<ModelVersionData[]>('/models');
  }

  // Admin Endpoints
  async getAdminAnalytics(): Promise<AnalyticsOverview> {
    return this.request<AnalyticsOverview>('/admin/analytics');
  }

  async getAdminModels(): Promise<ModelVersionData[]> {
    return this.request<ModelVersionData[]>('/admin/models');
  }

  async updateModelStatus(modelId: string, status: string): Promise<any> {
    return this.request<any>(`/admin/models/${modelId}/status`, {
      method: 'POST',
      body: JSON.stringify({ status }),
    });
  }

  async getAuditLogs(limit: number = 50): Promise<AuditLogItem[]> {
    return this.request<AuditLogItem[]>(`/admin/audit-logs?limit=${limit}`);
  }

  async getSystemHealth(): Promise<SystemHealthData> {
    return this.request<SystemHealthData>('/admin/system-health');
  }

  async getLiveHealth(): Promise<any> {
    return this.request<any>('/health/ready');
  }
}

export const api = new APIClient();
