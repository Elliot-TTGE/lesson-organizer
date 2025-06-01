<script lang="ts">
    const { student } = $props<{ student: Number | null }>();
</script>

<div class="bg-neutral text-neutral-content">    
    <h1 class="text-4xl">student.name</h1>
    <h2 class="text-2xl">Date Started: student.date_started</h2>
    <div class="flex flex-row gap-4"> 
        <h2 class="text-2xl">Curriculum Name: curriculum.name</h2>
        <h2 class="text-2xl">Level: level.name</h2>
    </div>
    <div class="flex flex-row mt-6">
        <div class="flex flex-col gap-4 w-1/2">
            <div class="bg-white w-1/2 h-1/2 text-2xl">General Notes</div>
            <div class="bg-white w-1/2 h-1/2 text-2xl">Strengths</div>
        </div>
        <div class="w-1/2 text-2xl flex flex-col gap-4">
            <div>Quizzes</div>
            <div class="ml-4">Enter new quiz</div>
            <div class="flex flex-row gap-4">
                <div class="ml-8">Date:</div>
                <input class="bg-white" type="date"/>
            </div>
            <div class="flex flex-row gap-4">
                <div class="ml-8">Curriculum:</div>
                <input class="bg-white w-32" type="text"/>
                <div class="ml-8">Level:</div>
                <input class="bg-white w-32" type="text"/>
            </div>
            <div class="flex flex-row gap-4">
                <div class="ml-8">Score:</div>
                <input class="bg-white w-32" type="text"/>
                <div> out of </div>
                <input class="bg-white w-32" type="text"/>
            </div>
        </div>
    </div>

</div>