import type { StudentLessonQuiz } from '../types/index';
import { apiRequest } from './apiClient';
import type { QueryParams } from './apiClient';

// Define the allowed fields that can be modified
export type StudentLessonQuizCreateFields = Required<Pick<StudentLessonQuiz, 'student_id' | 'lesson_id'>> & Partial<Pick<StudentLessonQuiz, 'quiz_id' | 'points' | 'notes'>>;
export type StudentLessonQuizUpdateFields = Pick<StudentLessonQuiz, 'student_id' | 'lesson_id' | 'quiz_id' | 'points' | 'notes'>;

function extractStudentLessonQuizFields(record: StudentLessonQuiz): StudentLessonQuizUpdateFields {
    const { student_id, lesson_id, quiz_id, points, notes } = record;
    return { student_id, lesson_id, quiz_id, points, notes };
}

export async function fetchStudentLessonQuizzes(params: QueryParams = {}): Promise<StudentLessonQuiz[]> {
    return await apiRequest<StudentLessonQuiz[]>('/student-lesson-quizzes', 'GET', null, {}, params);
}

export async function createStudentLessonQuiz(record: StudentLessonQuizCreateFields): Promise<StudentLessonQuiz> {
    const payload = {
        student_lesson_quiz: record
    };
    return await apiRequest<StudentLessonQuiz>('/student-lesson-quizzes', 'POST', payload);
}

export async function updateStudentLessonQuiz(id: number, record: Partial<StudentLessonQuizUpdateFields> | StudentLessonQuiz): Promise<StudentLessonQuiz> {
    const recordData = 'id' in record ? extractStudentLessonQuizFields(record) : record;
    
    const payload = {
        student_lesson_quiz: recordData
    };
    return await apiRequest<StudentLessonQuiz>(`/student-lesson-quizzes/${id}`, 'PUT', payload);
}

export async function deleteStudentLessonQuiz(id: number): Promise<void> {
    await apiRequest<void>(`/student-lesson-quizzes/${id}`, 'DELETE');
}
