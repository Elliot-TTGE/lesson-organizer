import type { Lesson } from "../../types";

interface LessonState {
  lessons: Lesson[];
}

export const lessonState = $state<LessonState>({ lessons: [] });
