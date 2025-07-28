<script lang="ts">
    let { 
        value,
        title,
        icon,
        min = 0,
        max,
        disabled = false,
        isUpdating = false,
        onChange,
        color = 'text-success',
        cardClass = 'card bg-base-100 text-base-content shadow-lg'
    } = $props<{
        value: number;
        title: string;
        icon?: string;
        min?: number;
        max?: number;
        disabled?: boolean;
        isUpdating?: boolean;
        onChange?: (newValue: number) => Promise<void> | void;
        color?: string;
        cardClass?: string;
    }>();

    async function increment() {
        if (disabled || isUpdating || (max !== undefined && value >= max)) return;
        const newValue = value + 1;
        await onChange?.(newValue);
    }

    async function decrement() {
        if (disabled || isUpdating || value <= min) return;
        const newValue = value - 1;
        await onChange?.(newValue);
    }
</script>

<div class={cardClass}>
    <div class="card-body">
        <h3 class="card-title {color} justify-center">
            {#if icon}
                {@html icon}
            {/if}
            {title}
        </h3>
        <div class="flex items-center gap-3">
            <button 
                class="btn btn-circle btn-sm btn-ghost text-error hover:bg-error hover:text-error-content disabled:text-base-content/40 disabled:bg-transparent"
                disabled={disabled || isUpdating || value <= min}
                onclick={decrement}
                aria-label="Decrease {title.toLowerCase()}"
            >
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-4 h-4 stroke-current">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"></path>
                </svg>
            </button>
            <div class="flex-1 text-center">
                <p class="text-lg font-semibold">{value}</p>
            </div>
            <button 
                class="btn btn-circle btn-sm btn-ghost text-success hover:bg-success hover:text-success-content disabled:text-base-content/40 disabled:bg-transparent"
                disabled={disabled || isUpdating || (max !== undefined && value >= max)}
                onclick={increment}
                aria-label="Increase {title.toLowerCase()}"
            >
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-4 h-4 stroke-current">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                </svg>
            </button>
        </div>
    </div>
</div>
