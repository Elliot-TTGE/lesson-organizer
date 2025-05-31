<script lang="ts">
    import type { Student } from "../../types";

    let students: Number[] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 2, 3, 4, 5, 6, 7, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 2, 3, 4, 5, 6, 7, 8];

    function onMount() {
        // Fetch all students from database.
    }
</script>

<div class="sticky z-10 mt-16 top-16 bg-base-200">
    <div class="flex bg-base-200">
        <div class="flex">
            <!-- Options for student search -->
        </div>
        <fieldset class="fieldset ml-auto mr-[2rem] w-[25rem] mb-2">
            <p class="fieldset-legend">Find a student</p>
            <label class="input input-accent">
                <svg class="h-[1em] opacity-50" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                    <g
                    stroke-linejoin="round"
                    stroke-linecap="round"
                    stroke-width="2.5"
                    fill="none"
                    stroke="currentColor"
                    >
                        <circle cx="11" cy="11" r="8"></circle>
                        <path d="m21 21-4.3-4.3"></path>
                    </g>
                </svg>
                <input type="search" placeholder="Search"/>
            </label>
        </fieldset>
    </div>

    <table class="table border bg-base-200 border-base-200">
        <thead class="sticky z-10 top-32">
            <tr>
                <th>#</th>
                <th>Name</th>
                <th>Level</th>
                <th>Next Lesson</th>
                <th>Last Lesson</th>
                <th>Last Quiz</th>
            </tr>
        </thead>
    </table>
</div>
<div class="overflow-y-auto">
    <table class="table table-zebra border border-base-200">
        <tbody>
            {#each students as student}
                <tr>
                    <td>{student}</td>
                    <td>student.name</td>
                    <td>student.level</td>
                    <td>student.nextLesson</td>
                    <td>student.lastLesson</td>
                    <td>student.lastQuiz</td>
                    <td>
                        <button class="btn btn-primary btn-sm">Edit</button>
                    </td>
                </tr>
            {/each}
        </tbody>
    </table>
</div>