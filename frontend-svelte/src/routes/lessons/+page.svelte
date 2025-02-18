<script lang='ts'>
    import { fetchStudents } from "../../api/student";
    import { onMount } from "svelte";
    import type { Student } from "../../types";

    let students: Student[];

    onMount( async () => {
        students = await fetchStudents({'id': '1'});
    });

</script>
{#each students as student}
    <h1>{student.first_name + ' ' + student.last_name} {student.id}</h1>
{/each}
