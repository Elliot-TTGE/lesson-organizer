import { apiRequest } from './apiClient';

interface LoginResponse {
    access_token: string;
}

interface LoginRequest {
    email: string;
    password: string;
}

export async function login(email: string, password: string): Promise<LoginResponse> {
    const body: LoginRequest = { email, password };
    return apiRequest<LoginResponse>('/login', 'POST', body);
}