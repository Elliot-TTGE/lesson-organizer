<script lang="ts">
    import type { Lesson, Student } from "../../types";
    import { createLesson } from "../../api/lesson";
    import { addLessonToState } from "$lib/states/lessonState.svelte";
    import Papa from "papaparse";

    function parseCSV(csv: string): Partial<Lesson>[] {
        const result = Papa.parse(csv, { header: true, skipEmptyLines: true });
        if (result.errors.length > 0) {
            console.error("CSV parsing errors:", result.errors);
            return [];
        }
        return (result.data as Record<string, string>[]).map(obj => ({
            id: obj.id ? Number(obj.id) : undefined,
            datetime: obj.datetime ? new Date(obj.datetime).toISOString() : "",
            created_date: obj.created_date ? new Date(obj.created_date).toISOString() : "",
            students: [],
            plan: obj.plan || "",
            concepts: obj.concepts || "",
            notes: obj.notes || ""
        }));
    }

    function parseJSON(json: string): Partial<Lesson>[] {
        try {
            const arr = JSON.parse(json);
            if (Array.isArray(arr)) {
                return arr.map(l => ({
                    ...l,
                    datetime: l.datetime ? new Date(l.datetime).toISOString() : "",
                    created_date: l.created_date ? new Date(l.created_date).toISOString() : "",
                    students: Array.isArray(l.students) ? l.students : []
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
            let newLessons: Partial<Lesson>[] = [];

            if (file.name.endsWith(".csv")) {
                newLessons = parseCSV(text);
            } else if (file.name.endsWith(".json")) {
                newLessons = parseJSON(text);
            }

            for (const lesson of newLessons) {
                try {
                    const created = await createLesson(lesson);
                    addLessonToState(created);
                } catch (e) {

                }
            }
        };
    }
</script>

<input type="file" class="file-input file-input-secondary file-input-sm" accept=".csv,application/json" style="display:none" id="importWeekInput" />
<button class="btn btn-secondary" onclick={importWeekFromFile}>Import Week</button>