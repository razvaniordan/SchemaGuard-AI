import { apiClient } from './client';

export type LoginResponse = {
  token: string;
  tokenType: string;
};

export async function login(
  username: string,
  password: string,
): Promise<LoginResponse> {
  return apiClient<LoginResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
}