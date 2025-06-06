<script lang="ts">
    import { lessonState } from "$lib/states/lessonState.svelte";
    import { getStartOfWeekInUTC } from "$lib/utils/dateUtils";
    import Papa from "papaparse";

    let { startDate = $bindable() }: { startDate: Date } = $props();

    function getExportData() {
        return lessonState.current.flat().map((lesson) => ({
            id: lesson.id,
            datetime: new Date(lesson.datetime).toISOString(),
            created_date: lesson.created_date,
            students: lesson.students,
            plan: lesson.plan,
            concepts: lesson.concepts,
            notes: lesson.notes,
        }));
    }

    function triggerDownload(blob: Blob, extension: string, mimeType: string) {
        const dateStr = getStartOfWeekInUTC(startDate).toISOString().split("T")[0];
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = `lessons-week-${dateStr}.${extension}`;
        link.click();
        URL.revokeObjectURL(link.href);
    }

    function exportWeekAsJSON() {
        const data = getExportData();
        const jsonBlob = new Blob([JSON.stringify(data, null, 2)], {
            type: "application/json",
        });
        triggerDownload(jsonBlob, "json", "application/json");
    }

    function exportWeekAsCSV() {
        const data = getExportData();
        const csv = Papa.unparse(data, { quotes: true });
        const csvBlob = new Blob([csv], { type: "text/csv" });
        triggerDownload(csvBlob, "csv", "text/csv");
    }
</script>

<div class="dropdown">
    <div tabindex="0" role="button" class="btn btn-secondary">Export Week</div>
    <ul class="dropdown-content z-[1] menu p-2 shadow bg-secondary rounded-box w-30">
        <li>
            <button class="btn btn-ghost btn-sm w-full justify-start" onclick={exportWeekAsJSON}>
                JSON
            </button>
        </li>
        <li>
            <button class="btn btn-ghost btn-sm w-full justify-start" onclick={exportWeekAsCSV}>
                CSV
            </button>
        </li>
    </ul>
</div>