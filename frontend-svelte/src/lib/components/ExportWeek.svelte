<script lang="ts">
    import { lessonState } from "$lib/states/lessonState.svelte";
    import { getStartOfWeekInUTC } from "$lib/utils/dateUtils";

    let { startDate = $bindable() }: { startDate: Date } = $props();

    function exportWeekAsJSON() {
        const jsonBlob = new Blob([JSON.stringify(lessonState.current.flat(), null, 2)], {
            type: "application/json",
        });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(jsonBlob);
        link.download = `lessons-week-${getStartOfWeekInUTC(startDate).toISOString().split("T")[0]}.json`;
        link.click();
        URL.revokeObjectURL(link.href);
    }

    function exportWeekAsCSV() {
        const headers = ["id", "datetime", "created_date", "students", "plan", "concepts", "notes"];
        const rows = lessonState.current.flat().map((lesson) => [
            lesson.id || "",
            new Date(lesson.datetime).toISOString(),
            lesson.created_date || "",
            lesson.students || "",
            lesson.plan || "",
            lesson.concepts || "",
            lesson.notes || "",
        ]);
        const csvContent = [headers, ...rows].map((row) => row.join(",")).join("\n");
        const blob = new Blob([csvContent], { type: "text/csv" });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = `lessons-week-${getStartOfWeekInUTC(startDate).toISOString().split("T")[0]}.csv`;
        link.click();
        URL.revokeObjectURL(link.href);
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