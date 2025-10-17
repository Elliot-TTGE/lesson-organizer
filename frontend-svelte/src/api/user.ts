import type { User, Pagination } from '../types/index';
import { apiRequest } from './apiClient';
import type { QueryParams } from './apiClient';

// Define the allowed fields that can be modified
export type UserCreateFields = Required<Pick<User, 'first_name' | 'last_name' | 'email' | 'password' | 'role'>>;
export type UserUpdateFields = Pick<User, 'first_name' | 'last_name' | 'email' | 'password' | 'role' | 'last_login'>;

// Enhanced interfaces for admin functionality
export interface UsersResponse {
    users?: User[];
    pagination?: Pagination;
}

export interface UserStatsResponse {
    users: {
        total: number;
        admins: number;
        assistants: number;
        instructors: number;
    };
    lessons: {
        total: number;
    };
}

export interface UserSearchParams {
    search?: string;
    email?: string;
    role?: string;
    page?: number;
    per_page?: number;
}

function extractUserFields(user: User): UserUpdateFields {
    const { first_name, last_name, email, password, role, last_login } = user;
    return { first_name, last_name, email, password, role, last_login };
}

// Enhanced fetchUsers function that handles both paginated and simple responses
export async function fetchUsers(params: UserSearchParams = {}): Promise<User[] | UsersResponse> {
    const queryParams: QueryParams = {};
    
    if (params.search) queryParams.search = params.search;
    if (params.email) queryParams.email = params.email;
    if (params.role) queryParams.role = params.role;
    if (params.page) queryParams.page = params.page;
    if (params.per_page) queryParams.per_page = params.per_page;

    const response = await apiRequest<User[] | UsersResponse>('/users', 'GET', null, {}, queryParams);
    
    // If it's an array, return it directly for backward compatibility
    if (Array.isArray(response)) {
        return response;
    }
    
    // Otherwise return the full response with pagination
    return response;
}

export async function fetchUser(id: number): Promise<User> {
    return await apiRequest<User>(`/users/${id}`, 'GET');
}

export async function createUser(user: UserCreateFields): Promise<User> {
    const payload = {
        user
    };
    return await apiRequest<User>('/users', 'POST', payload);
}

export async function updateUser(id: number, user: Partial<UserUpdateFields> | User): Promise<User> {
    const userData = 'id' in user ? extractUserFields(user) : user;
    
    const payload = {
        user: userData
    };
    return await apiRequest<User>(`/users/${id}`, 'PUT', payload);
}

export async function deleteUser(id: number): Promise<void> {
    await apiRequest<void>(`/users/${id}`, 'DELETE');
}

export async function fetchCurrentUser(): Promise<User> {
    return await apiRequest<User>('/users/me', 'GET');
}

export async function fetchUserStats(): Promise<UserStatsResponse> {
    return await apiRequest<UserStatsResponse>('/users/stats', 'GET');
}