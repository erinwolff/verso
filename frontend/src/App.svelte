<script lang="ts">
  import Spread from "./lib/Spread.svelte";
  import Editor from "./lib/Editor.svelte";
  import Book from "./lib/Book.svelte";
  import Hearth from "./lib/Hearth.svelte";
  import Ember from "./lib/Ember.svelte";
  import Nav from "./lib/Nav.svelte";
  import { stats, refreshStats, applySave } from "./lib/stats.svelte";
  import { settings, setFlicker } from "./lib/settings.svelte";
  import { todayStr } from "./lib/dates";

  // The day being written. Defaults to today (local); Nav can change it.
  let activeDate = $state(todayStr());

  $effect(() => {
    refreshStats();
  });
</script>

<Hearth />

<div class="room">
  <Spread>
    {#snippet verso()}
      <div class="verso-col">
        <Nav
          {activeDate}
          entries={stats.entries}
          onnavigate={(d) => (activeDate = d)}
        />
        <Editor date={activeDate} onsaved={applySave} />
      </div>
    {/snippet}

    {#snippet recto()}
      <div class="recto">
        {#if stats.loaded && stats.index}
          <Book count={stats.index.entries} />
          <Ember streak={stats.index.streak} />
        {/if}
      </div>
    {/snippet}
  </Spread>
</div>

<button
  class="flicker-toggle"
  type="button"
  aria-pressed={settings.flicker}
  title={settings.flicker ? "Firelight flicker: on" : "Firelight flicker: off"}
  onclick={() => setFlicker(!settings.flicker)}
>
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <path
      d="M12 2C9 6 7 8 7 13a5 5 0 0 0 10 0c0-2-1-4-2-5 0 1.5-1 2.5-2 2.5 0-3 1-6-1-8.5z"
      fill="currentColor"
    />
  </svg>
  <span class="sr-only">Toggle firelight flicker</span>
</button>

<style>
  .room {
    position: relative;
    z-index: 1;
  }
  .verso-col {
    display: flex;
    flex-direction: column;
    height: 100%;
    min-height: 0;
  }
  .recto {
    margin: auto 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.75rem;
    width: 100%;
  }

  .flicker-toggle {
    position: fixed;
    right: 1rem;
    bottom: 1rem;
    z-index: 2;
    display: grid;
    place-items: center;
    width: 2.1rem;
    height: 2.1rem;
    padding: 0;
    border-radius: 999px;
    border: 1px solid var(--surface-edge);
    background: color-mix(in srgb, var(--bg) 70%, transparent);
    color: var(--muted);
    cursor: pointer;
    transition: color 0.3s ease, border-color 0.3s ease;
  }
  .flicker-toggle:hover {
    color: var(--fire-soft);
    border-color: color-mix(in srgb, var(--fire) 40%, var(--surface-edge));
  }
  .flicker-toggle[aria-pressed="true"] {
    color: var(--fire);
  }
  .flicker-toggle svg {
    width: 1.05rem;
    height: 1.05rem;
  }
  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip: rect(0 0 0 0);
    white-space: nowrap;
  }
</style>
