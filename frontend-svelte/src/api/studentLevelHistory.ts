import type { StudentLevelHistory } from '../types/index';
import { apiRequest } from './apiClient';
import type { QueryParams } from './apiClient';

// Define the allowed fields that can be modified
type StudentLevelHistoryCreateFields = Required<Pick<StudentLevelHistory, 'student_id' | 'level_id' | 'start_date'>>;
type StudentLevelHistoryUpdateFields = Pick<StudentLevelHistory, 'student_id' | 'level_id' | 'start_date'>;

function extractStudentLevelHistoryFields(record: StudentLevelHistory): StudentLevelHistoryUpdateFields {
    const { student_id, level_id, start_date } = record;
    return { student_id, level_id, start_date };
}

export async function fetchStudentLevelHistory(params: QueryParams = {}): Promise<StudentLevelHistory[]> {
    return await apiRequest<StudentLevelHistory[]>('/student-level-history', 'GET', null, {}, params);
}

export async function createStudentLevelHistory(record: StudentLevelHistoryCreateFields): Promise<StudentLevelHistory> {
    const payload = {
        student_level_history: record
    };
    return await apiRequest<StudentLevelHistory>('/student-level-history', 'POST', payload);
}

export async function updateStudentLevelHistory(id: number, record: Partial<StudentLevelHistoryUpdateFields> | StudentLevelHistory): Promise<StudentLevelHistory> {
    const recordData = 'id' in record ? extractStudentLevelHistoryFields(record) : record;
    
    const payload = {
        student_level_history: recordData
    };
    return await apiRequest<StudentLevelHistory>(`/student-level-history/${id}`, 'PUT', payload);
}

export async function deleteStudentLevelHistory(id: number): Promise<void> {
    await apiRequest<void>(`/student-level-history/${id}`, 'DELETE');
}