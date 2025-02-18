import type { Quiz } from '../types/index';
import { apiRequest } from './apiClient';
import type { QueryParams } from './apiClient';

export async function fetchQuizzes(params: QueryParams = {}): Promise<Quiz[]> {
    return await apiRequest<Quiz[]>('/quizzes', 'GET', null, {}, params);
}

export async function createQuiz(quiz: Quiz): Promise<Quiz> {
    return await apiRequest<Quiz>('/quizzes', 'POST', quiz);
}