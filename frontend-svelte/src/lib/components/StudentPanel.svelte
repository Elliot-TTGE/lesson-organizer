<script lang="ts">
    import type { Student } from "../../types";
    import StudentCard from "./StudentCard.svelte";
    import StudentCreateModal from "./StudentCreateModal.svelte";
    import { fetchStudents } from "../../api/student";
    import { onMount } from "svelte";

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

    function handleStudentCreated(newStudent: Student) {
        // Add the new student to the existing list
        students = [...students, newStudent];
        
        // Close any existing modals
        closeModal();
        
        // Open the StudentCard modal for the new student
        showModal = true;
        selectedStudent = newStudent.id;
    }

    onMount(async () => {
        try {
            const response = await fetchStudents();
            students = response.students;
            isLoading = false;
        } catch (err) {
            error = err instanceof Error ? err.message : 'Failed to fetch students';
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

    <table class="table border bg-base-200 border-base-200">
        <thead class="sticky z-10 top-32">
            <tr>
                <th>#</th>
                <th>Name</th>
                <th>Level</th>
                <th>Next Lesson</th>
                <th>Last Lesson</th>
                <th>Last Quiz</th>
                <th>Actions</th>
            </tr>
        </thead>
    </table>
</div>
<div class="overflow-y-auto">
    {#if isLoading}
        <div class="flex justify-center p-8">
            <span class="loading loading-spinner loading-lg"></span>
        </div>
    {:else if error}
        <div class="alert alert-error m-4">
            <span>Error: {error}</span>
        </div>
    {:else}
        <table class="table table-zebra border border-base-200">
            <tbody>
                {#each students as student (student.id)}
                    <tr>
                    <td>{student.id}</td>
                        <td>{student.first_name} {student.last_name || ''}</td>
                        <td>-</td> <!-- TODO: Add current level logic -->
                        <td>-</td> <!-- TODO: Add next lesson logic -->
                        <td>-</td> <!-- TODO: Add last lesson logic -->
                        <td>-</td> <!-- TODO: Add last quiz logic -->
                        <td>
                            <button class="btn btn-primary btn-sm" onclick={() => openModal(student)}>Edit</button>
                        </td>
                    </tr>
                {/each}
                {#if students.length === 0}
                    <tr>
                        <td colspan="7" class="text-center py-8">
                            <div class="text-base-content/60">
                                No students found. 
                                <StudentCreateModal onStudentCreated={handleStudentCreated}>
                                    <span class="link link-primary">Create your first student</span>
                                </StudentCreateModal>
                            </div>
                        </td>
                    </tr>
                {/if}
            </tbody>
        </table>
    {/if}
</div>

{#if showModal}
    <dialog open class="modal modal-middle">
        <div class="modal-box max-w-[85vw] h-[85vh]">
            <div class="modal-action justify-end p-0 mb-2">
                <button class="btn" onclick={closeModal}>Close</button>
            </div>
            <StudentCard student={selectedStudent} />
        </div>
        <form method="dialog" class="modal-backdrop">
            <button onclick={closeModal}>close</button>
        </form>
    </dialog>
{/if}