<script lang="ts">
  import type { Lesson } from "../../types";
  import { deleteLesson, updateLesson, createLesson } from "../../api/lesson";
  import { lessonState, removeLessonFromState, updateLessonInState } from "$lib/states/lessonState.svelte";
  import { Tipex } from "@friendofsvelte/tipex";
  import type { Editor } from "@tiptap/core";
  import "@friendofsvelte/tipex/styles/Tipex.css";
  import "@friendofsvelte/tipex/styles/ProseMirror.css";
  import "@friendofsvelte/tipex/styles/EditLink.css";
  import "@friendofsvelte/tipex/styles/CodeBlock.css";
  import "$lib/styles/TipexControls.css"

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

  let notesEditor: Editor | undefined = $state();
  const notesContent = $derived(notesEditor?.getHTML());
  let conceptsEditor: Editor | undefined = $state();
  const conceptsContent = $derived(conceptsEditor?.getHTML());
  let planEditor: Editor | undefined = $state();
  const planContent = $derived(planEditor?.getHTML());

  async function handleDelete() {
    if (confirm("Are you sure you want to delete this lesson?")) {
      await deleteLesson(lesson.id);
      removeLessonFromState(lesson.id);
      isEditing = false;
    }
  }

  async function handleConfirm() {
    const datetime = new Date(`${dateInput}T${timeInput}`).toISOString();
    notes = notesContent ?? "";
    concepts = conceptsContent ?? "";
    plan = planContent ?? "";
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

<div class="w-full rounded-lg bg-neutral shadow-md p-4 space-y-4">
  <!-- Action Buttons -->
  <div class="flex justify-end space-x-2">
    {#if isEditing}
      <button onclick={handleConfirm} class="btn btn-success btn-sm">Confirm</button>
      <button onclick={handleCancel} class="btn btn-warning btn-sm">Cancel</button>
    {:else}
      <button onclick={handleCopyToNextWeek} class="btn btn-info btn-sm">
        <img src="/images/icons/arrow-clockwise.svg" alt="Copy Icon" class="w-4 h-4" />
      </button>
      <button onclick={() => isEditing = true} class="btn btn-accent btn-sm">
        <img src="/images/icons/pencil-fill.svg" alt="Edit Icon" class="w-4 h-4" />
      </button>
    {/if}
    <button onclick={handleDelete} class="btn btn-error btn-sm">
      <img src="/images/icons/trash3.svg" alt="Trash Icon" class="w-4 h-4" />
    </button>
  </div>

  <!-- Date Section -->
  {#if isEditing}
    <input type="date" bind:value={dateInput} class="input input-bordered w-36" />
    <input type="time" bind:value={timeInput} class="input input-bordered w-28" />
  {:else}
    <div class="flex items-center justify-between bg-neutral p-4 rounded-lg shadow-sm">
      <div>
        <p class="text-lg font-semibold text-secondary">{weekday}</p>
        <p class="text-sm text-secondary">{date} at {time}</p>
      </div>
    </div>
  {/if}

  <!-- Plan Section -->
  <div class="card bg-neutral shadow-md">
    {#if isEditing}
      <Tipex 
      body={plan}
      controls={true}
      floating={false}
      class="h-[20vh]"
      bind:tipex={planEditor}
      >
      {#snippet head()}
      <div class="text-lg font-bold text-secondary mb-2">
        Today's Plan
      </div>
      {/snippet}
    </Tipex>
    {:else}
      <div class="card-body">
        <h2 class="card-title text-secondary">Today's Plan</h2>
        <div class="prose">{@html plan}</div>
      </div>
    {/if}
  </div>

  <!-- Concepts Taught Section -->
  <div class="card bg-neutral shadow-md">
    {#if isEditing}
      <Tipex 
        body={concepts}
        controls={true}
        floating={false}
        class="h-[20vh]"
        bind:tipex={conceptsEditor}
      >
        {#snippet head()}
          <div class="text-lg font-bold text-secondary mb-2">
            Concepts Taught
          </div>
        {/snippet}
      </Tipex>
    {:else}
      <div class="card-body">
        <h2 class="card-title text-secondary">Concepts Taught</h2>
        <div class="prose">{@html concepts}</div>
      </div>
    {/if}
  </div>

  <!-- Notes Section -->
  <div class="card bg-neutral shadow-md">
    {#if isEditing}
      <Tipex 
        body={notes}
        controls={true}
        floating={false}
        class="h-[20vh]"
        bind:tipex={notesEditor}
      >
        {#snippet head()}
          <div class="text-lg font-bold text-secondary mb-2">
            Lesson Notes
          </div>
        {/snippet}
      </Tipex>
    {:else}
      <div class="card-body">
        <h2 class="card-title text-secondary">Lesson Notes</h2>
        <div class="prose">{@html notes}</div>
      </div>
    {/if}
  </div>
</div>

<style>
  .prose {
    color: var(--color-neutral-content);
  }
</style>
