<script lang="ts">
    import { createStudent } from "../../api/student";
    import type { Student } from "../../types";
    import TipexEditor from "./TipexEditor.svelte";

    let { children } = $props();

    let first_name = $state("");
    let last_name = $state("");
    let curriculum = $state("");
    let level = $state("");
    let status: 'active' | 'inactive' | 'hold' | 'trial' = $state("active");
    let notes = $state("");
    let started_date = $state("");

    let studentCreateModal: HTMLDialogElement;
    let firstNameWarning = $state(false);

    async function handleCreateStudent() {
        firstNameWarning = first_name === "";

        if (firstNameWarning) {
            return;
        }

        const created_date = new Date().toISOString();
        const newStudent: Partial<Student> = {
            first_name,
            last_name,
            created_date,
            started_date,
            status,
            /*levels,*/
            notes
        }

        try {
            const createdStudent = await createStudent(newStudent);
            studentCreateModal.close();
        } catch (error) {
            console.error("Error craeting student: ", error);
        }
    }
</script>

<button
    class="btn btn-primary"
    onclick={() => {
        first_name = "";
        last_name = "";
        started_date = "";
        status = "active";
        /*levels = "";*/
        notes = "";
        studentCreateModal.showModal();
    }}
>
    {@render children?.()}
</button>
<dialog bind:this={studentCreateModal} class="modal">
    <div class="modal-box bg-base-100 w-full max-w-4xl">
        <h3 class="text-lg font-bold text-base-content mb-4">Create a New Student</h3>
        <form class="flex flex-col gap-4">
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
                    bind:value={curriculum}
                >
                    <option value="" disabled selected>Select curriculum</option>
                    <option value="math">Math</option>
                    <option value="reading">Reading</option>
                    <option value="science">Science</option>
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
                    bind:value={level}
                >
                    <option value="" disabled selected>Select level</option>
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
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
                    bind:value={status}
                >
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                    <option value="hold">Hold</option>
                    <option value="trial">Trial</option>
                </select>
            </div>
            <!-- Notes (TipexEditor) -->
            <div>
                <TipexEditor bind:body={notes} heading="Notes" height="h-[20vh]" />
            </div>
        </form>
        <div class="modal-action mt-6">
            <button class="btn" onclick={() => studentCreateModal.close()}>Cancel</button>
            <button class="btn btn-primary" onclick={handleCreateStudent}>Create</button>
        </div>        
    </div>
    <form method="dialog" class="modal-backdrop">
        <button>close</button>
    </form>
</dialog>