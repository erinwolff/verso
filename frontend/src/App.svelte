<script lang="ts">
  import Spread from "./lib/Spread.svelte";
  import Editor from "./lib/Editor.svelte";

  // The day being written. Defaults to today (local). P8 lets this change.
  const today = new Date();
  const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;
  let activeDate = $state(todayStr);
</script>

<Spread>
  {#snippet verso()}
    <Editor date={activeDate} />
  {/snippet}

  {#snippet recto()}
    <p class="placeholder">A book will rest here, thickening as you write.</p>
  {/snippet}
</Spread>

<style>
  .placeholder {
    margin: auto;
    color: var(--muted);
    font-style: italic;
    opacity: 0.7;
    text-align: center;
  }
</style>
