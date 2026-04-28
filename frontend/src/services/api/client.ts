const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '';

type ApiClientOptions = RequestInit & {
  headers?: Record<string, string>;
};

export async function apiClient<TResponse>(
  path: string,
  options: ApiClientOptions = {},
): Promise<TResponse> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    let errorMessage = `Request failed with status ${response.status}`;

    try {
      const errorBody = await response.json();
      errorMessage = errorBody.message ?? errorMessage;
    } catch {
      // Keep default error message if response body is not JSON.
    }

    throw new Error(errorMessage);
  }

  if (response.status === 204) {
    return undefined as TResponse;
  }

  return response.json() as Promise<TResponse>;
}