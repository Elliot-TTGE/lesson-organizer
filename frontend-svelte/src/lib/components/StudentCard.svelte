<script lang="ts">
    import { type Student } from "../../types";
    import { fetchStudent } from "../../api/student";
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

    let { studentId, onStudentUpdated } = $props<{ 
        studentId: number; 
        onStudentUpdated?: (student: Student) => void;
    }>();

    let student = $state<Student | null>(null);
    let isLoading = $state(true);
    let error = $state<string | null>(null);

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

    function handleUpdate() {
        // This would be called when student data is updated in the modal
        // For now, we'll just refresh the data
        if (student && onStudentUpdated) {
            onStudentUpdated(student);
        }
    }

    function getCurrentStatusDisplay(): string {
        if (!student) return '-';
        
        const latestStatusId = getLatestStatusId(student);
        if (!latestStatusId) {
            return '-';
        }

        return getStatusNameById(latestStatusId) ?? '-';
    }

    function getLastLessonDisplay(): string {
        if (!student) return '-';
        
        const lastLesson = getLastLessonFromStudent(student);
        return lastLesson ? formatLessonDateTime(lastLesson) : '-';
    }

    function getCurrentLevelDisplay(): string {
        if (!student) return 'Not set';
        
        const latestLevelId = getLatestLevelId(student);
        if (!latestLevelId) {
            return 'Not set';
        }

        return getLevelDisplayById(latestLevelId) ?? 'Not set';
    }
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
    <div class="card bg-gradient-to-br from-primary to-secondary text-primary-content shadow-2xl">
        <div class="card-body p-8">
            <!-- Header Section -->
            <div class="text-center mb-6">
                <h1 class="text-4xl font-bold">{getStudentFullName(student)}</h1>
            </div>

            <!-- Stats Section -->
            <div class="stats stats-vertical sm:stats-horizontal shadow-lg bg-base-100 text-base-content mb-6">
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

            <!-- Current Status and Level Dropdowns -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div class="card bg-base-100 text-base-content shadow-lg">
                    <div class="card-body">
                        <h3 class="card-title text-accent">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-5 h-5 stroke-current">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                            Current Status
                        </h3>
                        <select class="select select-bordered w-full max-w-xs" value={getLatestStatusId(student) || ''}>
                            <option value="">Select Status</option>
                            {#each statusState.statuses as status}
                                <option value={status.id}>{status.name}</option>
                            {/each}
                        </select>
                    </div>
                </div>

                <div class="card bg-base-100 text-base-content shadow-lg">
                    <div class="card-body">
                        <h3 class="card-title text-accent">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-5 h-5 stroke-current">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                            </svg>
                            Current Level & Curriculum
                        </h3>
                        <select class="select select-bordered w-full max-w-xs" value={getLatestLevelId(student) || ''}>
                            <option value="">Select Level</option>
                            {#each levelState.levels as level}
                                <option value={level.id}>{level.curriculum.name}: {level.name}</option>
                            {/each}
                        </select>
                    </div>
                </div>
            </div>

            <!-- Additional Info Cards -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div class="card bg-base-100 text-base-content shadow-lg">
                    <div class="card-body">
                        <h3 class="card-title text-info">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-5 h-5 stroke-current">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                            Last Lesson
                        </h3>
                        <p class="text-lg font-semibold">{getLastLessonDisplay()}</p>
                    </div>
                </div>
                
                <div class="card bg-base-100 text-base-content shadow-lg">
                    <div class="card-body">
                        <h3 class="card-title text-success">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-5 h-5 stroke-current">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                            </svg>
                            Classes per Week
                        </h3>
                        <p class="text-lg font-semibold">{student.classes_per_week ?? "Not Set"}</p>
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
                        <div class="max-h-48 overflow-y-auto">
                            {#if student.status_history && student.status_history.length > 0}
                                <div class="timeline timeline-vertical timeline-compact">
                                    {#each student.status_history.slice().reverse() as statusHistory, index}
                                        <li>
                                            <div class="timeline-middle">
                                                <div class="w-2 h-2 bg-info rounded-full"></div>
                                            </div>
                                            <div class="timeline-end mb-4">
                                                <div class="text-sm opacity-75">{formatStudentDate(statusHistory.changed_at)}</div>
                                                <div class="font-semibold">{getStatusNameById(statusHistory.status_id) ?? 'Unknown Status'}</div>
                                            </div>
                                        </li>
                                    {/each}
                                </div>
                            {:else}
                                <div class="text-center text-base-content/70 py-4">
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
                        <div class="max-h-48 overflow-y-auto">
                            {#if student.level_history && student.level_history.length > 0}
                                <div class="timeline timeline-vertical timeline-compact">
                                    {#each student.level_history.slice().reverse() as levelHistory, index}
                                        <li>
                                            <div class="timeline-middle">
                                                <div class="w-2 h-2 bg-success rounded-full"></div>
                                            </div>
                                            <div class="timeline-end mb-4">
                                                <div class="text-sm opacity-75">{formatStudentDate(levelHistory.start_date)}</div>
                                                <div class="font-semibold">{getLevelDisplayById(levelHistory.level_id) ?? 'Unknown Level'}</div>
                                            </div>
                                        </li>
                                    {/each}
                                </div>
                            {:else}
                                <div class="text-center text-base-content/70 py-4">
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