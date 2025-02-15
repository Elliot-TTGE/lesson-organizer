<script lang='ts'>
    import { fetchStudents } from "../../controller";
    import { onMount } from "svelte";
    import type { Student } from "../../types";

    let students: Student[];

    onMount( async () => {
        students = await fetchStudents({'id': '1'});
    });

</script>
{#each students as student}
    <h1>{student.name} {student.id}</h1>
{/each}
