import type { Quiz } from '../types/index';
import { apiRequest } from './apiClient';
import type { QueryParams } from './apiClient';

// Define the allowed fields that can be modified
export type QuizCreateFields = Required<Pick<Quiz, 'name' | 'max_points'>> & Partial<Pick<Quiz, 'unit_id'>>;
export type QuizUpdateFields = Pick<Quiz, 'name' | 'max_points' | 'unit_id'>;

function extractQuizFields(quiz: Quiz): QuizUpdateFields {
    const { name, max_points, unit_id } = quiz;
    return { name, max_points, unit_id };
}

export async function fetchQuizzes(params: QueryParams = {}): Promise<Quiz[]> {
    return await apiRequest<Quiz[]>('/quizzes', 'GET', null, {}, params);
}

export async function createQuiz(quiz: QuizCreateFields): Promise<Quiz> {
    const payload = {
        quiz
    };
    return await apiRequest<Quiz>('/quizzes', 'POST', payload);
}

export async function updateQuiz(id: number, quiz: Partial<QuizUpdateFields> | Quiz): Promise<Quiz> {
    const quizData = 'id' in quiz ? extractQuizFields(quiz) : quiz;
    
    const payload = {
        quiz: quizData
    };
    return await apiRequest<Quiz>(`/quizzes/${id}`, 'PUT', payload);
}

export async function deleteQuiz(id: number): Promise<void> {
    await apiRequest<void>(`/quizzes/${id}`, 'DELETE');
}