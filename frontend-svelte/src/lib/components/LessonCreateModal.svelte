<script lang="ts">
    export let date = '';
    export let time = '';
    export let people = '';

    let lessonCreateModal: HTMLDialogElement;

    function createLesson() {
        // Handle lesson creation logic here
        // closeModal();
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

            <label class="label" for="people">
                <span class="label-text">Person/People</span>
            </label>
            <input id="people" type="text" bind:value={people} class="input input-bordered w-full" />
        </div>
        <div class="modal-action">
            <form method='dialog'>
                <button class="btn">Cancel</button>
                <button class="btn btn-primary" on:click={createLesson}>Create</button>
            </form>
        </div>
    </div>
    <form method='dialog' class='modal-backdrop'>
        <button>close</button>
    </form>
</dialog>
