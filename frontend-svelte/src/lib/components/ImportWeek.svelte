<script lang="ts">
    import type { Lesson, Student } from "../../types";
    import { createLesson, type LessonCreateFields } from "../../api/lesson";
    import { addLessonToState } from "$lib/states/lessonState.svelte";
    import Papa from "papaparse";
    import LessonCreateModal from "./LessonCreateModal.svelte";

    function parseCSV(csv: string): LessonCreateFields[] {
        const result = Papa.parse(csv, { header: true, skipEmptyLines: true });
        if (result.errors.length > 0) {
            console.error("CSV parsing errors:", result.errors);
            return [];
        }
        return (result.data as Record<string, string>[]).map(obj => ({
            datetime: obj.datetime ? new Date(obj.datetime).toISOString() : new Date().toISOString(),
            plan: obj.plan || "",
            concepts: obj.concepts || "",
            notes: obj.notes || ""
        }));
    }

    function parseJSON(json: string): LessonCreateFields[] {
        try {
            const arr = JSON.parse(json);
            if (Array.isArray(arr)) {
                return arr.map(l => ({
                    datetime: l.datetime ? new Date(l.datetime).toISOString() : new Date().toISOString(),
                    plan: l.plan || "",
                    concepts: l.concepts || "",
                    notes: l.notes || ""
                }));
            }
        } catch {
        }
        return [];
    }

    async function importWeekFromFile() {
        const input = document.createElement("input");
        input.type = "file";
        input.accept = ".csv,application/json,text/csv";
        input.click();

        input.onchange = async () => {
            if (!input.files?.length) return;
            const file = input.files[0];
            const text = await file.text();
            let newLessons: LessonCreateFields[] = [];

            if (file.name.endsWith(".csv")) {
                newLessons = parseCSV(text);
            } else if (file.name.endsWith(".json")) {
                newLessons = parseJSON(text);
            }

            for (const lesson of newLessons) {
                try {
                    const created = await createLesson(lesson, []); // Pass empty student_ids array
                    addLessonToState(created);
                } catch (e) {
                    console.error("Error creating lesson:", e);
                }
            }
        };
    }
</script>

<input type="file" class="file-input file-input-secondary file-input-sm" accept=".csv,application/json" style="display:none" id="importWeekInput" />
<button class="btn btn-secondary" onclick={importWeekFromFile}>Import Week</button>