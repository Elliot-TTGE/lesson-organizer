<script lang="ts">
    import { type Level, type Student, type StudentLevelHistory, type StudentStatus, type StudentStatusHistory } from "../../types";
    import StudentCard from "./StudentCard.svelte";
    import StudentCreateModal from "./StudentCreateModal.svelte";
    import { fetchStudents } from "../../api/student";
    import { onMount } from "svelte";
    import { fetchLevels } from "../../api/level";
    import { fetchStudentStatuses } from "../../api/studentStatus";

    let students = $state<Student[]>([]);
    let levels = $state<Level[]>([])
    let studentStatuses = $state<StudentStatus[]>([]);
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
        selectedStudent = newStudent.id;
    }

    function getCurrentLevel(student: Student): string {
        if (!student.level_history || student.level_history.length === 0) {
            return '-';
        }

        // Sort level history by start_date descending to get the most recent
        const sortedHistory = student.level_history.sort((a, b) => 
            new Date(b.start_date).getTime() - new Date(a.start_date).getTime()
        );
        
        const mostRecentHistory = sortedHistory[0];
        const level = levels.find(l => l.id === mostRecentHistory.level_id);
        
        if (!level || !level.curriculum) {
            return '-';
        }
        
        return `${level.curriculum.name}: ${level.name}`;
    }

    function getLastLesson(student: Student): string {
        if (!student.lessons || student.lessons.length === 0) {
            return '-';
        }

        const now = new Date();
        
        // Filter lessons to only include those in the past, then sort by datetime descending
        const pastLessons = student.lessons
            .filter(lesson => new Date(lesson.datetime) < now)
            .sort((a, b) => new Date(b.datetime).getTime() - new Date(a.datetime).getTime());
        
        if (pastLessons.length === 0) {
            return '-';
        }
        
        const mostRecentLesson = pastLessons[0];
        const lessonDate = new Date(mostRecentLesson.datetime);
        
        // Format the date and time
        return lessonDate.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric',
            year: 'numeric'
        }) + ' ' + lessonDate.toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    }

    function getNextLesson(student: Student): string {
        if (!student.lessons || student.lessons.length === 0) {
            return '-';
        }

        const now = new Date();
        
        // Filter lessons to only include those in the future, then sort by datetime ascending
        const futureLessons = student.lessons
            .filter(lesson => new Date(lesson.datetime) > now)
            .sort((a, b) => new Date(a.datetime).getTime() - new Date(b.datetime).getTime());
        
        if (futureLessons.length === 0) {
            return '-';
        }
        
        const nextLesson = futureLessons[0];
        const lessonDate = new Date(nextLesson.datetime);
        
        // Format the date and time
        return lessonDate.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric',
            year: 'numeric'
        }) + ' ' + lessonDate.toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    }

    function getCurrentStatus(student: Student): string {
        if (!student.status_history || student.status_history.length === 0) {
            return '-';
        }

        // Sort status history by changed_at descending to get the most recent
        const sortedHistory = student.status_history.sort((a, b) => 
            new Date(b.changed_at).getTime() - new Date(a.changed_at).getTime()
        );
        
        const mostRecentHistory = sortedHistory[0];
        const status = studentStatuses.find(s => s.id === mostRecentHistory.status_id);
        
        if (!status) {
            return '-';
        }
        
        return status.name;
    }

    onMount(async () => {
        try {
            students = (await fetchStudents()).students;
            levels = await fetchLevels();
            studentStatuses = await fetchStudentStatuses();
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
                <th>Status</th>
                <th>Next Lesson</th>
                <th>Last Lesson</th>
                <th>Last Quiz</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody class="table-zebra">
            {#if isLoading}
                <tr>
                    <td colspan="8" class="text-center p-8">
                        <span class="loading loading-spinner loading-lg"></span>
                    </td>
                </tr>
            {:else if error}
                <tr>
                    <td colspan="8" class="p-4">
                        <div class="alert alert-error">
                            <span>Error: {error}</span>
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