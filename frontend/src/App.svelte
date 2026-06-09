<script lang="ts">
  import Spread from "./lib/Spread.svelte";
  import Editor from "./lib/Editor.svelte";
  import Book from "./lib/Book.svelte";
  import { stats, refreshStats, applySave } from "./lib/stats.svelte";

  // The day being written. Defaults to today (local). P8 lets this change.
  const today = new Date();
  const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;
  let activeDate = $state(todayStr);

  $effect(() => {
    refreshStats();
  });
</script>

<Spread>
  {#snippet verso()}
    <Editor date={activeDate} onsaved={applySave} />
  {/snippet}

  {#snippet recto()}
    <!-- The ember pill (P6) will join the book here. -->
    <Book count={stats.index?.entries ?? 0} />
  {/snippet}
</Spread>
