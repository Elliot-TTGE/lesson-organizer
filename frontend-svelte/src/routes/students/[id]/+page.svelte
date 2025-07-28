<script lang="ts">
    import { page } from '$app/stores';
    import StudentCard from "$lib/components/StudentCard.svelte";
    
    // Get the id from the route parameters
    const id = $derived(parseInt($page.params.id));
</script>

<div class="mt-16 top-16">
    <StudentCard 
        studentId={id}
        onStudentUpdated={() => {}}
    />
</div>