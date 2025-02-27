import type { Lesson } from "../../types";
import { isWithinOneWeek } from "$lib/utils/dateUtils";
import { lessonWeekStartDate } from "./lessonWeekStartDate.svelte";

interface LessonState {
  lessons: Lesson[];
}

export const lessonState = $state<LessonState>({ lessons: [] });

export function addLessonToState(newLesson: Lesson){
  if (isWithinOneWeek(lessonWeekStartDate.current, new Date(newLesson.datetime))) {
    lessonState.lessons.push(newLesson);
  }
}

export function updateLessonInState(updatedLesson: Lesson) {
  if (isWithinOneWeek(lessonWeekStartDate.current, new Date(updatedLesson.datetime))) {
    lessonState.lessons = lessonState.lessons.map(lesson =>
      lesson.id === updatedLesson.id ? updatedLesson : lesson
    );
  } else {
    lessonState.lessons = lessonState.lessons.filter(lesson => lesson.id !== updatedLesson.id);
  }
}