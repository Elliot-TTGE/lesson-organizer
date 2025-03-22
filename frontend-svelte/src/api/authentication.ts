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
    try {
        return await apiRequest<LoginResponse>('/login', 'POST', body);
    } catch (error) {
        if (error instanceof Response) {
            switch (error.status) {
                case 400:
                    throw new Error('Bad Request: Please check your input.');
                case 401:
                    throw new Error('Unauthorized: Incorrect email or password.');
                case 404:
                    throw new Error('Not Found: The requested resource could not be found.');
                case 422:
                    throw new Error('Unprocessable Entity: Invalid data format.');
                default:
                    throw new Error('An unexpected error occurred.');
            }
        } else {
            throw new Error('An unexpected error occurred.');
        }
    }
}