import type { Unit } from '../types/index';
import { apiRequest } from './apiClient';
import type { QueryParams } from './apiClient';

// Define the allowed fields that can be modified
export type UnitCreateFields = Required<Pick<Unit, 'name' | 'level_id'>>;
export type UnitUpdateFields = Pick<Unit, 'name' | 'level_id'>;

function extractUnitFields(unit: Unit): UnitUpdateFields {
    const { name, level_id } = unit;
    return { name, level_id };
}

export async function fetchUnits(params: QueryParams = {}): Promise<Unit[]> {
    return await apiRequest<Unit[]>('/units', 'GET', null, {}, params);
}

export async function fetchUnit(id: number): Promise<Unit> {
    return await apiRequest<Unit>(`/units/${id}`, 'GET');
}

export async function createUnit(unit: UnitCreateFields): Promise<Unit> {
    const payload = {
        unit
    };
    return await apiRequest<Unit>('/units', 'POST', payload);
}

export async function updateUnit(id: number, unit: Partial<UnitUpdateFields> | Unit): Promise<Unit> {
    const unitData = 'id' in unit ? extractUnitFields(unit) : unit;
    
    const payload = {
        unit: unitData
    };
    return await apiRequest<Unit>(`/units/${id}`, 'PUT', payload);
}

export async function deleteUnit(id: number): Promise<void> {
    await apiRequest<void>(`/units/${id}`, 'DELETE');
}