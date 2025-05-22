<script lang="ts">
    import { lessonState } from "$lib/states/lessonState.svelte";
    import { getStartOfWeekInUTC } from "$lib/utils/dateUtils";

    let { startDate = $bindable() }: { startDate: Date } = $props();

    function exportWeek() {
        // Get the start of the week in UTC
        const startOfWeek = getStartOfWeekInUTC(startDate);

        // Flatten the lessons array and filter lessons for the current week
        const lessonsForWeek = lessonState.current
            .flat() // Flatten the array of arrays
            .filter((lesson: { datetime: string }) => {
                const lessonDate = new Date(lesson.datetime);
                return (
                    lessonDate >= startOfWeek &&
                    lessonDate < new Date(startOfWeek.getTime() + 7 * 24 * 60 * 60 * 1000)
                );
            });

        // Create a JSON blob
        const jsonBlob = new Blob([JSON.stringify(lessonsForWeek, null, 2)], {
            type: "application/json",
        });

        // Create a download link
        const link = document.createElement("a");
        link.href = URL.createObjectURL(jsonBlob);
        link.download = `lessons-week-${startOfWeek.toISOString().split("T")[0]}.json`;
        link.click();

        // Clean up the URL object
        URL.revokeObjectURL(link.href);
    }

    function exportWeekAsCSV() {
        const startOfWeek = getStartOfWeekInUTC(startDate);
        const lessonsForWeek = lessonState.current.flat().filter((lesson: { datetime: string }) => {
            const lessonDate = new Date(lesson.datetime);
            return (
                lessonDate >= startOfWeek &&
                lessonDate < new Date(startOfWeek.getTime() + 7 * 24 * 60 * 60 * 1000)
            );
        });

        const headers = ["id", "datetime", "created_date", "students", "plan", "concepts", "notes"];
        const rows = lessonsForWeek.map((lesson) => [
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
        link.download = `lessons-week-${startOfWeek.toISOString().split("T")[0]}.csv`;
        link.click();
        URL.revokeObjectURL(link.href);
    }
</script>

<button class="btn btn-secondary" onclick={exportWeekAsCSV}>Export Week</button>