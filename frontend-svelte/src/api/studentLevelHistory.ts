import type { StudentLevelHistory } from '../types/index';
import { apiRequest } from './apiClient';
import type { QueryParams } from './apiClient';

export async function fetchStudentLevelHistory(params: QueryParams = {}): Promise<StudentLevelHistory[]> {
    return await apiRequest<StudentLevelHistory[]>('/student-level-history', 'GET', null, {}, params);
}

export async function createStudentLevelHistory(data: {
    student_id: number;
    level_id: number;
    start_date: string;
}): Promise<StudentLevelHistory> {
    return await apiRequest<StudentLevelHistory>('/student-level-history', 'POST', data);
}

export async function updateStudentLevelHistory(id: number, data: Partial<{
    student_id: number;
    level_id: number;
    start_date: string;
}>): Promise<StudentLevelHistory> {
    return await apiRequest<StudentLevelHistory>(`/student-level-history/${id}`, 'PUT', data);
}

export async function deleteStudentLevelHistory(id: number): Promise<void> {
    await apiRequest<void>(`/student-level-history/${id}`, 'DELETE');
}