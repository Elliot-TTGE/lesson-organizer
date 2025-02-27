<script lang="ts">
  import { createLesson } from "../../api/lesson";
  import type { Lesson } from "../../types";
  import { lessonState, addLessonToState } from "$lib/states/lessonState.svelte";
  import { lessonWeekStartDate } from "$lib/states/lessonWeekStartDate.svelte";

  export let date = "";
  export let time = "";
  export let plan = "";
  export let concepts = "";
  export let notes = "";
  // export let students = "";

  let lessonCreateModal: HTMLDialogElement;
  let dateWarning = false;
  let timeWarning = false;

  async function handleCreateLesson() {
    dateWarning = date === "";
    timeWarning = time === "";

    if (dateWarning || timeWarning) {
      return;
    }

    const datetime = new Date(`${date}T${time}`).toISOString();
    const newLesson: Partial<Lesson> = {
      datetime,
      plan,
      concepts,
      notes,
    };

    try {
      const createdLesson = await createLesson(newLesson);
      addLessonToState(createdLesson);
      lessonCreateModal.close();
    } catch (error) {
      console.error("Error creating lesson:", error);
    }
  }
</script>

<button
  class="btn btn-secondary"
  on:click={() => {
    date = "";
    time = "";
    plan = "";
    concepts = "";
    notes = "";
    lessonCreateModal.showModal();
  }}
>
  <slot />
</button>
<dialog bind:this={lessonCreateModal} class="modal">
  <div class="modal-box bg-base-100 w-full max-w-4xl">
    <h3 class="text-lg font-bold text-base-content">Create a New Lesson</h3>
    <div class="py-4 flex flex-row space-x-4">
      <div class="flex flex-col space-y-4 w-1/2">
        <label class="label" for="date">
          <span class="label-text">Date</span>
        </label>
        <input
          id="date"
          type="date"
          bind:value={date}
          class="input input-bordered w-full bg-secondary"
          required
        />
        {#if dateWarning}
          <p class="text-error">Date is required.</p>
        {/if}

        <label class="label" for="plan">
          <span class="label-text">Plan</span>
        </label>
        <textarea
          id="plan"
          bind:value={plan}
          class="textarea textarea-bordered w-full bg-secondary"
          rows="3"
        ></textarea>

        <label class="label" for="notes">
          <span class="label-text">Notes</span>
        </label>
        <textarea
          id="notes"
          bind:value={notes}
          class="textarea textarea-bordered w-full bg-secondary"
          rows="3"
        ></textarea>
      </div>
      <div class="flex flex-col space-y-4 w-1/2">
        <label class="label" for="time">
          <span class="label-text">Time</span>
        </label>
        <input
          id="time"
          type="time"
          bind:value={time}
          class="input input-bordered w-full bg-secondary"
          required
        />
        {#if timeWarning}
          <p class="text-error">Time is required.</p>
        {/if}

        <label class="label" for="concepts">
          <span class="label-text">Concepts</span>
        </label>
        <textarea
          id="concepts"
          bind:value={concepts}
          class="textarea textarea-bordered w-full bg-secondary"
          rows="3"
        ></textarea>

        <!-- <label class="label" for="students">
          <span class="label-text">Students (comma-separated)</span>
        </label>
        <textarea
          id="students"
          type="text"
          bind:value={students}
          class="textarea textarea-bordered w-full bg-secondary"
          rows="3"
        ></textarea> -->
      </div>
    </div>
    <div class="modal-action">
      <button class="btn" on:click={() => lessonCreateModal.close()}>Cancel</button>
      <button class="btn btn-primary" on:click={handleCreateLesson}>Create</button>
    </div>
  </div>
  <form method="dialog" class="modal-backdrop">
    <button>close</button>
  </form>
</dialog>
