<script lang="ts">
    let { 
        isLoading = false,
        error = null,
        loadingText = 'Loading...',
        loadingSize = 'loading-lg',
        cardClass = 'card bg-base-200 shadow-xl'
    } = $props<{
        isLoading?: boolean;
        error?: string | null;
        loadingText?: string;
        loadingSize?: string;
        cardClass?: string;
    }>();
</script>

{#if isLoading}
    <div class={cardClass}>
        <div class="card-body items-center">
            <span class="loading loading-spinner {loadingSize} text-primary"></span>
            <p class="text-base-content/70">{loadingText}</p>
        </div>
    </div>
{:else if error}
    <div class="alert alert-error shadow-lg">
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>Error: {error}</span>
    </div>
{/if}
