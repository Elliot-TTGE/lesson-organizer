<script lang="ts">
    import type { ComponentProps } from 'svelte';

    type HistoryItem = {
        id: number;
        date: string;
        displayText: string;
        isDeletable?: boolean;
    };

    type DropdownOption = {
        id: number;
        name: string;
        disabled?: boolean;
    };

    let { 
        title,
        icon,
        historyItems,
        dropdownOptions,
        currentItemId,
        isUpdating = false,
        isDeleting = false,
        deletingItemId = null,
        onItemChange,
        onItemDelete,
        formatDate,
        emptyStateText = 'No history available',
        emptyStateSubtext = 'Changes will appear here',
        changeLabel = 'Change',
        selectLabel = 'Select New Item'
    } = $props<{
        title: string;
        icon?: string;
        historyItems: HistoryItem[];
        dropdownOptions: DropdownOption[];
        currentItemId: number | null;
        isUpdating?: boolean;
        isDeleting?: boolean;
        deletingItemId?: number | null;
        onItemChange?: (newItemId: number) => Promise<void> | void;
        onItemDelete?: (itemId: number) => Promise<void> | void;
        formatDate?: (date: string) => string;
        emptyStateText?: string;
        emptyStateSubtext?: string;
        changeLabel?: string;
        selectLabel?: string;
    }>();

    async function handleItemChange(event: Event) {
        const target = event.currentTarget as HTMLSelectElement;
        const newItemId = parseInt(target.value);
        if (newItemId && newItemId !== currentItemId) {
            await onItemChange?.(newItemId);
        }
        target.value = ''; // Reset dropdown
    }

    async function handleItemDelete(itemId: number) {
        await onItemDelete?.(itemId);
    }

    const defaultFormatDate = (date: string) => {
        return new Date(date).toLocaleDateString();
    };

    const formatDateFn = formatDate || defaultFormatDate;
</script>

<div class="card bg-base-100 shadow-lg">
    <div class="card-body">
        <h3 class="card-title text-base-content mb-4">
            {#if icon}
                {@html icon}
            {/if}
            {title}
        </h3>
        
        <!-- Change Item Dropdown -->
        <div class="mb-6">
            <label class="label" for="{title.toLowerCase().replace(/\s+/g, '-')}-select">
                <span class="label-text text-base-content font-medium">{changeLabel} {title}:</span>
            </label>
            <select 
                id="{title.toLowerCase().replace(/\s+/g, '-')}-select"
                class="select select-bordered w-full bg-base-100 text-base-content"
                disabled={isUpdating}
                onchange={handleItemChange}
            >
                <option value="">{selectLabel}</option>
                {#each dropdownOptions as option}
                    <option value={option.id} disabled={option.disabled || option.id === currentItemId}>
                        {option.name}
                    </option>
                {/each}
            </select>
            {#if isUpdating}
                <span class="loading loading-spinner loading-sm ml-2 text-base-content"></span>
            {/if}
        </div>

        <!-- History List -->
        <div class="max-h-64 overflow-y-auto overflow-x-hidden">
            {#if historyItems && historyItems.length > 0}
                <div class="timeline timeline-vertical timeline-compact">
                    {#each historyItems.slice().reverse() as item}
                        <li>
                            <div class="timeline-middle">
                                <div class="w-2 h-2 bg-info rounded-full"></div>
                            </div>
                            <div class="timeline-end mb-6 flex justify-between items-center w-full">
                                <div class="flex-1 pr-3">
                                    <div class="text-sm text-base-content/80 font-medium mb-1">{formatDateFn(item.date)}</div>
                                    <div class="font-semibold text-base-content">{item.displayText}</div>
                                </div>
                                {#if item.isDeletable !== false}
                                    <button 
                                        class="btn btn-ghost btn-xs text-error hover:bg-error hover:text-error-content border border-error/20 flex-shrink-0 mr-2"
                                        disabled={deletingItemId === item.id}
                                        onclick={() => handleItemDelete(item.id)}
                                        aria-label="Delete {title.toLowerCase()} entry"
                                    >
                                        {#if deletingItemId === item.id}
                                            <span class="loading loading-spinner loading-xs"></span>
                                        {:else}
                                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                                            </svg>
                                        {/if}
                                    </button>
                                {/if}
                            </div>
                        </li>
                    {/each}
                </div>
            {:else}
                <div class="text-center text-base-content/60 py-8">
                    <p class="font-medium">{emptyStateText}</p>
                    <p class="text-sm">{emptyStateSubtext}</p>
                </div>
            {/if}
        </div>
    </div>
</div>
