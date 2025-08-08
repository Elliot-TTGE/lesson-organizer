interface LessonMinimizedState {
  globalMinimized: boolean;
  individualOverrides: Record<number, boolean>; // Record of lesson IDs to their individual minimized state
}

export const lessonMinimizedState = $state<LessonMinimizedState>({
  globalMinimized: false,
  individualOverrides: {}
});

export function toggleGlobalMinimized() {
  lessonMinimizedState.globalMinimized = !lessonMinimizedState.globalMinimized;
  // Clear individual overrides when toggling global state
  lessonMinimizedState.individualOverrides = {};
}

export function toggleLessonMinimized(lessonId: number) {
  const currentlyMinimized = isLessonMinimized(lessonId);
  
  // Set individual override to opposite of current state
  lessonMinimizedState.individualOverrides = {
    ...lessonMinimizedState.individualOverrides,
    [lessonId]: !currentlyMinimized
  };
}

export function isLessonMinimized(lessonId: number): boolean {
  // If lesson has an individual override, use that
  if (lessonId in lessonMinimizedState.individualOverrides) {
    return lessonMinimizedState.individualOverrides[lessonId];
  }
  
  // Otherwise use global state
  return lessonMinimizedState.globalMinimized;
}

export function setAllLessonsMinimized(minimized: boolean) {
  lessonMinimizedState.globalMinimized = minimized;
  lessonMinimizedState.individualOverrides = {};
}
