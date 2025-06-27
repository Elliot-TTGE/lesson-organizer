import type { Unit } from '../types/index';
import { apiRequest } from './apiClient';
import type { QueryParams } from './apiClient';

export async function fetchUnits(params: QueryParams = {}): Promise<Unit[]> {
    return await apiRequest<Unit[]>('/units', 'GET', null, {}, params);
}