<script lang='ts'>
    import { onMount } from 'svelte';
    import LessonCard from '$lib/components/LessonCard.svelte';
    import LessonCreateModal from '$lib/components/LessonCreateModal.svelte';
    import type { Lesson } from '../types';

    let lessons: Lesson[] = [];
    
    onMount(async () => {
        try {
            const response = await fetch('http://localhost:4000/api/lessons');
            if (!response.ok) {
                throw new Error('Failed to fetch lessons');
            }
            const data: Lesson[] = await response.json();
            lessons = data;
            console.log(lessons);
        } catch (error) {
            console.error('Error fetching lessons:', error);
        }
    });
</script>

<div class='navbar bg shadow'>
  <div class='flex bg-primary ring-accent py-4 px-16 w-full shadow border-4 border-secondary'>
    <p>Week Of: </p>
    <div class="ml-4">01/13/24</div>
    <div class='ml-auto'>
      <LessonCreateModal>
        Create Lesson
      </LessonCreateModal>
    </div>
  </div>
</div>
<div class='flex flex-row'>
  {#each lessons as lesson}
    <div class='flex flex-col space-y-4'>
      <LessonCard 
        weekday={new Date(lesson.datetime).toLocaleDateString('en-US', { weekday: 'long' })}
        date={new Date(lesson.datetime).toLocaleDateString()}
        time={new Date(lesson.datetime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        student={lesson.students.map(student => student.name).join(', ')}
        plan={lesson.plan}
        concepts={lesson.concepts_taught}
        notes={lesson.additional_notes}
      />
    </div>
  {/each}
</div>