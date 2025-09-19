import type { UserLesson, Pagination } from "../types";
import { apiRequest } from "./apiClient";
import type { QueryParams } from "./apiClient";

export type UserLessonCreateFields = {
  lesson_id: number;
  user_id: number;
  permission_level: 'view' | 'edit' | 'manage';
};

export type UserLessonUpdateFields = {
  permission_level: 'view' | 'edit' | 'manage';
};

export interface UserLessonsResponse {
  user_lessons: UserLesson[];
  pagination?: Pagination;
}

export async function fetchUserLessons(params: QueryParams = {}): Promise<UserLessonsResponse> {
  return await apiRequest<UserLessonsResponse>('/user-lessons', 'GET', null, {}, params);
}

export async function fetchUserLesson(id: number): Promise<UserLesson> {
  return await apiRequest<UserLesson>(`/user-lessons/${id}`, 'GET');
}

export async function createUserLesson(userLesson: UserLessonCreateFields): Promise<UserLesson> {
  const payload = {
    user_lesson: userLesson
  };
  return await apiRequest<UserLesson>('/user-lessons', 'POST', payload);
}

export async function updateUserLesson(id: number, userLesson: UserLessonUpdateFields): Promise<UserLesson> {
  const payload = {
    user_lesson: userLesson
  };
  return await apiRequest<UserLesson>(`/user-lessons/${id}`, 'PUT', payload);
}

export async function deleteUserLesson(id: number): Promise<void> {
  await apiRequest<void>(`/user-lessons/${id}`, 'DELETE');
}

/**
 * Get user lesson shares for a specific lesson
 */
export async function getLessonShares(lessonId: number): Promise<UserLessonsResponse> {
  return await fetchUserLessons({ lesson_id: lessonId });
}

/**
 * Get current user's shared lessons
 */
export async function getMySharedLessons(): Promise<UserLessonsResponse> {
  return await fetchUserLessons();
}
