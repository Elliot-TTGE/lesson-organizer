import type { Lesson } from "../types";
import { apiRequest } from "./apiClient";
import type { QueryParams } from "./apiClient";

export async function fetchLessons(params: QueryParams = {}): Promise<Lesson[]> {
    return await apiRequest<Lesson[]>('/lessons', 'GET', null, {}, params);
}

export async function createLesson(lesson: Partial<Lesson>, student_ids: number[] = []): Promise<Lesson> {
    const payload = {
        lesson: lesson,
        student_ids: student_ids
    };
    return await apiRequest<Lesson>('/lessons', 'POST', payload);
}

export async function deleteLesson(id: number): Promise<void> {
    await apiRequest<void>(`/lessons/${id}`, 'DELETE');
}

export async function updateLesson(lesson: Lesson, student_ids: number[] = []): Promise<Lesson> {
    const payload = {
        lesson: lesson,
        student_ids: student_ids
    };
    return await apiRequest<Lesson>(`/lessons/${lesson.id}`, 'PUT', payload);
}