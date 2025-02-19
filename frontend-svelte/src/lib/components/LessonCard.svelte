<script lang="ts">
  import type { Lesson } from "../../types";
  import { deleteLesson } from "../../api/lesson";
  import { lessonState } from "$lib/states/lessonState.svelte";

  let { lesson }: { lesson: Lesson } = $props();

  let weekday: string = new Date(lesson.datetime).toLocaleDateString("en-US", {
    weekday: "long",
  });
  let date: string = new Date(lesson.datetime).toLocaleDateString("en-US");
  let time: string = new Date(lesson.datetime).toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
  });
  let student: string = lesson.students.map((student) => (student.first_name + ' ' + student.last_name)).join(", ");
  let plan: string = lesson.plan;
  let concepts: string = lesson.concepts;
  let notes: string = lesson.notes;

  async function handleDelete() {
    if (confirm("Are you sure you want to delete this lesson?")) {
      await deleteLesson(lesson.id);
      lessonState.lessons = lessonState.lessons.filter(l => l.id !== lesson.id);
    }
  }
</script>

<div class="m-4 w-64 rounded bg-neutral">
  <div class="flex justify-end space-x-2 mb-2">
    <button onclick={handleDelete} class="btn btn-ghost btn-sm text-error items-center p-1">
      <span class="mr-2">Delete</span>
    </button>
  </div>
  <div class="flex flex-col space-y-2 p-2">
    <p>{weekday}</p>
    <p>{date}:</p>
    <p>{time}:</p>
    <p>{student}</p>
  </div>
  <div class="flex flex-col space-y-2 p-2">
    <div>
      <p>Today's plan:</p>
      <p class="min-h-24">
        {plan}
      </p>
    </div>
    <div class="mx-2 min-h-32 bg-accent">
      <p>Card Concepts Taught</p>
      <p>{concepts}</p>
    </div>
    <div class="mx-2 min-h-32 bg-accent">
      <p>Card Lesson Notes</p>
      <p>{notes}</p>
    </div>
  </div>
</div>

<style>
  p {
    color: darkorchid;
  }
</style>
