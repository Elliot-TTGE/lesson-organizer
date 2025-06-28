import type { User } from '../types/index';
import { apiRequest } from './apiClient';
import type { QueryParams } from './apiClient';

// Define the allowed fields that can be modified
type UserCreateFields = Required<Pick<User, 'first_name' | 'last_name' | 'email' | 'password' | 'role'>>;
type UserUpdateFields = Pick<User, 'first_name' | 'last_name' | 'email' | 'password' | 'role' | 'last_login'>;

function extractUserFields(user: User): UserUpdateFields {
    const { first_name, last_name, email, password, role, last_login } = user;
    return { first_name, last_name, email, password, role, last_login };
}

export async function fetchUsers(params: QueryParams = {}): Promise<User[]> {
    return await apiRequest<User[]>('/users', 'GET', null, {}, params);
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