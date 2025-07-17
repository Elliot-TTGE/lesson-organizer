<script lang="ts">
    import { type Student } from "../../types";
    import { fetchStudent, updateStudent } from "../../api/student";
    import { createStudentStatusHistory, deleteStudentStatusHistory } from "../../api/studentStatusHistory";
    import { createStudentLevelHistory, deleteStudentLevelHistory } from "../../api/studentLevelHistory";
    import { onMount } from "svelte";
    import { 
        getLatestLevelId, 
        getLatestStatusId, 
        getLastLessonFromStudent, 
        formatLessonDateTime, 
        getStudentFullName, 
        formatStudentDate 
    } from "../utils";
    import { 
        statusState, 
        refreshStatuses, 
        getStatusNameById,
        levelState,
        refreshLevels,
        getLevelDisplayById
    } from "../states";
    import TipexEditor from "./TipexEditor.svelte";
    import LessonCard from "./LessonCard.svelte";

    let { studentId, onStudentUpdated } = $props<{ 
        studentId: number; 
        onStudentUpdated?: (student: Student) => void;
    }>();

    let student = $state<Student | null>(null);
    let isLoading = $state(true);
    let error = $state<string | null>(null);
    let isUpdatingStatus = $state(false);
    let isUpdatingLevel = $state(false);
    let isUpdatingClassesPerWeek = $state(false);
    let deletingStatusId = $state<number | null>(null);
    let deletingLevelId = $state<number | null>(null);

    onMount(async () => {
        try {
            // Fetch student data and ensure states are loaded
            const [fetchedStudent] = await Promise.all([
                fetchStudent(studentId),
                // Ensure states are loaded (these are no-op if already loaded)
                statusState.statuses.length === 0 ? refreshStatuses() : Promise.resolve(),
                levelState.levels.length === 0 ? refreshLevels() : Promise.resolve()
            ]);
            
            student = fetchedStudent;
            
            isLoading = false;
        } catch (err) {
            error = err instanceof Error ? err.message : 'Failed to fetch student data';
            isLoading = false;
        }
    });

    async function handleStatusChange(newStatusId: number) {
        if (!student || isUpdatingStatus) return;
        
        isUpdatingStatus = true;
        try {
            // Create new status history entry
            const newStatusHistory = await createStudentStatusHistory({
                student_id: student.id,
                status_id: newStatusId,
                changed_at: new Date().toISOString()
            });

            // Update local student data
            student.status_history = [...(student.status_history || []), newStatusHistory];
            
            // Notify parent component
            if (onStudentUpdated) {
                onStudentUpdated(student);
            }
        } catch (err) {
            error = err instanceof Error ? err.message : 'Failed to update status';
        } finally {
            isUpdatingStatus = false;
        }
    }

    async function handleLevelChange(newLevelId: number) {
        if (!student || isUpdatingLevel) return;
        
        isUpdatingLevel = true;
        try {
            // Create new level history entry
            const newLevelHistory = await createStudentLevelHistory({
                student_id: student.id,
                level_id: newLevelId,
                start_date: new Date().toISOString()
            });

            // Update local student data
            student.level_history = [...(student.level_history || []), newLevelHistory];
            
            // Notify parent component
            if (onStudentUpdated) {
                onStudentUpdated(student);
            }
        } catch (err) {
            error = err instanceof Error ? err.message : 'Failed to update level';
        } finally {
            isUpdatingLevel = false;
        }
    }

    async function handleDeleteStatusHistory(statusHistoryId: number) {
        if (!student || deletingStatusId) return;
        
        deletingStatusId = statusHistoryId;
        try {
            // Delete from database
            await deleteStudentStatusHistory(statusHistoryId);

            // Update local student data by filtering out the deleted entry
            student.status_history = student.status_history?.filter(sh => sh.id !== statusHistoryId) || [];
            
            // Notify parent component
            if (onStudentUpdated) {
                onStudentUpdated(student);
            }
        } catch (err) {
            error = err instanceof Error ? err.message : 'Failed to delete status history';
        } finally {
            deletingStatusId = null;
        }
    }

    async function handleDeleteLevelHistory(levelHistoryId: number) {
        if (!student || deletingLevelId) return;
        
        deletingLevelId = levelHistoryId;
        try {
            // Delete from database
            await deleteStudentLevelHistory(levelHistoryId);

            // Update local student data by filtering out the deleted entry
            student.level_history = student.level_history?.filter(lh => lh.id !== levelHistoryId) || [];
            
            // Notify parent component
            if (onStudentUpdated) {
                onStudentUpdated(student);
            }
        } catch (err) {
            error = err instanceof Error ? err.message : 'Failed to delete level history';
        } finally {
            deletingLevelId = null;
        }
    }

    async function handleClassesPerWeekChange(newClassesPerWeek: number) {
        if (!student || isUpdatingClassesPerWeek || newClassesPerWeek < 0) return;
        
        isUpdatingClassesPerWeek = true;
        try {
            // Update student in database
            const updatedStudent = await updateStudent(student.id, {
                classes_per_week: newClassesPerWeek
            });

            // Update local student data
            student.classes_per_week = updatedStudent.classes_per_week;
            
            // Notify parent component
            if (onStudentUpdated) {
                onStudentUpdated(student);
            }
        } catch (err) {
            error = err instanceof Error ? err.message : 'Failed to update classes per week';
        } finally {
            isUpdatingClassesPerWeek = false;
        }
    }

    function handleUpdate() {
        // This would be called when student data is updated in the modal
        // For now, we'll just refresh the data
        if (student && onStudentUpdated) {
            onStudentUpdated(student);
        }
    }

    const currentStatusDisplay = $derived(() => {
        if (!student) return '-';
        
        const latestStatusId = getLatestStatusId(student);
        if (!latestStatusId) {
            return '-';
        }

        return getStatusNameById(latestStatusId) ?? '-';
    });

    const lastLessonDisplay = $derived(() => {
        if (!student) return '-';
        
        const lastLesson = getLastLessonFromStudent(student);
        return lastLesson ? formatLessonDateTime(lastLesson) : '-';
    });

    const currentLevelDisplay = $derived(() => {
        if (!student) return 'Not set';
        
        const latestLevelId = getLatestLevelId(student);
        if (!latestLevelId) {
            return 'Not set';
        }

        return getLevelDisplayById(latestLevelId) ?? 'Not set';
    });

    const latestStatusId = $derived(() => student ? getLatestStatusId(student) : null);
    const latestLevelId = $derived(() => student ? getLatestLevelId(student) : null);
</script>

{#if isLoading}
    <div class="card bg-base-200 shadow-xl">
        <div class="card-body items-center">
            <span class="loading loading-spinner loading-lg text-primary"></span>
            <p class="text-base-content/70">Loading student information...</p>
        </div>
    </div>
{:else if error}
    <div class="alert alert-error shadow-lg">
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>Error: {error}</span>
    </div>
{:else if student}
    <div class="card bg-primary text-primary-content shadow-2xl">
        <div class="card-body p-8">
            <!-- Header Section -->
            <div class="text-center mb-6">
                <a 
                    href="/students/{student.id}" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    class="text-4xl font-bold link link-hover text-primary-content hover:text-primary-content/80 transition-colors"
                >
                    {getStudentFullName(student)}
                </a>
            </div>

            <!-- Main Info Section - Two Columns -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                <!-- Left Column -->
                <div class="space-y-4">
                    <!-- Student Since -->
                    <div class="stats shadow-lg bg-base-100 text-base-content w-full">
                        <div class="stat">
                            <div class="stat-figure text-primary">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-8 h-8 stroke-current">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                                </svg>
                            </div>
                            <div class="stat-title">Student Since</div>
                            <div class="stat-value text-lg">{formatStudentDate(student.date_started)}</div>
                        </div>
                    </div>

                    <!-- Current Status and Classes per Week Row -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div class="card bg-base-100 text-base-content shadow-lg">
                            <div class="card-body text-center">
                                <h3 class="card-title text-accent justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-5 h-5 stroke-current">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                    </svg>
                                    Current Status
                                </h3>
                                <p class="text-lg font-semibold">{currentStatusDisplay()}</p>
                            </div>
                        </div>

                        <div class="card bg-base-100 text-base-content shadow-lg">
                            <div class="card-body">
                                <h3 class="card-title text-success justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-5 h-5 stroke-current">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                                    </svg>
                                    Classes per Week
                                </h3>
                                <div class="flex items-center gap-3">
                                    <button 
                                        class="btn btn-circle btn-sm btn-ghost text-error hover:bg-error hover:text-error-content disabled:text-base-content/40 disabled:bg-transparent"
                                        disabled={isUpdatingClassesPerWeek || (student.classes_per_week ?? 0) <= 0}
                                        onclick={() => student && handleClassesPerWeekChange((student.classes_per_week ?? 0) - 1)}
                                        aria-label="Decrease classes per week"
                                    >
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-4 h-4 stroke-current">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"></path>
                                        </svg>
                                    </button>
                                    <div class="flex-1 text-center">
                                        <p class="text-lg font-semibold">{student.classes_per_week ?? 0}</p>
                                    </div>
                                    <button 
                                        class="btn btn-circle btn-sm btn-ghost text-success hover:bg-success hover:text-success-content disabled:text-base-content/40 disabled:bg-transparent"
                                        disabled={isUpdatingClassesPerWeek}
                                        onclick={() => student && handleClassesPerWeekChange((student.classes_per_week ?? 0) + 1)}
                                        aria-label="Increase classes per week"
                                    >
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-4 h-4 stroke-current">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                                        </svg>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Curriculum and Level Row -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div class="card bg-base-100 text-base-content shadow-lg">
                            <div class="card-body text-center">
                                <h3 class="card-title text-accent justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-5 h-5 stroke-current">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                                    </svg>
                                    Curriculum
                                </h3>
                                <p class="text-lg font-semibold">{currentLevelDisplay().split(':')[0] ?? 'Not set'}</p>
                            </div>
                        </div>

                        <div class="card bg-base-100 text-base-content shadow-lg">
                            <div class="card-body text-center">
                                <h3 class="card-title text-accent justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-5 h-5 stroke-current">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                                    </svg>
                                    Current Level
                                </h3>
                                <p class="text-lg font-semibold">{currentLevelDisplay().split(':')[1]?.trim() ?? 'Not set'}</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Right Column - Lessons -->
                <div class="card bg-base-100 text-base-content shadow-lg">
                    <div class="card-body">
                        <h3 class="card-title text-info">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-5 h-5 stroke-current">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                            Lessons
                        </h3>
                        
                        <!-- Lesson Navigation -->
                        <div class="flex justify-between items-center">
                            <button class="btn btn-ghost btn-sm" disabled>
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-4 h-4 stroke-current">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
                                </svg>
                                Previous
                            </button>
                            <span class="text-sm font-medium">Most Recent</span>
                            <button class="btn btn-ghost btn-sm" disabled>
                                Next
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-4 h-4 stroke-current">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                                </svg>
                            </button>
                        </div>

                        <!-- Lesson Content -->
                        <div class="bg-base-200 p-4 rounded-lg overflow-y-auto max-h-[38vh]">
                            {#if student.lessons && student.lessons.length > 0}
                                {@const lastLesson = getLastLessonFromStudent(student)}
                                {#if lastLesson}
                                    <!-- Use LessonCard component -->
                                    <LessonCard lesson={lastLesson} />
                                {:else}
                                    <div class="text-center text-base-content/60 py-4">
                                        <p class="font-medium">No past lessons found</p>
                                        <p class="text-sm">This student has no completed lessons</p>
                                    </div>
                                {/if}
                            {:else}
                                <div class="text-center text-base-content/60 py-8">
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-12 h-12 stroke-current mb-2">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                                    </svg>
                                    <p class="font-medium">No lessons found</p>
                                    <p class="text-sm">This student is not part of any lessons</p>
                                </div>
                            {/if}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Quiz Results Section -->
            <div class="card bg-base-100/10 backdrop-blur-sm border border-primary-content/20 mb-6">
                <div class="card-body">
                    <h2 class="card-title text-warning">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-6 h-6 stroke-current">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        Quiz Results
                    </h2>
                    <div class="alert alert-info">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        <span>Quiz functionality will be implemented here. This section is reserved for entering and displaying quiz results.</span>
                    </div>
                </div>
            </div>

            <!-- Notes Section -->
            <div class="divider text-primary-content/70">
                <span class="text-lg font-semibold">Student Notes</span>
            </div>
            
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="space-y-4">
                    <div class="card bg-base-100/10 backdrop-blur-sm border border-primary-content/20">
                        <div class="card-body p-4">
                            <TipexEditor heading="General Notes" bind:body={student.notes_general}></TipexEditor>
                        </div>
                    </div>
                    <div class="card bg-base-100/10 backdrop-blur-sm border border-primary-content/20">
                        <div class="card-body p-4">
                            <TipexEditor heading="Future Plans" bind:body={student.notes_future}></TipexEditor>
                        </div>
                    </div>
                </div>
                <div class="space-y-4">
                    <div class="card bg-base-100/10 backdrop-blur-sm border border-primary-content/20">
                        <div class="card-body p-4">
                            <TipexEditor heading="Strengths" bind:body={student.notes_strengths}></TipexEditor>
                        </div>
                    </div>
                    <div class="card bg-base-100/10 backdrop-blur-sm border border-primary-content/20">
                        <div class="card-body p-4">
                            <TipexEditor heading="Areas of Improvement" bind:body={student.notes_weaknesses}></TipexEditor>
                        </div>
                    </div>
                </div>
            </div>

            <!-- History Section -->
            <div class="divider text-primary-content/70">
                <span class="text-lg font-semibold">Student History</span>
            </div>
            
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="card bg-base-100/10 backdrop-blur-sm border border-primary-content/20">
                    <div class="card-body">
                        <h3 class="card-title text-info">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-5 h-5 stroke-current">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                            Status History
                        </h3>
                        
                        <!-- Change Status Dropdown -->
                        <div class="mb-4">
                            <label class="label" for="status-select">
                                <span class="label-text text-base-content font-medium">Change Status:</span>
                            </label>
                            <select 
                                id="status-select"
                                class="select select-bordered w-full"
                                disabled={isUpdatingStatus}
                                onchange={(e) => {
                                    const newStatusId = parseInt(e.currentTarget.value);
                                    if (student && newStatusId && newStatusId !== latestStatusId()) {
                                        handleStatusChange(newStatusId);
                                    }
                                    e.currentTarget.value = ''; // Reset dropdown
                                }}
                            >
                                <option value="">Select New Status</option>
                                {#each statusState.statuses as status}
                                    <option value={status.id} disabled={student && status.id === latestStatusId()}>
                                        {status.name}
                                    </option>
                                {/each}
                            </select>
                            {#if isUpdatingStatus}
                                <span class="loading loading-spinner loading-sm ml-2"></span>
                            {/if}
                        </div>

                        <!-- Status History List -->
                        <div class="max-h-64 overflow-y-auto overflow-x-hidden">
                            {#if student.status_history && student.status_history.length > 0}
                                <div class="timeline timeline-vertical timeline-compact">
                                    {#each student.status_history.slice().reverse() as statusHistory, index}
                                        <li>
                                            <div class="timeline-middle">
                                                <div class="w-2 h-2 bg-info rounded-full"></div>
                                            </div>
                                            <div class="timeline-end mb-4 flex justify-between items-center w-full">
                                                <div class="flex-1">
                                                    <div class="text-sm text-base-content/80 font-medium">{formatStudentDate(statusHistory.changed_at)}</div>
                                                    <div class="font-semibold text-base-content">{getStatusNameById(statusHistory.status_id) ?? 'Unknown Status'}</div>
                                                </div>
                                                <button 
                                                    class="btn btn-ghost btn-xs text-error hover:bg-error hover:text-error-content flex-shrink-0 mr-2"
                                                    disabled={deletingStatusId === statusHistory.id}
                                                    onclick={() => handleDeleteStatusHistory(statusHistory.id)}
                                                    aria-label="Delete status history entry"
                                                >
                                                    {#if deletingStatusId === statusHistory.id}
                                                        <span class="loading loading-spinner loading-xs"></span>
                                                    {:else}
                                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                                                        </svg>
                                                    {/if}
                                                </button>
                                            </div>
                                        </li>
                                    {/each}
                                </div>
                            {:else}
                                <div class="text-center text-base-content/60 py-4">
                                    No status history available
                                </div>
                            {/if}
                        </div>
                    </div>
                </div>
                
                <div class="card bg-base-100/10 backdrop-blur-sm border border-primary-content/20">
                    <div class="card-body">
                        <h3 class="card-title text-success">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-5 h-5 stroke-current">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                            </svg>
                            Level History
                        </h3>
                        
                        <!-- Change Level Dropdown -->
                        <div class="mb-4">
                            <label class="label" for="level-select">
                                <span class="label-text text-base-content font-medium">Change Level:</span>
                            </label>
                            <select 
                                id="level-select"
                                class="select select-bordered w-full"
                                disabled={isUpdatingLevel}
                                onchange={(e) => {
                                    const newLevelId = parseInt(e.currentTarget.value);
                                    if (student && newLevelId && newLevelId !== latestLevelId()) {
                                        handleLevelChange(newLevelId);
                                    }
                                    e.currentTarget.value = ''; // Reset dropdown
                                }}
                            >
                                <option value="">Select New Level</option>
                                {#each levelState.levels as level}
                                    <option value={level.id} disabled={student && level.id === latestLevelId()}>
                                        {level.curriculum.name}: {level.name}
                                    </option>
                                {/each}
                            </select>
                            {#if isUpdatingLevel}
                                <span class="loading loading-spinner loading-sm ml-2"></span>
                            {/if}
                        </div>

                        <!-- Level History List -->
                        <div class="max-h-64 overflow-y-auto overflow-x-hidden">
                            {#if student.level_history && student.level_history.length > 0}
                                <div class="timeline timeline-vertical timeline-compact">
                                    {#each student.level_history.slice().reverse() as levelHistory, index}
                                        <li>
                                            <div class="timeline-middle">
                                                <div class="w-2 h-2 bg-success rounded-full"></div>
                                            </div>
                                            <div class="timeline-end mb-4 flex justify-between items-center w-full">
                                                <div class="flex-1">
                                                    <div class="text-sm text-base-content/80 font-medium">{formatStudentDate(levelHistory.start_date)}</div>
                                                    <div class="font-semibold text-base-content">{getLevelDisplayById(levelHistory.level_id) ?? 'Unknown Level'}</div>
                                                </div>
                                                <button 
                                                    class="btn btn-ghost btn-xs text-error hover:bg-error hover:text-error-content flex-shrink-0 mr-2"
                                                    disabled={deletingLevelId === levelHistory.id}
                                                    onclick={() => handleDeleteLevelHistory(levelHistory.id)}
                                                    aria-label="Delete level history entry"
                                                >
                                                    {#if deletingLevelId === levelHistory.id}
                                                        <span class="loading loading-spinner loading-xs"></span>
                                                    {:else}
                                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                                                        </svg>
                                                    {/if}
                                                </button>
                                            </div>
                                        </li>
                                    {/each}
                                </div>
                            {:else}
                                <div class="text-center text-base-content/60 py-4">
                                    No level history available
                                </div>
                            {/if}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
{/if}