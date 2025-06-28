import type { Level } from '../types/index';
import { apiRequest } from './apiClient';
import type { QueryParams } from './apiClient';

// Define the allowed fields that can be modified
type LevelCreateFields = Required<Pick<Level, 'name' | 'curriculum_id'>>;
type LevelUpdateFields = Pick<Level, 'name' | 'curriculum_id'>;

function extractLevelFields(level: Level): LevelUpdateFields {
    const { name, curriculum_id } = level;
    return { name, curriculum_id };
}

export async function fetchLevels(params: QueryParams = {}): Promise<Level[]> {
    return await apiRequest<Level[]>('/levels', 'GET', null, {}, params);
}

export async function createLevel(level: LevelCreateFields): Promise<Level> {
    const payload = {
        level
    };
    return await apiRequest<Level>('/levels', 'POST', payload);
}

export async function updateLevel(id: number, level: Partial<LevelUpdateFields> | Level): Promise<Level> {
    const levelData = 'id' in level ? extractLevelFields(level) : level;
    
    const payload = {
        level: levelData
    };
    return await apiRequest<Level>(`/levels/${id}`, 'PUT', payload);
}

export async function deleteLevel(id: number): Promise<void> {
    await apiRequest<void>(`/levels/${id}`, 'DELETE');
}