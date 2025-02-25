<script lang="ts">
  import type { Lesson } from "../../types";
  import { deleteLesson, updateLesson } from "../../api/lesson";
  import { lessonState } from "$lib/states/lessonState.svelte";
  import { onMount } from 'svelte';

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
      lessonState.lessons = lessonState.lessons.filter(l => l.id !== lesson.id);
      isEditing = false;
    }
  }

  async function handleConfirm() {
    const datetime = new Date(`${dateInput}T${timeInput}`).toISOString();
    const updatedLesson = { ...lesson, datetime, plan, concepts, notes };
    await updateLesson(updatedLesson);
    lesson.datetime = datetime;
    isEditing = false;
  }

  function handleCancel() {
    isEditing = false;
    ({ dateInput, timeInput } = initializeDateTimeInput(lesson.datetime));
    plan = lesson.plan;
    concepts = lesson.concepts;
    notes = lesson.notes;
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
    return {
      dateInput: new Date(datetime).toISOString().split('T')[0],
      timeInput: new Date(datetime).toISOString().split('T')[1].slice(0,5),
    }
  }
</script>

<div class="m-4 w-64 rounded bg-neutral">
  <div class="flex justify-end space-x-2 mb-2">
    {#if isEditing}
      <button onclick={handleConfirm} class="btn btn-ghost btn-sm text-success items-center p-1">
        <span class="mr-2">Confirm</span>
      </button>
      <button onclick={handleCancel} class="btn btn-ghost btn-sm text-warning items-center p-1">
        <span class="mr-2">Cancel</span>
      </button>
    {:else}
      <button onclick={() => isEditing = true} class="btn btn-ghost btn-sm text-info items-center p-1">
        <span class="mr-2">Edit</span>
      </button>
    {/if}
    <button onclick={handleDelete} class="btn btn-ghost btn-sm text-error items-center p-1">
      <span class="mr-2">Delete</span>
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
      <p class="font-bold">Card Concepts Taught</p>
      {#if isEditing}
        <textarea rows="4" class="invisible-textarea" bind:value={concepts}></textarea>
      {:else}
        <p>{concepts}</p>
      {/if}
    </div>
    <div class="mx-2 min-h-32 bg-accent h-auto">
      <p class="font-bold">Card Lesson Notes</p>
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
