import type { StudentStatusHistory, Pagination } from '../types/index';
import { apiRequest } from './apiClient';
import type { QueryParams } from './apiClient';

// Define the allowed fields that can be modified
export type StudentStatusHistoryCreateFields = Required<Pick<StudentStatusHistory, 'student_id' | 'status_id' | 'changed_at'>>;
export type StudentStatusHistoryUpdateFields = Pick<StudentStatusHistory, 'student_id' | 'status_id' | 'changed_at'>;

export interface StudentStatusHistoryResponse {
    student_status_history: StudentStatusHistory[];
    pagination?: Pagination;
}

function extractStudentStatusHistoryFields(record: StudentStatusHistory): StudentStatusHistoryUpdateFields {
    const { student_id, status_id, changed_at } = record;
    return { student_id, status_id, changed_at };
}

export async function fetchStudentStatusHistory(params: QueryParams = {}): Promise<StudentStatusHistoryResponse> {
    return await apiRequest<StudentStatusHistoryResponse>('/student-status-history', 'GET', null, {}, params);
}

export async function createStudentStatusHistory(record: StudentStatusHistoryCreateFields): Promise<StudentStatusHistory> {
    const payload = {
        student_status_history: record
    };
    return await apiRequest<StudentStatusHistory>('/student-status-history', 'POST', payload);
}

export async function updateStudentStatusHistory(id: number, record: Partial<StudentStatusHistoryUpdateFields> | StudentStatusHistory): Promise<StudentStatusHistory> {
    const recordData = 'id' in record ? extractStudentStatusHistoryFields(record) : record;
    
    const payload = {
        student_status_history: recordData
    };
    return await apiRequest<StudentStatusHistory>(`/student-status-history/${id}`, 'PUT', payload);
}

export async function deleteStudentStatusHistory(id: number): Promise<void> {
    await apiRequest<void>(`/student-status-history/${id}`, 'DELETE');
}
