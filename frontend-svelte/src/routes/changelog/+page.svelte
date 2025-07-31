<script lang="ts">
    import Navbar from "$lib/components/Navbar.svelte";
    import changelog from '$lib/data/changelog.json'
</script>

<Navbar />
<div class="flex justify-center items-center min-h-screen text-base-content">
  <div class="card bg-base-200 shadow-xl w-full max-w-3xl top-16">
    <div class="card-body">
      <h1 class="card-title text-primary text-center text-3xl">Changelog</h1>
      {#each changelog as entry, index}
        <div class="mt-6">
          <h2 class="text-accent text-xl font-bold">
            {entry.version} - <span class="text-neutral">{entry.date}</span>
          </h2>
          <ul class="list-disc list-inside mt-2 text-accent">
            {#each entry.changes as change}
              <li>{change}</li>
            {/each}
          </ul>
          {#if index < changelog.length - 1}
            <div class="divider"></div>
          {/if}
        </div>
      {/each}
    </div>
  </div>
</div>