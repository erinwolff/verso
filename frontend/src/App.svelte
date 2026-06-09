<script lang="ts">
  import Spread from "./lib/Spread.svelte";

  // The room shows today's date on the verso as part of the empty frame.
  // The editor (P3) and book (P5) fill these pages in later phases.
  const today = new Date().toLocaleDateString(undefined, {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });
</script>

<Spread>
  {#snippet verso()}
    <header class="entry-head">
      <p class="wordmark">Verso</p>
      <h1 class="date">{today}</h1>
    </header>
    <p class="placeholder">The page is blank. Writing arrives in a later phase.</p>
  {/snippet}

  {#snippet recto()}
    <p class="placeholder">A book will rest here, thickening as you write.</p>
  {/snippet}
</Spread>

<style>
  .entry-head {
    margin-bottom: 1.5rem;
  }
  .wordmark {
    margin: 0;
    font-family: var(--sans);
    text-transform: uppercase;
    letter-spacing: 0.32em;
    font-size: 0.62rem;
    color: var(--muted);
  }
  .date {
    margin: 0.35rem 0 0;
    font-size: clamp(1.4rem, 3vmin, 2rem);
    font-weight: 500;
    color: var(--ink-bright);
  }
  .placeholder {
    margin: auto 0;
    color: var(--muted);
    font-style: italic;
    opacity: 0.7;
  }
</style>
