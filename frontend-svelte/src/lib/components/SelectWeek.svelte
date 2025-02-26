<script lang="ts">
    import { getStartOfWeekInUTC } from "$lib/utils/dateUtils";

    let { startDate = $bindable()}: { startDate: Date } = $props();

    function updateStartDate(newStartDate: Date) {
        startDate = getStartOfWeekInUTC(newStartDate);
    }
</script>

<p>Week:</p>
<input type="date" class="input input-ghost ml-4" value={startDate.toISOString().slice(0, 10)} onblur={(e: Event) => updateStartDate(new Date((e.target as HTMLInputElement).value))}/>
