<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import { onMount } from 'svelte';
    import { type Lesson } from "../../types";

    let lesson: Lesson = null;

    let lessonCreateModal: HTMLDialogElement;
    let date: string;
    let time: string;
    let plan: string;
    let concepts_taught: string;
    let additional_notes: string;
    let students: string;

    const dispatch = createEventDispatcher();

    function createLesson() {
        const datetime = new Date(`${date}T${time}`);
        const lesson = {
            datetime,
            plan,
            concepts_taught,
            additional_notes,
            students: students.split(',').map(name => name.trim())
        };
        dispatch('create', lesson);
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
            <label class="label" for="date">
                <span class="label-text">Date</span>
            </label>
            <input id="date" type="date" bind:value={date} class="input input-bordered w-full" />

            <label class="label" for="time">
                <span class="label-text">Time</span>
            </label>
            <input id="time" type="time" bind:value={time} class="input input-bordered w-full" />

            <label class="label" for="plan">
                <span class="label-text">Plan</span>
            </label>
            <input id="plan" type="text" bind:value={plan} class="input input-bordered w-full" />

            <label class="label" for="concepts_taught">
                <span class="label-text">Concepts Taught</span>
            </label>
            <input id="concepts_taught" type="text" bind:value={concepts_taught} class="input input-bordered w-full" />

            <label class="label" for="additional_notes">
                <span class="label-text">Additional Notes</span>
            </label>
            <input id="additional_notes" type="text" bind:value={additional_notes} class="input input-bordered w-full" />

            <label class="label" for="students">
                <span class="label-text">Students (comma-separated)</span>
            </label>
            <input id="students" type="text" bind:value={students} class="input input-bordered w-full" />
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
