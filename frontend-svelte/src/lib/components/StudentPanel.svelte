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
        getLevelDisplayById
    } from "../states";

    let students = $state<Student[]>([]);
    let isLoading = $state(true);
    let error = $state<string | null>(null);

    let showModal = $state(false);
    let selectedStudent = $state<number | null>(null);

    function openModal(student: Student) {
        showModal = true;
        selectedStudent = student.id;
    }

    function closeModal() {
        showModal = false;
        selectedStudent = null;
    }

    async function handleStudentUpdated(updatedStudent: Student) {
        // Update the student in the students array with fresh data
        students = students.map(student => 
            student.id === updatedStudent.id ? updatedStudent : student
        );
    }

    function handleStudentCreated(newStudent: Student, status_history: StudentStatusHistory[], level_history: StudentLevelHistory[]) {
        // Initialize the student with empty arrays for relationships we don't need to fetch
        const enrichedStudent: Student = {
            ...newStudent,
            lessons: [], // New students won't have lessons yet
            quizzes: [], // New students won't have quizzes yet
            // Use the history arrays passed from the modal
            status_history: status_history || [],
            level_history: level_history || []
        };

        // Add the enriched student to the existing list
        students = [...students, enrichedStudent];
        
        // Close any existing modals
        closeModal();
        
        // Open the StudentCard modal for the new student
        showModal = true;
        selectedStudent = enrichedStudent.id;
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

    onMount(async () => {
        try {
            // Fetch all data in parallel
            await Promise.all([
                fetchStudents().then(response => { students = response.students; }),
                refreshLevels(),
                refreshStatuses()
            ]);
            isLoading = false;
        } catch (err) {
            error = err instanceof Error ? err.message : 'Failed to fetch data';
            isLoading = false;
        }
    });
</script>

<div class="sticky z-10 mt-16 top-16 bg-base-200">
    <div class="flex bg-base-200 mb-2">
        <fieldset class="fieldset mr-auto ml-8 w-100">
            <p class="fieldset-legend">Find a student</p>
            <label class="input input-accent">
                <svg class="h-[1em] opacity-50" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                    <g
                    stroke-linejoin="round"
                    stroke-linecap="round"
                    stroke-width="2.5"
                    fill="none"
                    stroke="currentColor"
                    >
                        <circle cx="11" cy="11" r="8"></circle>
                        <path d="m21 21-4.3-4.3"></path>
                    </g>
                </svg>
                <input type="search" placeholder="Search"/>
            </label>
        </fieldset>
        <div class="flex items-center">
            <div class="mr-8">
                <StudentCreateModal onStudentCreated={handleStudentCreated}>New Student</StudentCreateModal>
            </div>
            <!-- Options for student search -->
        </div>
    </div>

    <div class="overflow-y-auto max-h-[calc(100vh-10rem)]">
        <table class="table border bg-base-200 border-base-200">
            <thead class="sticky top-0 z-10 bg-base-200">
                <tr>
                    <th>#</th>
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
                {#if isLoading || statusState.isLoading || levelState.isLoading}
                    <tr>
                        <td colspan="8" class="text-center p-8">
                            <span class="loading loading-spinner loading-lg"></span>
                        </td>
                    </tr>
                {:else if error || statusState.error || levelState.error}
                    <tr>
                        <td colspan="8" class="p-4">
                            <div class="alert alert-error">
                                <span>Error: {error || statusState.error || levelState.error}</span>
                            </div>
                        </td>
                    </tr>
                {:else}
                    {#each students as student (student.id)}
                        <tr class="hover">
                            <td>{student.id}</td>
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