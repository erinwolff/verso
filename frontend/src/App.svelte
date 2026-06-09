<script lang="ts">
  import Spread from "./lib/Spread.svelte";
  import Editor from "./lib/Editor.svelte";
  import Book from "./lib/Book.svelte";
  import Hearth from "./lib/Hearth.svelte";
  import Ember from "./lib/Ember.svelte";
  import Nav from "./lib/Nav.svelte";
  import Settings from "./lib/Settings.svelte";
  import { stats, refreshStats, applySave } from "./lib/stats.svelte";
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

<Settings />

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
</style>
