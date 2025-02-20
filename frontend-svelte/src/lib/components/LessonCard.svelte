<script lang="ts">
  import type { Lesson } from "../../types";
  import { deleteLesson, updateLesson } from "../../api/lesson";
  import { lessonState } from "$lib/states/lessonState.svelte";

  let { lesson }: { lesson: Lesson } = $props();
  let isEditing: boolean = $state(false);

  function initializeDateTime(datetime: string) {
    return {
      date: new Date(datetime).toLocaleDateString("en-US"),
      time: new Date(datetime).toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };
  }

  let { date, time } = $state(initializeDateTime(lesson.datetime));
  let weekday: string = $state(new Date(lesson.datetime).toLocaleDateString("en-US", {
    weekday: "long",
  }));
  let student: string = lesson.students.map((student) => (student.first_name + ' ' + student.last_name)).join(", ");
  let plan: string = $state(lesson.plan);
  let concepts: string = $state(lesson.concepts);
  let notes: string = $state(lesson.notes);

  async function handleDelete() {
    if (confirm("Are you sure you want to delete this lesson?")) {
      await deleteLesson(lesson.id);
      lessonState.lessons = lessonState.lessons.filter(l => l.id !== lesson.id);
    }
  }

  async function handleConfirm() {
    const datetime = new Date(`${date}T${time}`).toISOString();
    const updatedLesson = { ...lesson, datetime, plan, concepts, notes };
    await updateLesson(updatedLesson);
    lessonState.lessons = lessonState.lessons.map(l => l.id === lesson.id ? updatedLesson : l);
    isEditing = false;
  }

  function handleCancel() {
    isEditing = false;
    ({ date, time } = initializeDateTime(lesson.datetime));
    plan = lesson.plan;
    concepts = lesson.concepts;
    notes = lesson.notes;
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
      <input type="date" bind:value={date} class="input input-bordered" />
      <input type="time" bind:value={time} class="input input-bordered" />
    {:else}
      <p>{weekday}</p>
      <p>{date}:</p>
      <p>{time}:</p>
    {/if}
    <p>{student}</p>
  </div>
  <div class="flex flex-col space-y-2 p-2">
    <div>
      <p>Today's plan:</p>
      {#if isEditing}
        <textarea bind:value={plan} class="min-h-24 textarea textarea-primary"></textarea>
      {:else}
        <p class="min-h-24">{plan}</p>
      {/if}
    </div>
    <div class="mx-2 min-h-32 bg-accent">
      <p>Card Concepts Taught</p>
      {#if isEditing}
        <textarea class="textarea textarea-primary" bind:value={concepts}></textarea>
      {:else}
        <p>{concepts}</p>
      {/if}
    </div>
    <div class="mx-2 min-h-32 bg-accent">
      <p>Card Lesson Notes</p>
      {#if isEditing}
        <textarea class="textarea textarea-primary" bind:value={notes}></textarea>
      {:else}
        <p>{notes}</p>
      {/if}
    </div>
  </div>
</div>

<style>
  p {
    color: darkorchid;
  }
</style>
