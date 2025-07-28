<script lang="ts">
    let { 
        title,
        value,
        icon,
        color = 'text-accent',
        cardClass = 'card bg-base-100 text-base-content shadow-lg',
        centerAlign = true
    } = $props<{
        title: string;
        value: string | number;
        icon?: string;
        color?: string;
        cardClass?: string;
        centerAlign?: boolean;
    }>();
</script>

<div class={cardClass}>
    <div class="card-body" class:text-center={centerAlign}>
        <h3 class="card-title {color}" class:justify-center={centerAlign}>
            {#if icon}
                {@html icon}
            {/if}
            {title}
        </h3>
        <p class="text-lg font-semibold">{value}</p>
    </div>
</div>
