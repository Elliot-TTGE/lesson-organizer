<script lang='ts'>
    import { onMount } from 'svelte';

    let response: string = $state('');

    onMount(async () => {
        try {
            const res = await fetch('http://localhost:4000/');
            if (res.ok) {
                response = await res.text();
            } else {
                response = 'Failed to fetch data';
            }
        } catch (error) {
            response = 'Error: ' + (error as Error).message;
        }
    });
</script>

<div>
    <p>{response}</p>
</div>