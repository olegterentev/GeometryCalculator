import { getAuthToken } from '../auth/token'

const API_URL = 'http://127.0.0.1:8000'

type ApiOptions = {
  method?: string
  body?: unknown
  auth?: boolean
}

export async function apiFetch<T>(path: string, options: ApiOptions = {}): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }

  if (options.auth !== false) {
    const token = getAuthToken()
    if (token) {
      headers.Authorization = `Bearer ${token}`
    }
  }

  const response = await fetch(`${API_URL}${path}`, {
    method: options.method ?? 'GET',
    headers,
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
  })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    const message = typeof data.detail === 'string'
      ? data.detail
      : `Ошибка сервера: ${response.status}`
    throw new Error(message)
  }

  return response.json() as Promise<T>
}
