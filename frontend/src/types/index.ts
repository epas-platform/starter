/**
 * Shared TypeScript types for the frontend
 */

// Auth types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

// User types
export interface User {
  id: string;
  tenant_id: string;
  email: string;
  full_name: string | null;
  roles: string[];
  is_active: boolean;
  is_verified: boolean;
  last_login_at: string | null;
  created_at: string;
  updated_at: string;
}

// API Response types
export interface ApiError {
  detail: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  profile: string;
}

// Token payload (decoded JWT)
export interface TokenPayload {
  sub: string;
  email: string;
  tenant_id: string;
  roles: string[];
  type: 'access' | 'refresh';
  exp: number;
}
