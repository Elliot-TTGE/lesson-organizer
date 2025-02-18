import type { User } from '../types/index';
import { apiRequest } from './apiClient';
import type { QueryParams } from './apiClient';

export async function fetchUsers(params: QueryParams = {}): Promise<User[]> {
    return await apiRequest<User[]>('/users', 'GET', null, {}, params);
}

export async function createUser(user: User): Promise<User> {
    return await apiRequest<User>('/users', 'POST', user);
}