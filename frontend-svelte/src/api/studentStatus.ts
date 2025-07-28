import type { StudentStatus } from '../types/index';
import { apiRequest } from './apiClient';
import type { QueryParams } from './apiClient';

// Define the allowed fields that can be modified
export type StudentStatusCreateFields = Required<Pick<StudentStatus, 'name'>>;
export type StudentStatusUpdateFields = Pick<StudentStatus, 'name'>;

function extractStudentStatusFields(status: StudentStatus): StudentStatusUpdateFields {
    const { name } = status;
    return { name };
}

export async function fetchStudentStatuses(params: QueryParams = {}): Promise<StudentStatus[]> {
    return await apiRequest<StudentStatus[]>('/student-statuses', 'GET', null, {}, params);
}

export async function fetchStudentStatus(id: number): Promise<StudentStatus> {
    return await apiRequest<StudentStatus>(`/student-statuses/${id}`, 'GET');
}

export async function createStudentStatus(status: StudentStatusCreateFields): Promise<StudentStatus> {
    const payload = {
        student_status: status
    };
    return await apiRequest<StudentStatus>('/student-statuses', 'POST', payload);
}

export async function updateStudentStatus(id: number, status: Partial<StudentStatusUpdateFields> | StudentStatus): Promise<StudentStatus> {
    const statusData = 'id' in status ? extractStudentStatusFields(status) : status;
    
    const payload = {
        student_status: statusData
    };
    return await apiRequest<StudentStatus>(`/student-statuses/${id}`, 'PUT', payload);
}

export async function deleteStudentStatus(id: number): Promise<void> {
    await apiRequest<void>(`/student-statuses/${id}`, 'DELETE');
}
