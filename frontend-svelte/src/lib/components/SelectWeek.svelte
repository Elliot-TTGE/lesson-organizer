<script lang="ts">
    let { startDate = $bindable()}: { startDate: Date } = $props();

</script>

<p>Week:</p>
<input type="date" class="input input-ghost ml-4" value={startDate.toISOString().slice(0, 10)} onblur={(e: Event) => startDate = new Date((e.target as HTMLInputElement).value)}/>
