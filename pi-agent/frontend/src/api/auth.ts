import request from './request'

export interface AuthUser {
  id: number
  phone: string
  created_at: string
}

export interface AuthTokenResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: AuthUser
}

export interface SendCodeResponse {
  message: string
  expire_seconds: number
  debug_code?: string
}

export const sendLoginCode = (phone: string) =>
  request.post<SendCodeResponse>('/auth/send-code', { phone })

export const loginByCode = (phone: string, code: string) =>
  request.post<AuthTokenResponse>('/auth/login-by-code', { phone, code })

export const getCurrentUser = () => request.get<AuthUser>('/auth/me')

export const logoutAuth = () => request.post('/auth/logout')
