<script lang="ts">
    type FieldType = 'text' | 'date' | 'number';
    
    let { 
        value,
        type = 'text',
        placeholder = '',
        disabled = false,
        isEditing = $bindable(false),
        isUpdating = false,
        onSave,
        onCancel,
        displayValue = '',
        editIcon = true,
        inputClass = 'input input-bordered input-sm',
        buttonClass = 'btn btn-ghost btn-sm',
        ...inputProps
    } = $props<{
        value: string | number;
        type?: FieldType;
        placeholder?: string;
        disabled?: boolean;
        isEditing?: boolean;
        isUpdating?: boolean;
        onSave?: (value: string | number) => Promise<void> | void;
        onCancel?: () => void;
        displayValue?: string;
        editIcon?: boolean;
        inputClass?: string;
        buttonClass?: string;
        [key: string]: any;
    }>();

    let editingValue = $state(value);

    function startEditing() {
        if (disabled) return;
        editingValue = value;
        isEditing = true;
    }

    function cancelEditing() {
        isEditing = false;
        editingValue = value;
        onCancel?.();
    }

    async function saveChanges() {
        if (editingValue === value) {
            isEditing = false;
            return;
        }
        
        try {
            await onSave?.(editingValue);
            isEditing = false;
        } catch (error) {
            // Handle error if needed - could emit an event or show notification
            console.error('Failed to save:', error);
        }
    }

    function handleKeydown(event: KeyboardEvent) {
        if (event.key === 'Enter') {
            event.preventDefault();
            saveChanges();
        } else if (event.key === 'Escape') {
            event.preventDefault();
            cancelEditing();
        }
    }
</script>

{#if isEditing}
    <div class="flex items-center gap-2">
        <input 
            {type}
            bind:value={editingValue}
            {placeholder}
            class={inputClass}
            disabled={isUpdating}
            onkeydown={handleKeydown}
            {...inputProps}
        />
        <button 
            class="btn btn-success btn-xs"
            disabled={isUpdating}
            onclick={saveChanges}
        >
            {#if isUpdating}
                <span class="loading loading-spinner loading-xs"></span>
            {:else}
                ✓
            {/if}
        </button>
        <button 
            class="btn btn-ghost btn-xs"
            disabled={isUpdating}
            onclick={cancelEditing}
        >
            ✕
        </button>
    </div>
{:else}
    <div class="flex items-center gap-2">
        <span>{displayValue || value}</span>
        {#if editIcon}
            <button 
                class={buttonClass}
                onclick={startEditing}
                {disabled}
                aria-label="Edit field"
            >
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-4 h-4 stroke-current">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                </svg>
            </button>
        {/if}
    </div>
{/if}
