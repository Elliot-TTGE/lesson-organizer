<script lang="ts">
  import type { Lesson } from "../../types";
  import { deleteLesson, updateLesson, createLesson } from "../../api/lesson";
  import { lessonState, removeLessonFromState, updateLessonInState } from "$lib/states/lessonState.svelte";

  let { lesson = $bindable() }: { lesson: Lesson } = $props();
  let isEditing: boolean = $state(false);

  let { date, time } = $derived(initializeDateTime(lesson.datetime));
  let weekday: string = $derived(new Date(lesson.datetime).toLocaleDateString("en-US", {
    weekday: "long",
  }));

  // This is a bit hacky, but I didn't have time to make a cleaner solution
  let { dateInput, timeInput } = $state(initializeDateTimeInput(lesson.datetime));

  let student: string = lesson.students.map((student) => (student.first_name + ' ' + student.last_name)).join(", ");
  let plan: string = $state(lesson.plan);
  let concepts: string = $state(lesson.concepts);
  let notes: string = $state(lesson.notes);

  async function handleDelete() {
    if (confirm("Are you sure you want to delete this lesson?")) {
      await deleteLesson(lesson.id);
      removeLessonFromState(lesson.id);
      isEditing = false;
    }
  }

  async function handleConfirm() {
    const datetime = new Date(`${dateInput}T${timeInput}`).toISOString();
    const updatedLesson = { ...lesson, datetime, plan, concepts, notes };
    await updateLesson(updatedLesson);
    updateLessonInState(updatedLesson)
    isEditing = false;
  }

  function handleCancel() {
    isEditing = false;
    ({ dateInput, timeInput } = initializeDateTimeInput(lesson.datetime));
    plan = lesson.plan;
    concepts = lesson.concepts;
    notes = lesson.notes;
  }

  async function handleCopyToNextWeek() {
    const currentLessonDate = new Date(lesson.datetime);

    // Calculate the same day of the week in the next week
    const nextWeekDate = new Date(currentLessonDate);
    nextWeekDate.setDate(currentLessonDate.getDate() + 7);

    // Create a new lesson object with the updated date
    const newLesson = {
      ...lesson,
      id: undefined, // Ensure a new ID is generated
      datetime: nextWeekDate.toISOString(),
    };

    // Save the new lesson to the backend
    const createdLesson = await createLesson(newLesson);
  }

  function initializeDateTime(datetime: string) {
    return {
      date: new Date(datetime).toLocaleDateString("en-US"),
      time: new Date(datetime).toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };
  }

  function initializeDateTimeInput(datetime: string) {
    const localDate = new Date(datetime);
    const offset = localDate.getTimezoneOffset() * 60000; // offset in milliseconds
    const localISOTime = new Date(localDate.getTime() - offset).toISOString().slice(0, 16);
    return {
      dateInput: localISOTime.split('T')[0],
      timeInput: localISOTime.split('T')[1],
    };
  }
</script>

<div class="w-full rounded-sm bg-neutral">
  <div class="flex justify-end space-x-2 mb-2">
    {#if isEditing}
      <button onclick={handleConfirm} class="btn btn-ghost btn-accent btn-sm text-success items-center p-1">
        <span class="mr-2">Confirm</span>
      </button>
      <button onclick={handleCancel} class="btn btn-ghost btn-accent btn-sm text-warning items-center p-1">
        <span class="mr-2">Cancel</span>
      </button>
    {:else}
      <button onclick={handleCopyToNextWeek} class="btn btn-ghost btn-accent btn-sm text-success items-center p-1">
        <img src="/images/icons/arrow-clockwise.svg" alt="Copy Icon" />
      </button>
      <button onclick={() => isEditing = true} class="btn btn-ghost btn-accent btn-sm text-info items-center p-1">
        <img src="/images/icons/pencil-fill.svg" alt="Edit Icon" />
      </button>
    {/if}
    <button onclick={handleDelete} class="btn btn-ghost btn-accent btn-sm text-error items-center p-1">
      <img src="/images/icons/trash3.svg" alt="Trash Icon"/>
    </button>
  </div>
  <div class="flex flex-col space-y-2 p-2">
    {#if isEditing}
      <input type="date" bind:value={dateInput} class="input input-bordered" />
      <input type="time" bind:value={timeInput} class="input input-bordered" />
    {:else}
      <p>{weekday}</p>
      <p>{date}:</p>
      <p>{time}:</p>
    {/if}
    <p>{student}</p>
  </div>
  <div class="flex flex-col space-y-2 p-2">
    <div>
      <p class="font-bold">Today's plan:</p>
      {#if isEditing}
        <textarea rows="4" bind:value={plan} class="min-h-24 invisible-textarea"></textarea>
      {:else}
        <p class="min-h-24">{plan}</p>
      {/if}
    </div>
    <div class="mx-2 min-h-32 bg-accent">
      <p class="font-bold">Concepts Taught</p>
      {#if isEditing}
        <textarea rows="4" class="invisible-textarea" bind:value={concepts}></textarea>
      {:else}
        <p>{concepts}</p>
      {/if}
    </div>
    <div class="mx-2 min-h-32 bg-accent h-auto">
      <p class="font-bold">Lesson Notes</p>
      {#if isEditing}
        <textarea rows="4" class="invisible-textarea" bind:value={notes}></textarea>
      {:else}
        <p>{notes}</p>
      {/if}
    </div>
  </div>
</div>

<style>
  p, .invisible-textarea {
    color: darkorchid;
  }

  .invisible-textarea {
    border: none;
    background: transparent;
    resize: none;
    outline: none;
    field-sizing: content;  /* Only works on Chromium browsers as of 02/22/2025 */
    width: 100%;
  }
</style>
