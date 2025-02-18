import type { Level } from '../types/index';
import { apiRequest } from './apiClient';
import type { QueryParams } from './apiClient';

export async function fetchLevels(params: QueryParams = {}): Promise<Level[]> {
    return await apiRequest<Level[]>('/levels', 'GET', null, {}, params);
}

export async function createLevel(level: Level): Promise<Level> {
    return await apiRequest<Level>('/levels', 'POST', level);
}