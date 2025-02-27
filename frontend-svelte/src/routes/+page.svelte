<script lang="ts">
  import { onMount } from "svelte";
  import LessonCard from "$lib/components/LessonCard.svelte";
  import LessonCreateModal from "$lib/components/LessonCreateModal.svelte";
  import SelectWeek from "$lib/components/SelectWeek.svelte";
  import { fetchLessons } from "../api/lesson"
  import { lessonState } from "$lib/states/lessonState.svelte";
  import { lessonWeekStartDate } from "$lib/states/lessonWeekStartDate.svelte";

  onMount(async () => {
    getLessons();
  });

  $effect(() => {
    getLessons();
  })

  async function getLessons(date: Date = lessonWeekStartDate.current) {
    try {
      let newLessons = await fetchLessons({"initial_date": date.toISOString()});
      if (JSON.stringify(lessonState.lessons) !== JSON.stringify(newLessons)) {
        lessonState.lessons = newLessons;
      }
    } catch (error) {
      console.error("Error fetching lessons:", error);
    }
  }
</script>

<div class="bg navbar shadow">
  <div
    class="flex w-full border-4 border-secondary bg-primary px-16 py-4 shadow ring-accent"
  >
    <SelectWeek bind:startDate={lessonWeekStartDate.current} />
    <div class="ml-auto">
      <LessonCreateModal>Create Lesson</LessonCreateModal>
    </div>
  </div>
</div>
<div class="flex flex-row">
  {#each lessonState.lessons as lesson, i (lesson.id)}
    <div class="flex flex-col space-y-4">
      <LessonCard
        bind:lesson={lessonState.lessons[i]}
      />
    </div>
  {/each}
</div>
