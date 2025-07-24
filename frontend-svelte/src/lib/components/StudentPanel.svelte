<script lang="ts">
    import { type Student, type StudentLevelHistory, type StudentStatusHistory } from "../../types";
    import StudentCard from "./StudentCard.svelte";
    import StudentCreateModal from "./StudentCreateModal.svelte";
    import { fetchStudents } from "../../api/student";
    import { onMount } from "svelte";
    import { 
        getLatestLevelId, 
        getLatestStatusId, 
        getLastLessonFromStudent, 
        getNextLessonFromStudent, 
        formatLessonDateTime 
    } from "../utils/studentUtils";
    import {
        statusState,
        refreshStatuses,
        getStatusNameById,
        levelState,
        refreshLevels,
        getLevelDisplayById,
        getLevelsByCurriculumId,
        curriculumState,
        refreshCurriculums,
        getCurriculumNameById
    } from "../states";

    let students = $state<Student[]>([]);
    let isLoading = $state(true);
    let error = $state<string | null>(null);

    let showModal = $state(false);
    let selectedStudent = $state<number | null>(null);

    // Search and filter state
    let searchTerm = $state('');
    let statusFilter = $state<number | null>(null);
    let levelFilter = $state<number | null>(null);
    let sortByRecentLessons = $state(false);

    function openModal(student: Student) {
        showModal = true;
        selectedStudent = student.id;
    }

    function closeModal() {
        showModal = false;
        selectedStudent = null;
    }

    async function handleStudentUpdated(updatedStudent: Student) {
        // Refresh the students list to reflect any changes that might affect filtering
        await loadStudents();
    }

    function handleStudentCreated(newStudent: Student, status_history: StudentStatusHistory[], level_history: StudentLevelHistory[]) {
        // Refresh the students list to include the new student with proper filtering
        loadStudents();
        
        // Close any existing modals
        closeModal();
        
        // Open the StudentCard modal for the new student
        showModal = true;
        selectedStudent = newStudent.id;
    }

    function getCurrentLevel(student: Student): string {
        const latestLevelId = getLatestLevelId(student);
        if (!latestLevelId) {
            return '-';
        }

        return getLevelDisplayById(latestLevelId) ?? '-';
    }

    function getLastLesson(student: Student): string {
        const lastLesson = getLastLessonFromStudent(student);
        return lastLesson ? formatLessonDateTime(lastLesson) : '-';
    }

    function getNextLesson(student: Student): string {
        const nextLesson = getNextLessonFromStudent(student);
        return nextLesson ? formatLessonDateTime(nextLesson) : '-';
    }

    function getCurrentStatus(student: Student): string {
        const latestStatusId = getLatestStatusId(student);
        if (!latestStatusId) {
            return '-';
        }

        return getStatusNameById(latestStatusId) ?? '-';
    }

    async function loadStudents() {
        isLoading = true;
        error = null;
        
        try {
            const params: Record<string, any> = {};
            
            // Add search filter
            if (searchTerm.trim()) {
                params.search = searchTerm.trim();
            }
            
            // Add status filter
            if (statusFilter) {
                const statusName = getStatusNameById(statusFilter);
                if (statusName) {
                    params.status = statusName;
                }
            }
            
            // Add level filter
            if (levelFilter) {
                const levelName = levelState.levels.find(l => l.id === levelFilter)?.name;
                if (levelName) {
                    params.level = levelName;
                }
            }
            
            // Note: sortByRecentLessons is handled client-side in the $effect below
            // to ensure all students are shown, just sorted differently
            
            const response = await fetchStudents(params);
            let fetchedStudents = response.students;
            
            students = fetchedStudents;
        } catch (err) {
            error = err instanceof Error ? err.message : 'Failed to fetch students';
        } finally {
            isLoading = false;
        }
    }

    function clearFilters() {
        searchTerm = '';
        statusFilter = null;
        levelFilter = null;
        sortByRecentLessons = false;
        loadStudents();
    }

    // Sort by most recent lessons if requested (client-side for now)
    $effect(() => {
        if (sortByRecentLessons && students.length > 0) {
            students.sort((a, b) => {
                const lastLessonA = getLastLessonFromStudent(a);
                const lastLessonB = getLastLessonFromStudent(b);
                
                if (!lastLessonA && !lastLessonB) return 0;
                if (!lastLessonA) return 1;
                if (!lastLessonB) return -1;
                
                return new Date(lastLessonB.datetime).getTime() - new Date(lastLessonA.datetime).getTime();
            });
        }
    });

    // Debounced search for text input
    let searchTimeout: number;
    function handleSearchInput() {
        if (searchTimeout) {
            clearTimeout(searchTimeout);
        }
        searchTimeout = setTimeout(() => {
            loadStudents();
        }, 300);
    }

    // Handle filter changes
    function handleFilterChange() {
        loadStudents();
    }

    onMount(async () => {
        try {
            // Fetch all data in parallel
            await Promise.all([
                refreshLevels(),
                refreshStatuses(),
                refreshCurriculums()
            ]);
            // Load students after all reference data is loaded
            await loadStudents();
        } catch (err) {
            error = err instanceof Error ? err.message : 'Failed to fetch data';
            isLoading = false;
        }
    });
</script>

<div class="sticky z-10 mt-16 top-16 bg-base-100">
    <div class="flex bg-gradient-to-r from-base-100 to-base-200 mb-0 gap-3 p-6 justify-between items-end">
        <!-- Left side: Search and Filters -->
        <div class="flex gap-3 items-end flex-wrap">
            <!-- Search -->
            <fieldset class="fieldset bg-base-100 shadow-sm border border-secondary rounded-lg p-3 flex-1 min-w-80">
                <legend class="fieldset-legend text-accent font-semibold text-sm px-2">Find a student</legend>
                <label class="input input-bordered input-accent flex items-center gap-2 bg-base-100 hover:bg-base-50 transition-colors">
                    <svg class="h-4 w-4 opacity-60 text-accent" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="11" cy="11" r="8"></circle>
                        <path d="m21 21-4.3-4.3"></path>
                    </svg>
                    <input type="search" placeholder="Search by name..." class="grow" bind:value={searchTerm} oninput={handleSearchInput}/>
                </label>
            </fieldset>

            <!-- Status Filter -->
            <fieldset class="fieldset bg-base-100 shadow-sm border border-secondary rounded-lg p-3">
                <legend class="fieldset-legend text-accent font-semibold text-sm px-2">Status</legend>
                <select class="select select-bordered select-accent bg-base-100 hover:bg-base-50 transition-colors min-w-32" bind:value={statusFilter} onchange={handleFilterChange}>
                    <option value={null}>All Statuses</option>
                    {#each statusState.statuses as status (status.id)}
                        <option value={status.id}>{status.name}</option>
                    {/each}
                </select>
            </fieldset>

            <!-- Level Filter -->
            <fieldset class="fieldset bg-base-100 shadow-sm border border-secondary rounded-lg p-3">
                <legend class="fieldset-legend text-accent font-semibold text-sm px-2">Level</legend>
                <select class="select select-bordered select-accent bg-base-100 hover:bg-base-50 transition-colors min-w-48" bind:value={levelFilter} onchange={handleFilterChange}>
                    <option value={null}>All Levels</option>
                    {#each levelState.levels as level (level.id)}
                        <option value={level.id}>{level.curriculum?.name || 'Unknown'}: {level.name}</option>
                    {/each}
                </select>
            </fieldset>

            <!-- Sort by recent lessons -->
            <div class="bg-base-100 shadow-sm border border-secondary rounded-lg p-3 hover:bg-base-50 transition-colors">
                <label class="label cursor-pointer justify-start gap-3 m-0 p-0">
                    <input type="checkbox" class="checkbox checkbox-accent checkbox-sm" bind:checked={sortByRecentLessons} onchange={handleFilterChange} />
                    <span class="label-text text-sm font-medium text-accent">Sort by recent lessons</span>
                </label>
            </div>
            
            <!-- Clear All button -->
            <button class="btn btn-outline btn-warning btn-sm shadow-sm hover:shadow-md transition-all duration-200 font-medium" onclick={clearFilters}>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
                Clear All
            </button>
        </div>

        <!-- Right side: New Student Button -->
        <div class="flex items-end">
            <StudentCreateModal onStudentCreated={handleStudentCreated}>New Student</StudentCreateModal>
        </div>
    </div>

    <div class="overflow-y-auto" style="max-height: calc(100vh - 12rem); padding-bottom: 2rem;">
        <table class="table border bg-base-200 border-base-200">
            <thead class="sticky top-0 z-10 bg-base-200">
                <tr>
                    <th>Name</th>
                    <th>Level</th>
                    <th>Status</th>
                    <th>Next Lesson</th>
                    <th>Last Lesson</th>
                    <th>Last Quiz</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody class="table-zebra">
                {#if isLoading || statusState.isLoading || levelState.isLoading || curriculumState.isLoading}
                    <tr>
                        <td colspan="7" class="text-center p-8">
                            <span class="loading loading-spinner loading-lg"></span>
                        </td>
                    </tr>
                {:else if error || statusState.error || levelState.error || curriculumState.error}
                    <tr>
                        <td colspan="7" class="p-4">
                            <div class="alert alert-error">
                                <span>Error: {error || statusState.error || levelState.error || curriculumState.error}</span>
                            </div>
                        </td>
                    </tr>
                {:else if students.length === 0}
                    <tr>
                        <td colspan="7" class="text-center p-8">
                            <div class="alert alert-info">
                                <span>No students found matching your criteria.</span>
                            </div>
                        </td>
                    </tr>
                {:else}
                    {#each students as student (student.id)}
                        <tr class="hover">
                            <td>{student.first_name} {student.last_name || ''}</td>
                            <td>{getCurrentLevel(student)}</td>
                            <td>{getCurrentStatus(student)}</td>
                            <td>{getNextLesson(student)}</td>
                            <td>{getLastLesson(student)}</td>
                            <td>-</td> <!-- TODO: Add last quiz logic -->
                            <td>
                                <button class="btn btn-primary btn-sm" onclick={() => openModal(student)}>Edit</button>
                            </td>
                        </tr>
                    {/each}
                {/if}
            </tbody>
        </table>
    </div>
</div>

{#if showModal}
    <dialog open class="modal modal-middle">
        <div class="modal-box max-w-[95vw] h-[95vh] p-0 bg-transparent shadow-none overflow-y-auto">
            <div class="absolute top-4 right-4 z-20">
                <button class="btn btn-circle btn-ghost bg-base-100/80 backdrop-blur-sm" onclick={closeModal} aria-label="Close modal">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
            <div>
                {#if selectedStudent}
                    <StudentCard studentId={selectedStudent} onStudentUpdated={handleStudentUpdated} />
                {/if}
            </div>
        </div>
        <form method="dialog" class="modal-backdrop">
            <button onclick={closeModal}>close</button>
        </form>
    </dialog>
{/if}