import { apiFetch } from './http'
import type { User } from '../types/user'

type AuthResponse = {
  user: User | null
  token: string | null
  error: string
}

export async function register(
  name: string,
  email: string,
  password: string,
  age?: number,
): Promise<AuthResponse> {
  return apiFetch<AuthResponse>('/auth/register', {
    method: 'POST',
    body: { name, email, password, age },
    auth: false,
  })
}

export async function login(email: string, password: string): Promise<AuthResponse> {
  return apiFetch<AuthResponse>('/auth/login', {
    method: 'POST',
    body: { email, password },
    auth: false,
  })
}

export async function fetchMe(): Promise<{ user: User | null }> {
  return apiFetch<{ user: User | null }>('/auth/me')
}
