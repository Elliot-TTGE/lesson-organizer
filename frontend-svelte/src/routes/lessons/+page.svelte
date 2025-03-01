<script lang="ts">
  import { onMount } from "svelte";
  import LessonCard from "$lib/components/LessonCard.svelte";
  import LessonCreateModal from "$lib/components/LessonCreateModal.svelte";
  import SelectWeek from "$lib/components/SelectWeek.svelte";
  import { fetchCurrentWeekLessons, lessonState } from "$lib/states/lessonState.svelte";
  import { lessonWeekStartDate } from "$lib/states/lessonWeekStartDate.svelte";

  onMount(async () => {
    await fetchCurrentWeekLessons();
  });

  $effect(() => {
    fetchCurrentWeekLessons();
  });
</script>

<div class="bg navbar shadow">
  <div
    class="flex w-full border-4 border-secondary bg-primary px-4 py-4 shadow ring-accent"
  >
    <SelectWeek bind:startDate={lessonWeekStartDate.current} />
    <div class="ml-auto">
      <LessonCreateModal>Create Lesson</LessonCreateModal>
    </div>
  </div>
</div>
<div class="flex flex-row flex-wrap">
  {#each lessonState.current as lessons}
    {#if lessons.length > 0}
      <div class="flex flex-col space-y-4 m-2 flex-1">
        <h2 class="text-lg font-bold">{new Date(lessons[0].datetime).toLocaleDateString("en-US", {weekday: "long"})}</h2>
        {#each lessons as lesson, i (lesson.id)}
          <LessonCard bind:lesson={lessons[i]} />
        {/each}
      </div>
    {/if}
  {/each}
</div>

<style>
  .flex-1 {
    flex: 1 1 0;
    min-width: 15rem; /* Adjust this value as needed */
  }
</style>
