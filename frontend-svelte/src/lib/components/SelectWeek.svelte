<script lang="ts">
    let { startDate = $bindable()}: { startDate: Date } = $props();

    function updateStartDate(newStartDate: Date) {
        // Adjust to get week day belongs to
        const day = newStartDate.getUTCDay();
        const diff = newStartDate.getUTCDate() - day;
        const sunday = new Date(newStartDate.setDate(diff));
        
        // Set time to midnight local time
        sunday.setHours(0, 0, 0, 0);
        
        // Convert to UTC
        const utcSunday = new Date(Date.UTC(sunday.getFullYear(), sunday.getMonth(), sunday.getDate(), 0, 0, 0));
        
        startDate = utcSunday;
    }
</script>

<p>Week:</p>
<input type="date" class="input input-ghost ml-4" value={startDate.toISOString().slice(0, 10)} onblur={(e: Event) => updateStartDate(new Date((e.target as HTMLInputElement).value))}/>
