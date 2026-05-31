import type { AuthUser } from '@/api/auth'

const USER_STORAGE_KEY = 'pi-agent-user-session'

export interface StoredSession {
  accessToken: string
  user: AuthUser
}

export function readStoredSession(): StoredSession | null {
  const raw = localStorage.getItem(USER_STORAGE_KEY)
  if (!raw) return null

  try {
    const parsed = JSON.parse(raw) as StoredSession
    if (!parsed.accessToken || !parsed.user?.id) return null
    return parsed
  } catch {
    return null
  }
}

export function writeStoredSession(session: StoredSession) {
  localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(session))
}

export function clearStoredSession() {
  localStorage.removeItem(USER_STORAGE_KEY)
}

export function getStoredAccessToken(): string {
  return readStoredSession()?.accessToken ?? ''
}
