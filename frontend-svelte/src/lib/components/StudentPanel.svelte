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
        curriculumState,
        refreshCurriculums
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
    
    // Sorting state
    type SortField = 'name' | 'level' | 'status' | 'nextLesson' | 'lastLesson' | 'lastQuiz';
    type SortDirection = 'asc' | 'desc';
    
    let sortField = $state<SortField>('lastLesson');
    let sortDirection = $state<SortDirection>('desc');
    
    // Status cycling order for status sorting
    const statusCycleOrder = ['active', 'trial', 'future', 'hold', 'inactive'];
    let statusSortCycle = $state(0); // Track which status to prioritize

    function getStatusSortValue(statusName: string, cycle: number): number {
        const normalizedStatus = statusName.toLowerCase();
        const baseIndex = statusCycleOrder.indexOf(normalizedStatus);
        
        if (baseIndex === -1) return 999; // Unknown statuses go to end
        
        // Rotate the order based on current cycle
        const rotatedIndex = (baseIndex - cycle + statusCycleOrder.length) % statusCycleOrder.length;
        return rotatedIndex;
    }

    // Helper function to handle empty value sorting (always puts empty values at bottom)
    function compareWithEmptyHandling(
        valueA: any, 
        valueB: any, 
        isEmpty: (val: any) => boolean, 
        compare: (a: any, b: any) => number
    ): { comparison: number; hasEmpty: boolean } {
        const emptyA = isEmpty(valueA);
        const emptyB = isEmpty(valueB);
        
        if (emptyA && emptyB) return { comparison: 0, hasEmpty: true };
        if (emptyA) return { comparison: 1, hasEmpty: true }; // Empty always goes to end
        if (emptyB) return { comparison: -1, hasEmpty: true }; // Empty always goes to end
        
        return { comparison: compare(valueA, valueB), hasEmpty: false };
    }

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

    function handleSort(field: SortField) {
        if (sortField === field) {
            if (field === 'status') {
                // For status, cycle through the status priority order
                statusSortCycle = (statusSortCycle + 1) % statusCycleOrder.length;
            } else {
                // If clicking the same field, toggle direction
                sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
            }
        } else {
            // If clicking a new field, set it and use appropriate default direction
            sortField = field;
            statusSortCycle = 0; // Reset status cycle when switching fields
            // Most fields default to ascending, but lastLesson defaults to descending (most recent first)
            sortDirection = field === 'lastLesson' ? 'desc' : 'asc';
        }
    }

    function sortStudents(students: Student[]): Student[] {
        if (!students.length) return students;

        return [...students].sort((a, b) => {
            let result: { comparison: number; hasEmpty: boolean };

            switch (sortField) {
                case 'name':
                    const nameA = `${a.first_name} ${a.last_name || ''}`.trim().toLowerCase();
                    const nameB = `${b.first_name} ${b.last_name || ''}`.trim().toLowerCase();
                    result = { comparison: nameA.localeCompare(nameB), hasEmpty: false };
                    break;

                case 'level':
                    result = compareWithEmptyHandling(
                        getCurrentLevel(a),
                        getCurrentLevel(b),
                        (val) => val === '-',
                        (a, b) => a.localeCompare(b)
                    );
                    break;

                case 'status':
                    result = compareWithEmptyHandling(
                        getCurrentStatus(a),
                        getCurrentStatus(b),
                        (val) => val === '-',
                        (a, b) => {
                            const orderA = getStatusSortValue(a.toLowerCase(), statusSortCycle);
                            const orderB = getStatusSortValue(b.toLowerCase(), statusSortCycle);
                            return orderA - orderB;
                        }
                    );
                    break;

                case 'nextLesson':
                    result = compareWithEmptyHandling(
                        getNextLessonFromStudent(a),
                        getNextLessonFromStudent(b),
                        (val) => !val,
                        (a, b) => new Date(a.datetime).getTime() - new Date(b.datetime).getTime()
                    );
                    break;

                case 'lastLesson':
                    result = compareWithEmptyHandling(
                        getLastLessonFromStudent(a),
                        getLastLessonFromStudent(b),
                        (val) => !val,
                        (a, b) => new Date(a.datetime).getTime() - new Date(b.datetime).getTime()
                    );
                    break;

                case 'lastQuiz':
                    // TODO: Implement when quiz data is available
                    result = { comparison: 0, hasEmpty: false };
                    break;

                default:
                    result = { comparison: 0, hasEmpty: false };
            }

            // If we're dealing with empty values, don't apply sort direction reversal
            // Empty values should always go to the bottom
            if (result.hasEmpty) {
                return result.comparison;
            }

            // For non-empty values, apply the sort direction
            return sortDirection === 'asc' ? result.comparison : -result.comparison;
        });
    }

    // Reactive sorted students
    let sortedStudents = $derived(sortStudents(students));

    function getSortIcon(field: SortField): string {
        if (sortField !== field) {
            return '⇅'; // Neutral sort icon
        }
        
        if (field === 'status') {
            const priorityStatus = statusCycleOrder[statusSortCycle];
            return `↑${priorityStatus.charAt(0).toUpperCase()}`;
        }
        
        return sortDirection === 'asc' ? '↑' : '↓';
    }

    function getSortButtonClass(field: SortField): string {
        const baseClass = 'btn btn-ghost btn-sm text-left justify-start h-auto min-h-0 p-1 font-medium hover:bg-accent/10';
        return sortField === field ? `${baseClass} text-accent` : `${baseClass} text-base-content`;
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
            
            // Note: Sorting is handled client-side for better UX
            
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
        // Reset sorting to default
        sortField = 'lastLesson';
        sortDirection = 'desc';
        loadStudents();
    }

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
            
           

            <!-- Current Sort Info -->
            <div class="bg-accent/10 border border-accent/20 rounded-lg p-3 text-sm">
                <div class="flex items-center gap-2">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
                    </svg>
                    <span class="text-accent font-medium">
                        Sorted by: {sortField === 'lastLesson' ? 'Last Lesson' : 
                                   sortField === 'nextLesson' ? 'Next Lesson' :
                                   sortField === 'lastQuiz' ? 'Last Quiz' :
                                   sortField === 'status' ? `Status (${statusCycleOrder[statusSortCycle]} first)` :
                                   sortField.charAt(0).toUpperCase() + sortField.slice(1)}
                        {sortField !== 'status' ? `(${sortDirection})` : ''}
                    </span>
                </div>
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
                    <th>
                        <button class={getSortButtonClass('name')} onclick={() => handleSort('name')}>
                            Name {getSortIcon('name')}
                        </button>
                    </th>
                    <th>
                        <button class={getSortButtonClass('level')} onclick={() => handleSort('level')}>
                            Level {getSortIcon('level')}
                        </button>
                    </th>
                    <th>
                        <button class={getSortButtonClass('status')} onclick={() => handleSort('status')}>
                            Status {getSortIcon('status')}
                        </button>
                    </th>
                    <th>
                        <button class={getSortButtonClass('nextLesson')} onclick={() => handleSort('nextLesson')}>
                            Next Lesson {getSortIcon('nextLesson')}
                        </button>
                    </th>
                    <th>
                        <button class={getSortButtonClass('lastLesson')} onclick={() => handleSort('lastLesson')}>
                            Last Lesson {getSortIcon('lastLesson')}
                        </button>
                    </th>
                    <th>
                        <button class={getSortButtonClass('lastQuiz')} onclick={() => handleSort('lastQuiz')}>
                            Last Quiz {getSortIcon('lastQuiz')}
                        </button>
                    </th>
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
                {:else if sortedStudents.length === 0}
                    <tr>
                        <td colspan="7" class="text-center p-8">
                            <div class="alert alert-info">
                                <span>No students found matching your criteria.</span>
                            </div>
                        </td>
                    </tr>
                {:else}
                    {#each sortedStudents as student (student.id)}
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