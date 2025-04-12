import type { Lesson } from "../../types";
import { isWithinOneWeek } from "$lib/utils/dateUtils";
import { lessonWeekStartDate } from "./lessonWeekStartDate.svelte";
import { fetchLessons } from "../../api/lesson";

interface LessonState {
  current: Lesson[][];
}

export const lessonState = $state<LessonState>({ current: Array(7).fill(null).map(() => []) });

function sortLessonsByDatetime(lessons: Lesson[]): Lesson[] {
  return lessons.sort((a, b) => new Date(a.datetime).getTime() - new Date(b.datetime).getTime());
}

export function addLessonToState(newLesson: Lesson) {
  if (isWithinOneWeek(lessonWeekStartDate.current, new Date(newLesson.datetime))) {
    const dayIndex = new Date(newLesson.datetime).getDay();
    lessonState.current[dayIndex].push(newLesson);
    lessonState.current[dayIndex] = sortLessonsByDatetime(lessonState.current[dayIndex]);
  }
}

export function updateLessonInState(updatedLesson: Lesson) {
  const newDayIndex = new Date(updatedLesson.datetime).getDay();

  // Remove the lesson from its original day
  lessonState.current.forEach((lessons, index) => {
    lessonState.current[index] = lessons.filter(lesson => lesson.id !== updatedLesson.id);
  });

  // Add the updated lesson to the new day
  if (isWithinOneWeek(lessonWeekStartDate.current, new Date(updatedLesson.datetime))) {
    lessonState.current[newDayIndex].push(updatedLesson);
    lessonState.current[newDayIndex] = sortLessonsByDatetime(lessonState.current[newDayIndex]);
  }
}

export function removeLessonFromState(lessonId: number) {
  lessonState.current.forEach((lessons, index) => {
    const updatedLessons = lessons.filter(lesson => lesson.id !== lessonId);
    lessonState.current[index] = sortLessonsByDatetime(updatedLessons);
  });
}

export async function fetchCurrentWeekLessons() {
  try {
    const date = lessonWeekStartDate.current;
    const newLessons = await fetchLessons({ "initial_date": date.toISOString() });
    const lessonsArray: Lesson[][] = Array(7).fill(null).map(() => []);

    newLessons.forEach((lesson: Lesson) => {
      const dayIndex = new Date(lesson.datetime).getDay();
      lessonsArray[dayIndex].push(lesson);
    });

    lessonState.current = lessonsArray.map(sortLessonsByDatetime);
  } catch (error) {
    console.error("Error fetching lessons:", error);
  }
}