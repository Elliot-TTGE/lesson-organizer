<script lang="ts">
    import { createStudent } from "../../api/student";
    import { createStudentStatusHistory } from "../../api/studentStatusHistory";
    import { createStudentLevelHistory } from "../../api/studentLevelHistory";
    import { fetchCurriculums } from "../../api/curriculum";
    import { fetchStudentStatuses } from "../../api/studentStatus";
    import type { Student, Curriculum, StudentStatus } from "../../types";
    import { onMount } from "svelte";

    let { children, onStudentCreated } = $props();

    let first_name = $state("");
    let last_name = $state("");
    let selectedCurriculumId = $state<number | null>(null);
    let selectedLevelId = $state<number | null>(null);
    let selectedStatusId = $state<number | null>(null);

    let studentCreateModal: HTMLDialogElement;
    let firstNameWarning = $state(false);
    let isLoading = $state(false);

    // Data for dropdowns
    let curriculums = $state<Curriculum[]>([]);
    let statuses = $state<StudentStatus[]>([]);

    onMount(async () => {
        try {
            [curriculums, statuses] = await Promise.all([
                fetchCurriculums(),
                fetchStudentStatuses()
            ]);
        } catch (error) {
            console.error("Error loading dropdown data:", error);
        }
    });

    // Reset level selection when curriculum changes
    $effect(() => {
        if (selectedCurriculumId) {
            selectedLevelId = null;
        }
    });

    async function handleCreateStudent() {
        firstNameWarning = first_name.trim() === "";

        if (firstNameWarning) {
            return;
        }

        isLoading = true;

        try {
            // Create the student
            const newStudent = await createStudent({
                first_name: first_name.trim(),
                last_name: last_name.trim() || undefined,
                date_started: new Date().toISOString()
            });

            // Arrays to store created history records
            let statusHistory = [];
            let levelHistory = [];

            // Create status history if status is selected
            if (selectedStatusId) {
                const statusHistoryRecord = await createStudentStatusHistory({
                    student_id: newStudent.id,
                    status_id: selectedStatusId,
                    changed_at: new Date().toISOString()
                });
                statusHistory.push(statusHistoryRecord);
            }

            // Create level history if level is selected
            if (selectedLevelId) {
                const levelHistoryRecord = await createStudentLevelHistory({
                    student_id: newStudent.id,
                    level_id: selectedLevelId,
                    start_date: new Date().toISOString()
                });
                levelHistory.push(levelHistoryRecord);
            }

            studentCreateModal.close();
            
            // Notify parent component about the new student with history data
            if (onStudentCreated) {
                onStudentCreated(newStudent, statusHistory, levelHistory);
            }

        } catch (error) {
            console.error("Error creating student:", error);
        } finally {
            isLoading = false;
        }
    }

    function resetForm() {
        first_name = "";
        last_name = "";
        selectedCurriculumId = null;
        selectedLevelId = null;
        selectedStatusId = null;
        firstNameWarning = false;
    }
</script>

<button
    class="btn btn-primary"
    onclick={() => {
        resetForm();
        studentCreateModal.showModal();
    }}
>
    {@render children?.()}
</button>

<dialog bind:this={studentCreateModal} class="modal">
    <div class="modal-box bg-base-100 w-full max-w-2xl">
        <h3 class="text-lg font-bold text-base-content mb-4">Create a New Student</h3>
        
        <form class="flex flex-col gap-4" onsubmit={(e) => { e.preventDefault(); handleCreateStudent(); }}>
            <!-- First Name (required) -->
            <div>
                <label class="label" for="first_name">
                    <span class="label-text">First Name<span class="text-error">*</span></span>
                </label>
                <input
                    id="first_name"
                    type="text"
                    class="input input-bordered w-full"
                    bind:value={first_name}
                    required
                />
                {#if firstNameWarning}
                    <p class="text-error mt-1">First name is required.</p>
                {/if}
            </div>

            <!-- Last Name -->
            <div>
                <label class="label" for="last_name">
                    <span class="label-text">Last Name</span>
                </label>
                <input
                    id="last_name"
                    type="text"
                    class="input input-bordered w-full"
                    bind:value={last_name}
                />
            </div>

            <!-- Curriculum Dropdown -->
            <div>
                <label class="label" for="curriculum">
                    <span class="label-text">Curriculum</span>
                </label>
                <select
                    id="curriculum"
                    class="select select-bordered w-full"
                    bind:value={selectedCurriculumId}
                >
                    <option value={null}>Select curriculum</option>
                    {#each curriculums as curriculum}
                        <option value={curriculum.id}>{curriculum.name}</option>
                    {/each}
                </select>
            </div>

            <!-- Level Dropdown -->
            <div>
                <label class="label" for="level">
                    <span class="label-text">Level</span>
                </label>
                <select
                    id="level"
                    class="select select-bordered w-full"
                    bind:value={selectedLevelId}
                    disabled={!selectedCurriculumId}
                >
                    <option value={null}>
                        {selectedCurriculumId ? "Select level" : "Select curriculum first"}
                    </option>
                    {#each curriculums.find(c => c.id === selectedCurriculumId)?.levels || [] as level}
                        <option value={level.id}>{level.name}</option>
                    {/each}
                </select>
            </div>

            <!-- Status Dropdown -->
            <div>
                <label class="label" for="status">
                    <span class="label-text">Status</span>
                </label>
                <select
                    id="status"
                    class="select select-bordered w-full"
                    bind:value={selectedStatusId}
                >
                    <option value={null}>Select status</option>
                    {#each statuses as status}
                        <option value={status.id}>{status.name}</option>
                    {/each}
                </select>
            </div>
        </form>

        <div class="modal-action mt-6">
            <button 
                class="btn" 
                onclick={() => studentCreateModal.close()}
                disabled={isLoading}
            >
                Cancel
            </button>
            <button 
                class="btn btn-primary" 
                onclick={handleCreateStudent}
                disabled={isLoading}
            >
                {#if isLoading}
                    <span class="loading loading-spinner loading-sm"></span>
                {/if}
                Create
            </button>
        </div>        
    </div>
    <form method="dialog" class="modal-backdrop">
        <button>close</button>
    </form>
</dialog>