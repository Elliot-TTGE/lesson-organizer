<script lang="ts">
  import { onMount } from "svelte";
  import LessonCard from "$lib/components/LessonCard.svelte";
  import LessonCreateModal from "$lib/components/LessonCreateModal.svelte";
  import type { Lesson } from "../types";
  import { fetchLessons } from "../controller"

  let lessons: Lesson[] = [];

  onMount(async () => {
    try {
      lessons = await fetchLessons();
    } catch (error) {
      console.error("Error fetching lessons:", error);
    }
  });
</script>

<div class="bg navbar shadow">
  <div
    class="flex w-full border-4 border-secondary bg-primary px-16 py-4 shadow ring-accent"
  >
    <p>Week Of:</p>
    <div class="ml-4">01/13/24</div>
    <div class="ml-auto">
      <LessonCreateModal>Create Lesson</LessonCreateModal>
    </div>
  </div>
</div>
<div class="flex flex-row">
  {#each lessons as lesson}
    <div class="flex flex-col space-y-4">
      <LessonCard
        lesson={lesson}
      />
    </div>
  {/each}
</div>
