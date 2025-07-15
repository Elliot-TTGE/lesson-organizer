<script lang="ts">
    import { type Student } from "../../types";
    import { fetchStudent } from "../../api/student";
    import { onMount } from "svelte";
    import { 
        getLatestLevelId, 
        getLatestStatusId, 
        getLastLessonFromStudent, 
        formatLessonDateTime, 
        getStudentFullName, 
        formatStudentDate 
    } from "../utils";
    import { 
        statusState, 
        refreshStatuses, 
        getStatusNameById,
        levelState,
        refreshLevels,
        getLevelDisplayById
    } from "../states";
    import TipexEditor from "./TipexEditor.svelte";

    let { studentId, onStudentUpdated } = $props<{ 
        studentId: number; 
        onStudentUpdated?: (student: Student) => void;
    }>();

    let student = $state<Student | null>(null);
    let isLoading = $state(true);
    let error = $state<string | null>(null);

    onMount(async () => {
        try {
            // Fetch student data and ensure states are loaded
            const [fetchedStudent] = await Promise.all([
                fetchStudent(studentId),
                // Ensure states are loaded (these are no-op if already loaded)
                statusState.statuses.length === 0 ? refreshStatuses() : Promise.resolve(),
                levelState.levels.length === 0 ? refreshLevels() : Promise.resolve()
            ]);
            
            student = fetchedStudent;
            
            isLoading = false;
        } catch (err) {
            error = err instanceof Error ? err.message : 'Failed to fetch student data';
            isLoading = false;
        }
    });

    function handleUpdate() {
        // This would be called when student data is updated in the modal
        // For now, we'll just refresh the data
        if (student && onStudentUpdated) {
            onStudentUpdated(student);
        }
    }

    function getCurrentStatusDisplay(): string {
        if (!student) return '-';
        
        const latestStatusId = getLatestStatusId(student);
        if (!latestStatusId) {
            return '-';
        }

        return getStatusNameById(latestStatusId) ?? '-';
    }

    function getLastLessonDisplay(): string {
        if (!student) return '-';
        
        const lastLesson = getLastLessonFromStudent(student);
        return lastLesson ? formatLessonDateTime(lastLesson) : '-';
    }

    function getCurrentLevelDisplay(): string {
        if (!student) return 'Not set';
        
        const latestLevelId = getLatestLevelId(student);
        if (!latestLevelId) {
            return 'Not set';
        }

        return getLevelDisplayById(latestLevelId) ?? 'Not set';
    }
</script>

{#if isLoading}
    <div class="flex justify-center p-8">
        <span class="loading loading-spinner loading-lg"></span>
    </div>
{:else if error}
    <div class="alert alert-error">
        <span>Error: {error}</span>
    </div>
{:else if student}
    <div class="bg-neutral text-neutral-content">
        <h1 class="text-4xl">{getStudentFullName(student)}</h1>
        <div class="flex flex-row">
            <div class="flex-col">
                <h2 class="text-2xl">
                    Date Started: {formatStudentDate(student.date_started)}
                </h2>
                <div class="flex flex-row gap-4"> 
                    <h2 class="text-2xl">
                        Current Level: {getCurrentLevelDisplay()}
                    </h2>
                </div>    
            </div>
            <div class="flex-col">
                <h2 class="text-2xl">
                    Current Status: {getCurrentStatusDisplay()}
                </h2>
                <h2 class="text-2xl">
                    Last Lesson: {getLastLessonDisplay()}
                </h2>
                <h2 class="text-2xl">
                    Desired Classes per Week: {student.classes_per_week ?? "Not Set"}
                </h2>
            </div>
        </div>
        <div class="flex flex-row mt-6">
            <div class="flex flex-col gap-4 w-1/2">
                <TipexEditor heading="General Notes" bind:body={student.notes_general}></TipexEditor>
                <TipexEditor heading="Future Plans" bind:body={student.notes_future}></TipexEditor>
            </div>
            <div class="flex flex-col gap-4 w-1/2">
                <TipexEditor heading="Strengths" bind:body={student.notes_strengths}></TipexEditor>
                <TipexEditor heading="Areas of Improvement" bind:body={student.notes_weaknesses}></TipexEditor>
            </div>
        </div>
    </div>
{/if}