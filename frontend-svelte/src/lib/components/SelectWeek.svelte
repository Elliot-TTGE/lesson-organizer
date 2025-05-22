<script lang="ts">
    import { getStartOfWeekInUTC } from "$lib/utils/dateUtils";

    let { startDate = $bindable()}: { startDate: Date } = $props();

    function changeWeek(offset: number) {
        const newStartDate = new Date(startDate);
        newStartDate.setDate(newStartDate.getDate() + offset);
        startDate = getStartOfWeekInUTC(newStartDate);
    }
</script>

<div class="flex items-center">
    <button class="btn btn-secondary" onclick={() => changeWeek(-7)}>&lt;</button>
    <input 
        type="date" 
        class="input mx-2 bg-secondary" 
        value={startDate.toISOString().slice(0, 10)} 
        onblur={(e: Event) => {
        const value = (e.target as HTMLInputElement).value;
        if (value) {
            startDate = getStartOfWeekInUTC(new Date((e.target as HTMLInputElement).value));
        } else {
            startDate = getStartOfWeekInUTC(new Date());
        }
        }}
    />
    <button class="btn btn-secondary" onclick={() => changeWeek(7)}>&gt;</button>
</div>
