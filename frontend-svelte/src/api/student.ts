import type { Student, Pagination } from "../types";
import type { QueryParams } from "./apiClient";
import { apiRequest } from "./apiClient";

export type StudentCreateFields = Required<Pick<Student, 'first_name'>> & Partial<Pick<Student, 'last_name' | 'date_started' | 'classes_per_week' | 'notes_general' | 'notes_strengths' | 'notes_weaknesses' | 'notes_future'>>;
export type StudentUpdateFields = Pick<Student, 'first_name' | 'last_name' | 'date_started' | 'classes_per_week' | 'notes_general' | 'notes_strengths' | 'notes_weaknesses' | 'notes_future'>;

export interface StudentsResponse {
    students: Student[];
    pagination: Pagination;
}

function extractStudentFields(student: Student): StudentUpdateFields {
    const { first_name, last_name, date_started, classes_per_week, notes_general, notes_strengths, notes_weaknesses, notes_future } = student;
    return { first_name, last_name, date_started, classes_per_week, notes_general, notes_strengths, notes_weaknesses, notes_future };
}

export async function fetchStudents(params: QueryParams = {}): Promise<StudentsResponse> {
    return await apiRequest<StudentsResponse>('/students', 'GET', null, {}, params);
}

export async function createStudent(student: StudentCreateFields): Promise<Student> {
    const payload = {
        student
    };
    return await apiRequest<Student>('/students', 'POST', payload);
}

export async function updateStudent(id: number, student: Partial<StudentUpdateFields> | Student): Promise<Student> {
    const studentData = 'id' in student ? extractStudentFields(student) : student;
    
    const payload = {
        student: studentData
    };
    return await apiRequest<Student>(`/students/${id}`, 'PUT', payload);
}

export async function deleteStudent(id: number): Promise<void> {
    await apiRequest<void>(`/students/${id}`, 'DELETE');
}