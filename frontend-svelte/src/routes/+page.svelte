<script lang='ts'>
    import Lesson from '$lib/components/Lesson.svelte'
    import LessonCreateModal from '$lib/components/LessonCreateModal.svelte'
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
  <div class='flex flex-col space-y-4'>
	<Lesson 
	weekday="Monday"
	date="01/13/25"
	time='1:00 PM'
	student="Jose"
	plan='plan'
	/>
	<Lesson 
	weekday="Monday"
	date="01/13/25"
	time='2:00 PM'
	student="Laura"
	plan='plan'
	/>
	<Lesson 
	weekday="Monday"
	date="01/13/25"
	time='3:00 PM'
	student="Benjamin"
	plan='plan'
	/>
  </div>
  <div class='flex flex-col space-y-4'>
	<Lesson 
	weekday="Tuesday"
	date="01/14/25"  
	time='1:00 PM'
	student='Youstos'
	plan='plan'
	/>
  </div>
</div>