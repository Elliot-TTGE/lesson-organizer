<script lang="ts">
  import { Tipex } from "@friendofsvelte/tipex";
  import type { Editor } from "@tiptap/core";
  import "@friendofsvelte/tipex/styles/Tipex.css";
  import "@friendofsvelte/tipex/styles/EditLink.css";
  import "@friendofsvelte/tipex/styles/CodeBlock.css";
  import "$lib/styles/TipexControls.css";
  import "$lib/styles/TipexProse.css";

  let { body = $bindable(""), heading = "", height = "h-[30vh]" } = $props();

  function handleUpdate(event: any) {
    const editor = event.editor;
    if (editor) {
      const htmlContent = editor.getHTML();
      body = htmlContent;
    }
  }
</script>

<Tipex
  body={body}
  controls={true}
  floating={false}
  class={height}
  onupdate={handleUpdate}
  autofocus={false}
>
  {#snippet head()}
    <div class="text-lg font-bold text-secondary mb-2 px-2">
      {heading}
    </div>
  {/snippet}
  {#snippet utilities()}
    <!-- Removes utilities prop -->
  {/snippet}
</Tipex>