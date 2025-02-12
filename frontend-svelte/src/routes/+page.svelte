<script lang="ts">
  import { onMount } from "svelte";
  import LessonCard from "$lib/components/LessonCard.svelte";
  import LessonCreateModal from "$lib/components/LessonCreateModal.svelte";
  import type { Lesson } from "../types";

  let lessons: Lesson[] = [];

  async function fetchLessons() {
    try {
      const response = await fetch("http://localhost:4000/api/lessons");
      if (!response.ok) {
        throw new Error("Failed to fetch lessons");
      }
      const data: Lesson[] = await response.json();
      lessons = data;
    } catch (error) {
      console.error("Error fetching lessons:", error);
    }
  }

  onMount(fetchLessons);

  function handleCreate() {
    fetchLessons(); // Refetch lessons after creating a new one
  }
</script>

<div class="bg navbar shadow">
  <div
    class="flex w-full border-4 border-secondary bg-primary px-16 py-4 shadow ring-accent"
  >
    <p>Week Of:</p>
    <div class="ml-4">01/13/24</div>
    <div class="ml-auto">
      <LessonCreateModal onCreate={handleCreate}>
        Create Lesson
      </LessonCreateModal>
    </div>
  </div>
</div>
<div class="flex flex-row">
  {#each lessons as lesson}
    <div class="flex flex-col space-y-4">
      <LessonCard
        weekday={new Date(lesson.datetime).toLocaleDateString("en-US", {
          weekday: "long",
        })}
        date={new Date(lesson.datetime).toLocaleDateString()}
        time={new Date(lesson.datetime).toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        })}
        student={lesson.students.map((student) => student.name).join(", ")}
        plan={lesson.plan}
        concepts={lesson.concepts_taught}
        notes={lesson.additional_notes}
      />
    </div>
  {/each}
</div>
