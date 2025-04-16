<script lang="ts">
  import { createLesson } from "../../api/lesson";
  import type { Lesson } from "../../types";
  import { lessonState, addLessonToState } from "$lib/states/lessonState.svelte";
  import { lessonWeekStartDate } from "$lib/states/lessonWeekStartDate.svelte";
  import TipexEditor from "./TipexEditor.svelte";

  let { children } = $props();

  let date = $state("");
  let time = $state("");
  let plan = $state("");
  let concepts = $state("");
  let notes = $state("");

  let lessonCreateModal: HTMLDialogElement;
  let dateWarning = $state(false);
  let timeWarning = $state(false);

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
  onclick={() => {
    date = "";
    time = "";
    plan = "";
    concepts = "";
    notes = "";
    lessonCreateModal.showModal();
  }}
>
  {@render children?.()}
</button>
<dialog bind:this={lessonCreateModal} class="modal">
  <div class="modal-box bg-base-100 w-full max-w-4xl">
    <h3 class="text-lg font-bold text-base-content">Create a New Lesson</h3>
    <div class="py-4 flex flex-col space-y-4">
      <div class="flex flex-row space-x-4 w-full">
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
        </div>
      </div>
      <div class="flex flex-row space-x-4 w-full">
        <div class="flex flex-col space-y-4 w-1/2">
          <TipexEditor
            bind:body={plan}
            heading="Today's Plan"
            height="h-[20vh]"
          />
        </div>
        <div class="flex flex-col space-y-4 w-1/2">
          <TipexEditor
            bind:body={concepts}
            heading="Concepts Taught"
            height="h-[20vh]"
          />
        </div>
      </div>
      <div class="flex flex-row space-x-4 w-full">
        <div class="flex flex-col space-y-4 w-1/2">
          <TipexEditor
            bind:body={notes}
            heading="Lesson Notes"
            height="h-[20vh]"
          />
        </div>
        <div class="flex flex-col space-y-4 w-1/2">
          <!-- Student Section -->
        </div>
      </div>
    </div>
    <div class="modal-action">
      <button class="btn" onclick={() => lessonCreateModal.close()}>Cancel</button>
      <button class="btn btn-primary" onclick={handleCreateLesson}>Create</button>
    </div>
  </div>
  <form method="dialog" class="modal-backdrop">
    <button>close</button>
  </form>
</dialog>
