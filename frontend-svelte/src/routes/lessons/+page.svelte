<script lang="ts">
  import { onMount } from "svelte";
  import LessonCard from "$lib/components/LessonCard.svelte";
  import LessonCreateModal from "$lib/components/LessonCreateModal.svelte";
  import SelectWeek from "$lib/components/SelectWeek.svelte";
  import { fetchCurrentWeekLessons, lessonState } from "$lib/states/lessonState.svelte";
  import { lessonWeekStartDate } from "$lib/states/lessonWeekStartDate.svelte";
  import ExportWeek from "$lib/components/ExportWeek.svelte";
  import ImportWeek from "$lib/components/ImportWeek.svelte";

  onMount(async () => {
    await fetchCurrentWeekLessons();
  });

  $effect(() => {
    fetchCurrentWeekLessons();
  });
</script>

<div class="bg navbar shadow-sm">
  <div
    class="flex w-full border-4 border-secondary bg-primary px-4 py-4 shadow-sm ring-accent gap-2"
  >
    <SelectWeek bind:startDate={lessonWeekStartDate.current} />
    <ExportWeek bind:startDate={lessonWeekStartDate.current}/>
    <ImportWeek />
    <div class="ml-auto">
      <LessonCreateModal>Create Lesson</LessonCreateModal>
    </div>
  </div>
</div>
<div class="flex flex-row flex-wrap gap-2 p-2">
  {#each lessonState.current as lessons}
    {#if lessons.length > 0}
      <div class="flex flex-col space-y-4 grow-0 shrink-0 sm:basis-[calc(50%_-_1rem)] md:basis-[calc(33.333%_-_1rem)] lg:basis-[calc(16.666%_-_0.5rem)]">
        <h2 class="text-lg font-bold">{new Date(lessons[0].datetime).toLocaleDateString("en-US", {weekday: "long"})}</h2>
        {#each lessons as lesson, i (lesson.id)}
          <LessonCard bind:lesson={lessons[i]} />
        {/each}
      </div>
    {/if}
  {/each}
</div>
