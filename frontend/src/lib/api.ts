import type { HealthResponse, LoginRequest, LoginResponse, User } from '@/types';

const DEFAULT_API_BASE_URL = 'http://localhost:8010';
const ACCESS_TOKEN_KEY = 'epas_prototype_access_token';

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

function getApiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL ?? DEFAULT_API_BASE_URL;
}

function getStoredAccessToken(): string | null {
  if (typeof window === 'undefined') {
    return null;
  }
  return window.localStorage.getItem(ACCESS_TOKEN_KEY);
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null,
): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set('Content-Type', 'application/json');

  const bearer = token ?? getStoredAccessToken();
  if (bearer) {
    headers.set('Authorization', `Bearer ${bearer}`);
  }

  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let detail = response.statusText || 'Request failed';
    try {
      const payload = await response.json();
      detail = payload?.detail ?? detail;
    } catch {
      // fall back to status text
    }
    throw new ApiError(detail, response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export const api = {
  health: () => request<HealthResponse>('/health', { method: 'GET' }),
  login: (payload: LoginRequest) =>
    request<LoginResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  register: (payload: LoginRequest) =>
    request<LoginResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  refresh: (refresh_token: string) =>
    request<LoginResponse>('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token }),
    }),
  getCurrentUser: () => request<User>('/users/me', { method: 'GET' }),
};
