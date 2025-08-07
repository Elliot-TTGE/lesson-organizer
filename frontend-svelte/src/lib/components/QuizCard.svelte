<script lang="ts">
    import type { Student, Quiz, StudentLessonQuiz, Lesson, StudentLevelHistory } from "../../types";
    import { getSortedLessonsFromStudent, getPastLessonsFromStudent, formatLessonDateTime, formatStudentDate, getLatestLevelId } from "../utils";
    import { fetchQuizzes } from "../../api/quiz";
    import { createStudentLessonQuiz, deleteStudentLessonQuiz, fetchStudentLessonQuizzes, updateStudentLessonQuiz } from "../../api/studentLessonQuiz";
    import { onMount } from "svelte";
    import LoadingState from "./LoadingState.svelte";

    let { student } = $props<{ student: Student }>();

    // State
    let availableQuizzes = $state<Quiz[]>([]);
    let studentQuizHistory = $state<StudentLessonQuiz[]>([]);
    let isLoadingQuizzes = $state(true);
    let isLoadingHistory = $state(true);
    let isSubmitting = $state(false);
    let deletingQuizId = $state<number | null>(null);
    let editingQuizId = $state<number | null>(null);
    let isUpdatingQuiz = $state(false);
    let error = $state<string | null>(null);

    // Form state
    let selectedLessonId = $state<number | null>(null);
    let selectedQuizId = $state<number | null>(null);
    let quizScore = $state<number>(0);
    let quizNotes = $state<string>('');

    // Edit form state
    let editingScore = $state<number>(0);
    let editingNotes = $state<string>('');

    // Get lessons from student (past lessons first, most recent first)
    const studentLessons = $derived(() => {
        const pastLessons = getPastLessonsFromStudent(student);
        const allLessons = getSortedLessonsFromStudent(student);
        
        // Return past lessons first, then future lessons
        const futureLessons = allLessons.filter(lesson => 
            !pastLessons.some(pastLesson => pastLesson.id === lesson.id)
        );
        
        return [...pastLessons, ...futureLessons];
    });

    // Filter quizzes based on student's current level
    const availableQuizzesForStudent = $derived(() => {
        if (availableQuizzes.length === 0) return [];
        
        const currentLevelId = getLatestLevelId(student);
        if (!currentLevelId) return [];

        return availableQuizzes
            .filter(quiz => quiz.unit?.level.id === currentLevelId)
            .sort((a, b) => a.id - b.id);
    });

    // Get max points for selected quiz
    const maxPointsForSelectedQuiz = $derived(() => {
        if (!selectedQuizId) return 100;
        const selectedQuiz = availableQuizzes.find(quiz => quiz.id === selectedQuizId);
        return selectedQuiz?.max_points || 100;
    });

    // Enhanced quiz history with lesson and quiz details
    const enhancedQuizHistory = $derived(() => {
        return studentQuizHistory.map((quizRecord: StudentLessonQuiz) => {
            const lesson = studentLessons().find((l: Lesson) => l.id === quizRecord.lesson_id);
            const quiz = availableQuizzes.find((q: Quiz) => q.id === quizRecord.quiz_id);
            
            return {
                ...quizRecord,
                lesson,
                quiz,
                displayDate: lesson ? formatLessonDateTime(lesson) : 'Unknown Date',
                displayQuizName: quiz?.name || 'Unknown Quiz',
                displayScore: `${quizRecord.points}/${quiz?.max_points || 100}`,
                lessonDateTime: lesson ? new Date(lesson.datetime) : new Date(0) // For sorting
            };
        }).sort((a: any, b: any) => {
            // Sort by lesson date (most recent first), fallback to created_date
            const dateA = a.lessonDateTime.getTime();
            const dateB = b.lessonDateTime.getTime();
            if (dateA !== dateB) {
                return dateB - dateA; // Most recent lesson first
            }
            return new Date(b.created_date).getTime() - new Date(a.created_date).getTime();
        });
    });

    onMount(async () => {
        await Promise.all([
            loadQuizzes(),
            loadQuizHistory()
        ]);
    });

    async function loadQuizzes() {
        try {
            isLoadingQuizzes = true;
            availableQuizzes = await fetchQuizzes();
        } catch (err) {
            error = err instanceof Error ? err.message : 'Failed to load quizzes';
        } finally {
            isLoadingQuizzes = false;
        }
    }

    async function loadQuizHistory() {
        try {
            isLoadingHistory = true;
            const response = await fetchStudentLessonQuizzes({ student_id: student.id });
            studentQuizHistory = response.student_lesson_quizzes;
        } catch (err) {
            error = err instanceof Error ? err.message : 'Failed to load quiz history';
        } finally {
            isLoadingHistory = false;
        }
    }

    async function handleSubmitQuiz() {
        if (!selectedLessonId || !selectedQuizId || isSubmitting) return;

        isSubmitting = true;
        error = null;

        try {
            const newQuizRecord = await createStudentLessonQuiz({
                student_id: student.id,
                lesson_id: selectedLessonId,
                quiz_id: selectedQuizId,
                points: quizScore,
                notes: quizNotes.trim() || undefined
            });

            // Add to local history
            studentQuizHistory = [newQuizRecord, ...studentQuizHistory];

            // Reset form
            selectedLessonId = null;
            selectedQuizId = null;
            quizScore = 0;
            quizNotes = '';
        } catch (err) {
            error = err instanceof Error ? err.message : 'Failed to submit quiz';
        } finally {
            isSubmitting = false;
        }
    }

    async function handleDeleteQuiz(quizRecordId: number) {
        if (deletingQuizId) return;

        deletingQuizId = quizRecordId;
        error = null;

        try {
            await deleteStudentLessonQuiz(quizRecordId);
            studentQuizHistory = studentQuizHistory.filter(record => record.id !== quizRecordId);
        } catch (err) {
            error = err instanceof Error ? err.message : 'Failed to delete quiz record';
        } finally {
            deletingQuizId = null;
        }
    }

    function startEditingQuiz(quizRecord: StudentLessonQuiz) {
        editingQuizId = quizRecord.id;
        editingScore = quizRecord.points;
        editingNotes = quizRecord.notes || '';
    }

    function cancelEditing() {
        editingQuizId = null;
        editingScore = 0;
        editingNotes = '';
    }

    async function saveQuizEdit(quizRecord: StudentLessonQuiz) {
        if (!editingQuizId || isUpdatingQuiz) return;

        isUpdatingQuiz = true;
        error = null;

        try {
            const updatedRecord = await updateStudentLessonQuiz(editingQuizId, {
                student_id: quizRecord.student_id,
                lesson_id: quizRecord.lesson_id,
                quiz_id: quizRecord.quiz_id,
                points: editingScore,
                notes: editingNotes.trim() || undefined
            });

            // Update local history
            studentQuizHistory = studentQuizHistory.map(record => 
                record.id === editingQuizId ? updatedRecord : record
            );

            cancelEditing();
        } catch (err) {
            error = err instanceof Error ? err.message : 'Failed to update quiz record';
        } finally {
            isUpdatingQuiz = false;
        }
    }

    // Reset selected quiz when lesson changes
    $effect(() => {
        if (selectedLessonId) {
            selectedQuizId = null;
        }
    });

    // Update score bounds when quiz changes
    $effect(() => {
        if (selectedQuizId) {
            const maxPoints = maxPointsForSelectedQuiz();
            if (quizScore > maxPoints) {
                quizScore = maxPoints;
            }
        }
    });
</script>

{#if isLoadingQuizzes || isLoadingHistory}
    <LoadingState 
        isLoading={true}
        loadingText="Loading quiz information..."
    />
{:else}
    <div>
        {#if error}
            <div class="alert alert-error mb-6 shadow-lg">
                <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{error}</span>
            </div>
        {/if}

        <div class="grid grid-cols-1 xl:grid-cols-2 gap-8">
                <!-- Left Column - New Quiz Entry -->
                <div class="card bg-base-100/20 backdrop-blur-sm border border-primary-content/20 shadow-lg h-fit">
                    <div class="card-body p-6">
                        <h3 class="text-lg font-bold text-primary-content mb-4 flex items-center gap-2">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-4 h-4 stroke-current">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                            </svg>
                            Record New Quiz
                        </h3>
                        
                        <div class="gap-2">
                            <!-- Lesson, Quiz, and Score on same line -->
                            <div class="grid grid-cols-1 lg:grid-cols-12 gap-3">
                                <!-- Lesson Selector -->
                                <div class="form-control lg:col-span-5">
                                    <label class="label py-1">
                                        <span class="label-text text-primary-content font-medium text-sm">Lesson</span>
                                    </label>
                                    <select 
                                        class="select select-bordered select-primary bg-base-100 text-base-content focus:ring-2 focus:ring-primary h-10 text-sm"
                                        bind:value={selectedLessonId}
                                        disabled={isSubmitting}
                                    >
                                        <option value={null}>Select a lesson</option>
                                        {#each studentLessons() as lesson}
                                            <option value={lesson.id}>
                                                {formatLessonDateTime(lesson)}
                                            </option>
                                        {/each}
                                    </select>
                                </div>

                                <!-- Quiz Selector -->
                                <div class="form-control lg:col-span-5">
                                    <label class="label py-1">
                                        <span class="label-text text-primary-content font-medium text-sm">Quiz</span>
                                    </label>
                                    <select 
                                        class="select select-bordered select-primary bg-base-100 text-base-content focus:ring-2 focus:ring-primary h-10 text-sm"
                                        bind:value={selectedQuizId}
                                        disabled={isSubmitting || !selectedLessonId}
                                    >
                                        <option value={null}>Select a quiz</option>
                                        {#each availableQuizzesForStudent() as quiz}
                                            <option value={quiz.id}>
                                                {quiz.name}
                                            </option>
                                        {/each}
                                    </select>
                                    {#if selectedLessonId && availableQuizzesForStudent().length === 0}
                                        <label class="label py-1">
                                            <span class="label-text-alt text-warning font-medium text-xs">No quizzes available for student's current level</span>
                                        </label>
                                    {/if}
                                </div>

                                <!-- Score Input (smaller width) -->
                                <div class="form-control lg:col-span-2">
                                    <label class="label py-1">
                                        <span class="label-text text-primary-content font-medium text-sm">
                                            Score {selectedQuizId ? `(max: ${maxPointsForSelectedQuiz()})` : ''}
                                        </span>
                                    </label>
                                    <input 
                                        type="number" 
                                        class="input input-bordered input-primary bg-base-100 text-base-content focus:ring-2 focus:ring-primary h-10 text-sm"
                                        bind:value={quizScore}
                                        min="0"
                                        max={maxPointsForSelectedQuiz()}
                                        disabled={isSubmitting || !selectedQuizId}
                                        placeholder="Score"
                                    />
                                </div>
                            </div>

                            <!-- Notes Input -->
                            <fieldset class="fieldset mb-2">
                                <legend class="fieldset-legend text-primary-content font-medium text-sm -mb-2">Notes (optional)</legend>
                                <textarea 
                                    class="textarea textarea-bordered textarea-primary bg-base-100 text-base-content focus:ring-2 focus:ring-primary resize-none text-sm w-full"
                                    bind:value={quizNotes}
                                    disabled={isSubmitting}
                                    placeholder="Additional notes about the quiz..."
                                    rows="2"
                                ></textarea>
                            </fieldset>

                            <!-- Submit Button -->
                            <button 
                                class="btn btn-success w-full shadow-lg hover:shadow-xl transition-all duration-200"
                                onclick={handleSubmitQuiz}
                                disabled={isSubmitting || !selectedLessonId || !selectedQuizId}
                            >
                                {#if isSubmitting}
                                    <span class="loading loading-spinner loading-sm"></span>
                                {/if}
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-4 h-4 stroke-current">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                                </svg>
                                Record Quiz Result
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Right Column - Quiz History -->
                <div class="card bg-base-100/20 backdrop-blur-sm border border-primary-content/20 shadow-lg h-fit">
                    <div class="card-body p-3">
                        <h3 class="text-xl font-bold text-primary-content mb-3 flex items-center gap-2">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-5 h-5 stroke-current">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                            Quiz History
                        </h3>
                        
                        {#if enhancedQuizHistory().length === 0}
                            <div class="card bg-base-100/10 border border-primary-content/10">
                                <div class="card-body text-center py-8">
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-12 h-12 stroke-current text-primary-content/30 mb-3">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                    </svg>
                                    <p class="text-primary-content/70 font-medium text-base">No quiz history available</p>
                                    <p class="text-primary-content/50 text-sm">Quiz results will appear here once recorded</p>
                                </div>
                            </div>
                        {:else}
                            <div class="max-h-65 overflow-y-auto pr-2 space-y-2 scrollbar-thin scrollbar-track-base-300 scrollbar-thumb-primary">
                                {#each enhancedQuizHistory() as quizRecord}
                                    <div class="card bg-base-100/10 border border-primary-content/20 hover:bg-base-100/20 transition-all duration-200 shadow-sm">
                                        <div class="card-body p-3">
                                            {#if editingQuizId === quizRecord.id}
                                                <!-- Edit Mode -->
                                                <div>
                                                    <h4 class="font-medium text-primary-content flex items-center gap-2 text-base">
                                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-4 h-4 stroke-current">
                                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                                                        </svg>
                                                        Editing: {quizRecord.displayQuizName}
                                                    </h4>
                                                    
                                                    <div class="flex items-center mb-2">
                                                        <p class="text-sm text-primary-content/70 flex-1">
                                                            {quizRecord.displayDate}
                                                        </p>
                                                    </div>
                                                    <div class="form-control w-30">
                                                        <label class="label py-0">
                                                            <span class="label-text text-primary-content text-sm font-bold">Score (max: {quizRecord.quiz?.max_points || 100})</span>
                                                        </label>
                                                        <input 
                                                            type="number" 
                                                            class="input input-bordered input-sm bg-base-100 text-base-content"
                                                            bind:value={editingScore}
                                                            min="0"
                                                            max={quizRecord.quiz?.max_points || 100}
                                                            disabled={isUpdatingQuiz}
                                                        />
                                                    </div>
                                                    
                                                    <!-- Notes taking full width -->
                                                    <fieldset class="fieldset">
                                                        <legend class="fieldset-legend text-primary-content text-sm -mb-2">Notes</legend>
                                                        <textarea 
                                                            class="textarea textarea-bordered textarea-sm text-sm bg-base-100 text-base-content resize-none w-full"
                                                            bind:value={editingNotes}
                                                            rows="2"
                                                            disabled={isUpdatingQuiz}
                                                            placeholder="Additional notes..."
                                                        ></textarea>
                                                    </fieldset>
                                                    
                                                    <div class="flex gap-2 justify-end">
                                                        <button 
                                                            class="btn btn-xs btn-ghost"
                                                            onclick={cancelEditing}
                                                            disabled={isUpdatingQuiz}
                                                        >
                                                            Cancel
                                                        </button>
                                                        <button 
                                                            class="btn btn-xs btn-success"
                                                            onclick={() => saveQuizEdit(quizRecord)}
                                                            disabled={isUpdatingQuiz}
                                                        >
                                                            {#if isUpdatingQuiz}
                                                                <span class="loading loading-spinner loading-xs"></span>
                                                            {/if}
                                                            Save
                                                        </button>
                                                    </div>
                                                </div>
                                            {:else}
                                                <!-- View Mode -->
                                                <div class="flex-1 min-w-0">
                                                    <!-- Quiz name, score, and percentage on same line -->
                                                    <div class="flex items-center gap-2 mb-1">
                                                        <h4 class="font-medium text-primary-content text-base flex-1 truncate">
                                                            {quizRecord.displayQuizName}
                                                        </h4>
                                                        <div class="badge badge-success badge-md font-bold">
                                                            {quizRecord.displayScore}
                                                        </div>
                                                        {#if quizRecord.quiz}
                                                            <div class="text-sm text-primary-content/60 font-medium min-w-fit">
                                                                {Math.round((quizRecord.points / quizRecord.quiz.max_points) * 100)}%
                                                            </div>
                                                        {/if}
                                                        <!-- Edit and Delete buttons moved here -->
                                                        <div class="flex gap-1 flex-shrink-0">
                                                            <button 
                                                                class="btn btn-ghost btn-xs btn-square text-secondary hover:bg-info hover:text-info-content"
                                                                onclick={() => startEditingQuiz(quizRecord)}
                                                                disabled={editingQuizId !== null}
                                                                aria-label="Edit quiz record"
                                                            >
                                                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-4 h-4 stroke-current">
                                                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                                                                </svg>
                                                            </button>
                                                            <button 
                                                                class="btn btn-ghost btn-xs btn-square text-error hover:bg-error hover:text-error-content"
                                                                onclick={() => handleDeleteQuiz(quizRecord.id)}
                                                                disabled={deletingQuizId === quizRecord.id || editingQuizId !== null}
                                                                aria-label="Delete quiz record"
                                                            >
                                                                {#if deletingQuizId === quizRecord.id}
                                                                    <span class="loading loading-spinner loading-xs"></span>
                                                                {:else}
                                                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-4 h-4 stroke-current">
                                                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                                                                    </svg>
                                                                {/if}
                                                            </button>
                                                        </div>
                                                    </div>
                                                    <!-- Lesson date -->
                                                    <p class="text-sm text-primary-content/70 mb-2">
                                                        {quizRecord.displayDate}
                                                    </p>
                                                    <!-- Notes if they exist -->
                                                    {#if quizRecord.notes}
                                                        <div class="bg-base-100/20 rounded p-2 mt-1">
                                                            <p class="text-sm text-primary-content/80">
                                                                {quizRecord.notes}
                                                            </p>
                                                        </div>
                                                    {/if}
                                                </div>
                                            {/if}
                                        </div>
                                    </div>
                                {/each}
                            </div>
                        {/if}
                    </div>
                </div>
            </div>
    </div>
{/if}
