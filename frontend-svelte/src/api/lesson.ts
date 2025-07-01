import type { Lesson } from "../types";
import { apiRequest } from "./apiClient";
import type { QueryParams } from "./apiClient";

export type LessonCreateFields = Required<Pick<Lesson, 'datetime'>> & Partial<Pick<Lesson, 'plan' | 'concepts' | 'notes'>>;
export type LessonUpdateFields = Pick<Lesson, 'datetime' | 'plan' | 'concepts' | 'notes'>;

function extractLessonFields(lesson: Lesson): LessonUpdateFields {
    const { datetime, plan, concepts, notes } = lesson;
    return { datetime, plan, concepts, notes };
}

export async function fetchLessons(params: QueryParams = {}): Promise<Lesson[]> {
    return await apiRequest<Lesson[]>('/lessons', 'GET', null, {}, params);
}

export async function createLesson(lesson: LessonCreateFields | Lesson, student_ids: number[] = []): Promise<Lesson> {
    const lessonData = 'id' in lesson ? extractLessonFields(lesson) : lesson;
    
    const payload = {
        lesson: lessonData,
        student_ids
    };
    return await apiRequest<Lesson>('/lessons', 'POST', payload);
}

export async function updateLesson(id: number, lesson: Partial<LessonUpdateFields> | Lesson, student_ids: number[] = []): Promise<Lesson> {
    const lessonData = 'id' in lesson ? extractLessonFields(lesson) : lesson;
    
    const payload = {
        lesson: lessonData,
        student_ids
    };
    return await apiRequest<Lesson>(`/lessons/${id}`, 'PUT', payload);
}

export async function deleteLesson(id: number): Promise<void> {
    await apiRequest<void>(`/lessons/${id}`, 'DELETE');
}