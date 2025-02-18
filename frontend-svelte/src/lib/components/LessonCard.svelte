<script lang="ts">
  import type { Lesson } from "../../types";

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

</script>

<div class="m-4 w-64 rounded bg-neutral">
  <div class="flex flex-col space-y-2 p-2">
    <p>{weekday}</p>
    <p>{date}:</p>
    <p>{time}:</p>
    <p>{student}</p>
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
