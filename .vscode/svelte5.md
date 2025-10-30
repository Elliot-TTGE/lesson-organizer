Svelte 5 Runes

Use:

    $state<T>(x: T): Reactive state

    $effect(() => {}): Side effects

    $effect.pre(() => {}): Pre-DOM effects

    $derived<T>(): Computed values

    $bindable<T>(): Two-way binding

    $props<T>(): Component props

    onclick={handler}: Event handling

    {#snippet mySnippet(name)}<span>{name}</span>{/snippet} {@render mySnippet(‘tom’)}: Snippets for content projection

Don’t use:

    $: declarations

    on:event syntax

    Svelte stores

    createEventDispatcher()

    export let props

    <slot> elements

    Store $ syntax

Generally speaking, you should not update state inside $effects, as it will make code more convoluted and will often lead to never-ending update cycles.