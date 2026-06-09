<script lang="ts">
  // Date navigation for the verso: wordmark, the active date with prev/next
  // day stepping and a "today" jump, plus a quiet browsable list of past
  // entries (past entries are editable, §P8).
  import type { EntryMeta } from "./api";
  import { addDays, formatLong, formatShort, todayStr } from "./dates";

  let {
    activeDate,
    entries,
    onnavigate,
  }: {
    activeDate: string;
    entries: EntryMeta[];
    onnavigate: (date: string) => void;
  } = $props();

  let browsing = $state(false);

  const today = todayStr();
  const heading = $derived(formatLong(activeDate));
  const isToday = $derived(activeDate === today);
  // Don't wander into the future; today is the latest writable day.
  const canGoNext = $derived(activeDate < today);

  function go(delta: number) {
    const next = addDays(activeDate, delta);
    if (delta > 0 && next > today) return;
    onnavigate(next);
  }

  function pick(date: string) {
    onnavigate(date);
    browsing = false;
  }
</script>

<nav class="nav">
  <div class="row">
    <p class="wordmark">Verso</p>
    <button
      class="browse"
      type="button"
      aria-expanded={browsing}
      onclick={() => (browsing = !browsing)}
    >
      {browsing ? "close" : "past entries"}
    </button>
  </div>

  <div class="datebar">
    <button class="step" type="button" onclick={() => go(-1)} title="Previous day"
      >‹</button
    >
    <h1 class="date">{heading}</h1>
    <button
      class="step"
      type="button"
      onclick={() => go(1)}
      disabled={!canGoNext}
      title="Next day">›</button
    >
  </div>
  {#if !isToday}
    <button class="today" type="button" onclick={() => onnavigate(today)}>
      ↩ back to today
    </button>
  {/if}
</nav>

{#if browsing}
  <div class="list" role="listbox" aria-label="Past entries">
    {#if entries.length === 0}
      <p class="empty">No entries yet. The first page is today's.</p>
    {:else}
      {#each entries as e (e.date)}
        <button
          class="item"
          class:active={e.date === activeDate}
          role="option"
          aria-selected={e.date === activeDate}
          onclick={() => pick(e.date)}
        >
          <span class="item-date">{formatShort(e.date)}</span>
          <span class="item-preview">{e.preview || "—"}</span>
          <span class="item-words">{e.words}w</span>
        </button>
      {/each}
    {/if}
  </div>
{/if}

<style>
  .nav {
    margin-bottom: 1.25rem;
  }
  .row {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .wordmark {
    margin: 0;
    font-family: var(--sans);
    text-transform: uppercase;
    letter-spacing: 0.32em;
    font-size: 0.62rem;
    color: var(--muted);
  }
  .browse {
    background: none;
    border: 0;
    color: var(--muted);
    font-family: var(--sans);
    font-size: 0.7rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    cursor: pointer;
    padding: 0.2rem 0;
  }
  .browse:hover {
    color: var(--fire-soft);
  }

  .datebar {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 0.4rem;
  }
  .date {
    margin: 0;
    font-size: clamp(1.3rem, 2.6vmin, 1.9rem);
    font-weight: 500;
    color: var(--ink-bright);
    flex: 1;
  }
  .step {
    background: none;
    border: 0;
    color: var(--muted);
    font-size: 1.5rem;
    line-height: 1;
    cursor: pointer;
    padding: 0 0.3rem;
    transition: color 0.2s ease;
  }
  .step:hover:not(:disabled) {
    color: var(--fire-soft);
  }
  .step:disabled {
    opacity: 0.25;
    cursor: default;
  }
  .today {
    margin-top: 0.4rem;
    background: none;
    border: 0;
    color: var(--fire-soft);
    font-family: var(--sans);
    font-size: 0.72rem;
    letter-spacing: 0.04em;
    cursor: pointer;
    padding: 0;
  }
  .today:hover {
    color: var(--fire);
  }

  .list {
    position: absolute;
    inset: clamp(1.5rem, 4vmin, 3.25rem) auto auto
      clamp(1.5rem, 4vmin, 3.25rem);
    width: min(80%, 22rem);
    max-height: 70%;
    overflow-y: auto;
    z-index: 5;
    background: color-mix(in srgb, var(--bg) 94%, #000);
    border: 1px solid var(--surface-edge);
    border-radius: 8px;
    box-shadow: 0 20px 50px -24px rgba(0, 0, 0, 0.9);
    padding: 0.4rem;
  }
  .item {
    display: grid;
    grid-template-columns: 1fr auto;
    grid-template-areas: "date words" "preview preview";
    gap: 0.15rem 0.5rem;
    width: 100%;
    text-align: left;
    background: none;
    border: 0;
    border-radius: 5px;
    padding: 0.55rem 0.6rem;
    cursor: pointer;
    color: var(--ink);
  }
  .item:hover {
    background: var(--surface-edge);
  }
  .item.active {
    background: color-mix(in srgb, var(--fire) 14%, transparent);
  }
  .item-date {
    grid-area: date;
    font-family: var(--sans);
    font-size: 0.75rem;
    color: var(--ink-bright);
    letter-spacing: 0.03em;
  }
  .item-words {
    grid-area: words;
    font-family: var(--sans);
    font-size: 0.7rem;
    color: var(--muted);
  }
  .item-preview {
    grid-area: preview;
    font-size: 0.82rem;
    color: var(--muted);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .empty {
    margin: 0;
    padding: 0.8rem;
    color: var(--muted);
    font-style: italic;
    font-size: 0.85rem;
  }
</style>
