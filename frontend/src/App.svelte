<script lang="ts">
  import Spread from "./lib/Spread.svelte";
  import Editor from "./lib/Editor.svelte";
  import Book from "./lib/Book.svelte";
  import Hearth from "./lib/Hearth.svelte";
  import Ember from "./lib/Ember.svelte";
  import Nav from "./lib/Nav.svelte";
  import Settings from "./lib/Settings.svelte";
  import Login from "./lib/Login.svelte";
  import { stats, refreshStats, applySave } from "./lib/stats.svelte";
  import { getAuth, setUnauthorizedHandler } from "./lib/api";
  import { todayStr } from "./lib/dates";

  // The day being written. Defaults to today (local); Nav can change it.
  let activeDate = $state(todayStr());

  type Phase = "checking" | "login" | "ready";
  let phase = $state<Phase>("checking");
  let authRequired = $state(false);

  function enterRoom() {
    phase = "ready";
    refreshStats();
  }

  // A protected request returning 401 mid-session drops back to login.
  setUnauthorizedHandler(() => {
    phase = "login";
  });

  $effect(() => {
    getAuth()
      .then((a) => {
        authRequired = a.required;
        if (a.required && !a.authenticated) {
          phase = "login";
        } else {
          enterRoom();
        }
      })
      .catch(() => enterRoom()); // if auth check fails, fail open to the room
  });
</script>

{#if phase === "login"}
  <Login onsuccess={enterRoom} />
{:else if phase === "ready"}

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
          <Book
            count={stats.index.entries}
            dates={stats.entries.map((e) => e.date)}
            {activeDate}
            onnavigate={(d) => (activeDate = d)}
          />
          <Ember streak={stats.index.streak} />
        {/if}
      </div>
    {/snippet}
  </Spread>
</div>

  <Settings {authRequired} />
{/if}

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
