<script lang="ts">
    import { onMount } from 'svelte';
    import { type Lesson } from "../../types";
    import type { ErrorObject } from '$lib/utils/index.svelte';

    let lessonCreateModal: HTMLDialogElement;
    let date: string = "";
    let time: string = "";
    let plan: string = "";
    let concepts_taught: string = "";
    let additional_notes: string = "";
    let students: string = "";

    let error: ErrorObject = {
        date: "",
        time: "",
        plan: "",
        concepts_taught: "",
        additional_notes: "",
        students: ""
    };

    function validateFields(): boolean {
        let hasError = false;
        error = {}; // Reset errors

        if (date === "") {
            error.date = "Date can't be empty";
            hasError = true;
        }
        if (time === "") {
            error.time = "Time can't be empty";
            hasError = true;
        }
        if (plan === "") {
            error.plan = "Plan can't be empty";
            hasError = true;
        }
        if (concepts_taught === "") {
            error.concepts_taught = "Concepts taught can't be empty";
            hasError = true;
        }
        if (students === "") {
            error.students = "Students can't be empty";
            hasError = true;
        }

        return !hasError;
    }

    function createLesson() {
        if (!validateFields()) {
            return;
        }

        const datetime = new Date(`${date}T${time}`);
        const lesson = {
            datetime,
            plan,
            concepts_taught,
            additional_notes,
            students: students.split(',').map(name => name.trim())
        };

        // Assuming onCreate is passed as a prop
        if (typeof onCreate === 'function') {
            onCreate(lesson);
        }

        lessonCreateModal.close();
    }
</script>

<button class='btn btn-secondary' on:click={() => {lessonCreateModal.showModal()}}>
    <slot />    
</button>
<dialog bind:this={lessonCreateModal} class="modal">
    <div class="modal-box">
        <h3 class="font-bold text-lg">Create a New Lesson</h3>
        <div class="py-4">
            <div class="flex">
                <div class="w-1/2">
                    <label class="label" for="date">
                        <span class="label-text">Date</span>
                    </label>
                    <input id="date" type="date" bind:value={date} class="input input-bordered w-full" />
                    {#if error.date}
                        <p class="text-red-500 text-sm">{error.date}</p>
                    {/if}

                    <label class="label" for="time">
                        <span class="label-text">Time</span>
                    </label>
                    <input id="time" type="time" bind:value={time} class="input input-bordered w-full" />
                    {#if error.time}
                        <p class="text-red-500 text-sm">{error.time}</p>
                    {/if}

                    <label class="label" for="students">
                        <span class="label-text">Students (comma-separated)</span>
                    </label>
                    <input id="students" type="text" bind:value={students} class="input input-bordered w-full" />
                    {#if error.students}
                        <p class="text-red-500 text-sm">{error.students}</p>
                    {/if}
                </div>
                <div class="w-1/2 pl-4">
                    <label class="label" for="plan">
                        <span class="label-text">Plan</span>
                    </label>
                    <textarea id="plan" bind:value={plan} class="textarea textarea-bordered w-full h-24"></textarea>
                    {#if error.plan}
                        <p class="text-red-500 text-sm">{error.plan}</p>
                    {/if}

                    <label class="label" for="concepts_taught">
                        <span class="label-text">Concepts Taught</span>
                    </label>
                    <textarea id="concepts_taught" bind:value={concepts_taught} class="textarea textarea-bordered w-full h-24"></textarea>
                    {#if error.concepts_taught}
                        <p class="text-red-500 text-sm">{error.concepts_taught}</p>
                    {/if}

                    <label class="label" for="additional_notes">
                        <span class="label-text">Additional Notes</span>
                    </label>
                    <textarea id="additional_notes" bind:value={additional_notes} class="textarea textarea-bordered w-full h-24"></textarea>
                    {#if error.additional_notes}
                        <p class="text-red-500 text-sm">{error.additional_notes}</p>
                    {/if}
                </div>
            </div>
        </div>
        <div class="modal-action">
            <form method='dialog'>
                <button class="btn">Cancel</button>
                <button type="button" class="btn btn-primary" on:click={createLesson}>Create</button>
            </form>
        </div>
    </div>
    <form method='dialog' class='modal-backdrop'>
        <button>close</button>
    </form>
</dialog>
