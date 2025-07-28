<script lang="ts">
    import type { Student } from "../../types";
    import { getPastLessonsFromStudent, getSortedLessonsFromStudent, formatLessonDateTime } from "../utils";
    import LessonCard from "./LessonCard.svelte";

    let { student } = $props<{ student: Student }>();

    // Get all lessons sorted by date (newest first)
    const allLessons = $derived(() => {
        return getSortedLessonsFromStudent(student);
    });
    
    // Get all past lessons for finding the default starting point
    const pastLessons = $derived(() => {
        return getPastLessonsFromStudent(student);
    });
    
    // Find the index of the most recent past lesson in the all lessons array
    const defaultLessonIndex = $derived(() => {
        const pastLessonsList = pastLessons();
        const allLessonsList = allLessons();
        
        if (pastLessonsList.length === 0) {
            // If no past lessons, start with the first (most recent) lesson
            return 0;
        }
        
        // Find the most recent past lesson in the all lessons array
        const mostRecentPastLesson = pastLessonsList[0];
        const index = allLessonsList.findIndex(lesson => lesson.id === mostRecentPastLesson.id);
        return index >= 0 ? index : 0;
    });
    
    // Current lesson index (starts at most recent past lesson)
    let currentLessonIndex = $state(0);
    
    // Current lesson to display
    const currentLesson = $derived(() => {
        const lessons = allLessons();
        return lessons.length > 0 && currentLessonIndex < lessons.length 
            ? lessons[currentLessonIndex] 
            : null;
    });

    // Navigation state
    const hasPrevious = $derived(() => {
        return currentLessonIndex < allLessons().length - 1;
    });
    const hasNext = $derived(() => {
        return currentLessonIndex > 0;
    });
    
    // Check if we're currently viewing the default lesson
    const isAtDefaultLesson = $derived(() => currentLessonIndex === defaultLessonIndex());

    // Navigation functions
    function goToPrevious() {
        if (hasPrevious()) {
            currentLessonIndex++;
        }
    }

    function goToNext() {
        if (hasNext()) {
            currentLessonIndex--;
        }
    }
    
    // Go back to the default lesson (most recent past lesson)
    function goToDefault() {
        currentLessonIndex = defaultLessonIndex();
    }

    // Reset to most recent past lesson when student changes
    $effect(() => {
        if (student) {
            currentLessonIndex = defaultLessonIndex();
        }
    });
</script>

<div class="card bg-base-100 text-base-content shadow-lg">
    <div class="card-body">
        <h3 class="card-title text-info">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-5 h-5 stroke-current">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            Lessons
        </h3>
        
        <!-- Lesson Navigation -->
        <div class="flex justify-between items-center mb-4">
            <button 
                class="btn btn-ghost btn-sm"
                class:btn-disabled={!hasPrevious()}
                onclick={goToPrevious}
                disabled={!hasPrevious()}
            >
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-4 h-4 stroke-current">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
                </svg>
                Previous
            </button>
            
            <div class="text-center">
                <button 
                    class="btn btn-ghost btn-sm"
                    class:text-warning={!isAtDefaultLesson()}
                    onclick={goToDefault}
                    disabled={isAtDefaultLesson()}
                    title={isAtDefaultLesson() ? "Currently viewing most recent lesson" : "Click to return to most recent lesson"}
                >
                    <div class="flex items-center gap-1">
                        {#if !isAtDefaultLesson()}
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-3 h-3 stroke-current">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                        {/if}
                        <span class="text-sm font-medium">{"Most Recent"}</span>
                    </div>
                </button>
            </div>
            
            <button 
                class="btn btn-ghost btn-sm"
                class:btn-disabled={!hasNext()}
                onclick={goToNext}
                disabled={!hasNext()}
            >
                Next
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-4 h-4 stroke-current">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                </svg>
            </button>
        </div>

        <!-- Lesson Content -->
        <div class="overflow-y-auto max-h-96">
            {#if currentLesson()}
                <!-- Use LessonCard component -->
                <LessonCard lessonId={currentLesson()!.id} />
            {:else if allLessons().length === 0}
                <div class="text-center text-base-content/60 py-8">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-12 h-12 stroke-current mb-2">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                    <p class="font-medium">No lessons found</p>
                    <p class="text-sm">This student has no lessons scheduled</p>
                </div>
            {:else}
                <div class="text-center text-base-content/60 py-4">
                    <p class="font-medium">Lesson not found</p>
                    <p class="text-sm">There was an error loading the lesson</p>
                </div>
            {/if}
        </div>
    </div>
</div>
