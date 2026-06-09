<script lang="ts">
  import Spread from "./lib/Spread.svelte";
  import Editor from "./lib/Editor.svelte";
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
    <!-- Provisional stats readout; the book (P5) and ember (P6) replace this. -->
    <div class="stats">
      {#if stats.index}
        <p class="big">{stats.index.entries}</p>
        <p class="label">
          {stats.index.entries === 1 ? "entry" : "entries"} ·
          {stats.index.words} words
        </p>
        <p class="streak">
          {stats.index.streak.count} days kept alight
          <span class="state">({stats.index.streak.state})</span>
        </p>
      {:else}
        <p class="placeholder">…</p>
      {/if}
    </div>
  {/snippet}
</Spread>

<style>
  .stats {
    margin: auto;
    text-align: center;
    color: var(--muted);
  }
  .big {
    margin: 0;
    font-size: 3rem;
    color: var(--ink-bright);
    line-height: 1;
  }
  .label {
    margin: 0.4rem 0 0;
    font-family: var(--sans);
    font-size: 0.8rem;
    letter-spacing: 0.05em;
  }
  .streak {
    margin-top: 1.5rem;
    color: var(--fire-soft);
    font-style: italic;
  }
  .state {
    color: var(--muted);
    font-style: normal;
    font-size: 0.8em;
  }
  .placeholder {
    margin: auto;
    opacity: 0.5;
  }
</style>
