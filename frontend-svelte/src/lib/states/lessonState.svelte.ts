import type { Lesson } from "../../types";
import { isWithinOneWeek } from "$lib/utils/dateUtils";
import { lessonWeekStartDate } from "./lessonWeekStartDate.svelte";

interface LessonState {
  current: Lesson[];
}

export const lessonState = $state<LessonState>({current: [] });

export function addLessonToState(newLesson: Lesson){
  if (isWithinOneWeek(lessonWeekStartDate.current, new Date(newLesson.datetime))) {
    lessonState.current.push(newLesson);
  }
}

export function updateLessonInState(updatedLesson: Lesson) {
  if (isWithinOneWeek(lessonWeekStartDate.current, new Date(updatedLesson.datetime))) {
    lessonState.current = lessonState.current.map(lesson =>
      lesson.id === updatedLesson.id ? updatedLesson : lesson
    );
  } else {
    lessonState.current = lessonState.current.filter(lesson => lesson.id !== updatedLesson.id);
  }
}