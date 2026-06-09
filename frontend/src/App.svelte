<script lang="ts">
  import Spread from "./lib/Spread.svelte";
  import Editor from "./lib/Editor.svelte";
  import Book from "./lib/Book.svelte";
  import Hearth from "./lib/Hearth.svelte";
  import Ember from "./lib/Ember.svelte";
  import { stats, refreshStats, applySave } from "./lib/stats.svelte";
  import { settings, setFlicker } from "./lib/settings.svelte";

  // The day being written. Defaults to today (local). P8 lets this change.
  const today = new Date();
  const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;
  let activeDate = $state(todayStr);

  $effect(() => {
    refreshStats();
  });
</script>

<Hearth />

<div class="room">
  <Spread>
    {#snippet verso()}
      <Editor date={activeDate} onsaved={applySave} />
    {/snippet}

    {#snippet recto()}
      <div class="recto">
        <Book count={stats.index?.entries ?? 0} />
        {#if stats.index}
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
