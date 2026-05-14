import { decodeJwt } from 'jose';
import type { LoginResponse, TokenPayload } from '@/types';
import { api } from '@/lib/api';

const ACCESS_TOKEN_KEY = 'epas_prototype_access_token';
const REFRESH_TOKEN_KEY = 'epas_prototype_refresh_token';

function getStorage(): Storage | null {
  if (typeof window === 'undefined') {
    return null;
  }
  return window.localStorage;
}

export function storeTokens(response: LoginResponse): void {
  const storage = getStorage();
  if (!storage) {
    return;
  }

  storage.setItem(ACCESS_TOKEN_KEY, response.access_token);
  storage.setItem(REFRESH_TOKEN_KEY, response.refresh_token);
}

export function getAccessToken(): string | null {
  return getStorage()?.getItem(ACCESS_TOKEN_KEY) ?? null;
}

export function getRefreshToken(): string | null {
  return getStorage()?.getItem(REFRESH_TOKEN_KEY) ?? null;
}

export function clearTokens(): void {
  const storage = getStorage();
  if (!storage) {
    return;
  }

  storage.removeItem(ACCESS_TOKEN_KEY);
  storage.removeItem(REFRESH_TOKEN_KEY);
}

export function decodeToken(token: string): TokenPayload {
  return decodeJwt<TokenPayload>(token);
}

export function isTokenExpired(token: string): boolean {
  try {
    const payload = decodeToken(token);
    return payload.exp * 1000 <= Date.now();
  } catch {
    return true;
  }
}

export async function refreshAccessToken(): Promise<boolean> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    return false;
  }

  try {
    const response = await api.refresh(refreshToken);
    storeTokens(response);
    return true;
  } catch {
    clearTokens();
    return false;
  }
}
