<script lang="ts">
  import { Tipex } from "@friendofsvelte/tipex";
  import "@friendofsvelte/tipex/styles/index.css";
  import "$lib/styles/TipexControls.css";
  import "$lib/styles/TipexProse.css";

  let { 
    body = $bindable(""), 
    heading = "", 
    height = "h-[30vh]",
    onSave = undefined
  } = $props<{ 
    body: string | undefined;
    heading: string;
    height?: string;
    onSave?: (content: string) => Promise<void>;
  }>();

  let saveTimeout: ReturnType<typeof setTimeout> | null = null;
  let isSaving = $state(false);
  let lastSavedContent = $state(body || "");

  // Ensure body is never undefined
  $effect(() => {
    if (body === undefined) {
      body = "";
    }
  });

  function handleUpdate(event: any) {
    const editor = event.editor;
    if (editor) {
      const htmlContent = editor.getHTML();
      body = htmlContent;
      
      // Debounce the save operation
      if (onSave && htmlContent !== lastSavedContent) {
        if (saveTimeout) {
          clearTimeout(saveTimeout);
        }
        
        saveTimeout = setTimeout(async () => {
          isSaving = true;
          try {
            await onSave(htmlContent);
            lastSavedContent = htmlContent;
          } catch (error) {
            console.error('Failed to save content:', error);
          } finally {
            isSaving = false;
          }
        }, 1000); // 1 second delay
      }
    }
  }
</script>

<Tipex
  body={body || ""}
  floating={false}
  class={height}
  onupdate={handleUpdate}
  autofocus={false}
>
  {#snippet head()}
    <div class="flex justify-between items-center mb-2 px-2">
      <div class="text-lg font-bold text-secondary">
        {heading}
      </div>
      {#if isSaving}
        <div class="flex items-center gap-2 text-sm text-base-content/60">
          <span class="loading loading-spinner loading-xs"></span>
          Saving...
        </div>
      {/if}
    </div>
  {/snippet}
  {#snippet utilities()}
    <!-- Removes utilities prop -->
  {/snippet}
</Tipex>