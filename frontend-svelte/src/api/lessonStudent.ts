import type { LessonStudent, Pagination } from "../types";
import type { QueryParams } from "./apiClient";
import { apiRequest } from "./apiClient";

// Define the allowed fields that can be modified
export type LessonStudentCreateFields = Required<Pick<LessonStudent, 'lesson_id' | 'student_id'>>;
export type LessonStudentUpdateFields = Pick<LessonStudent, 'lesson_id' | 'student_id'>;

export interface LessonStudentsResponse {
    lesson_students: LessonStudent[];
    pagination?: Pagination;
}

function extractLessonStudentFields(lessonStudent: LessonStudent): LessonStudentUpdateFields {
    const { lesson_id, student_id } = lessonStudent;
    return { lesson_id, student_id };
}

export async function fetchLessonStudents(params: QueryParams = {}): Promise<LessonStudentsResponse> {
    return await apiRequest<LessonStudentsResponse>('/lesson-students', 'GET', null, {}, params);
}

export async function createLessonStudent(lessonStudent: LessonStudentCreateFields): Promise<LessonStudent> {
    const payload = {
        lesson_student: lessonStudent
    };
    return await apiRequest<LessonStudent>('/lesson-students', 'POST', payload);
}

export async function updateLessonStudent(id: number, lessonStudent: Partial<LessonStudentUpdateFields> | LessonStudent): Promise<LessonStudent> {
    const lessonStudentData = 'id' in lessonStudent ? extractLessonStudentFields(lessonStudent) : lessonStudent;
    
    const payload = {
        lesson_student: lessonStudentData
    };
    return await apiRequest<LessonStudent>(`/lesson-students/${id}`, 'PUT', payload);
}

export async function deleteLessonStudent(id: number): Promise<void> {
    await apiRequest<void>(`/lesson-students/${id}`, 'DELETE');
}