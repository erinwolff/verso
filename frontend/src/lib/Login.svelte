<script lang="ts">
  // Single-password gate (§7). Quiet, in-keeping with the room.
  import { login } from "./api";

  let { onsuccess }: { onsuccess: () => void } = $props();

  let password = $state("");
  let error = $state(false);
  let busy = $state(false);

  async function submit(e: Event) {
    e.preventDefault();
    if (busy || !password) return;
    busy = true;
    error = false;
    try {
      if (await login(password)) {
        onsuccess();
      } else {
        error = true;
        password = "";
      }
    } catch {
      error = true;
    } finally {
      busy = false;
    }
  }
</script>

<main class="gate">
  <form onsubmit={submit}>
    <p class="wordmark">Verso</p>
    <h1>The book is closed.</h1>
    <input
      type="password"
      bind:value={password}
      placeholder="password"
      aria-label="Password"
      autocomplete="current-password"
      class:error
    />
    {#if error}
      <p class="msg">That isn't the key. Try again.</p>
    {/if}
    <button type="submit" disabled={busy || !password}>
      {busy ? "opening…" : "open"}
    </button>
  </form>
</main>

<style>
  .gate {
    min-height: 100vh;
    display: grid;
    place-items: center;
    padding: 1.5rem;
  }
  form {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.85rem;
    width: min(100%, 20rem);
    text-align: center;
  }
  .wordmark {
    margin: 0;
    font-family: var(--sans);
    text-transform: uppercase;
    letter-spacing: 0.32em;
    font-size: 0.62rem;
    color: var(--muted);
  }
  h1 {
    margin: 0 0 0.5rem;
    font-weight: 500;
    font-size: 1.5rem;
    color: var(--ink-bright);
  }
  input {
    width: 100%;
    padding: 0.6rem 0.8rem;
    background: color-mix(in srgb, var(--bg) 88%, #000);
    border: 1px solid var(--surface-edge);
    border-radius: 7px;
    color: var(--ink);
    font-family: var(--serif);
    font-size: 1.05rem;
    caret-color: var(--fire);
    text-align: center;
  }
  input:focus {
    outline: none;
    border-color: color-mix(in srgb, var(--fire) 45%, var(--surface-edge));
  }
  input.error {
    border-color: #c96a4a;
  }
  .msg {
    margin: 0;
    font-size: 0.8rem;
    color: #c96a4a;
    font-family: var(--sans);
  }
  button {
    padding: 0.5rem 1.4rem;
    background: none;
    border: 1px solid var(--fire);
    border-radius: 999px;
    color: var(--fire);
    font-family: var(--sans);
    letter-spacing: 0.06em;
    text-transform: uppercase;
    font-size: 0.78rem;
    cursor: pointer;
    transition: background 0.2s ease;
  }
  button:hover:not(:disabled) {
    background: color-mix(in srgb, var(--fire) 14%, transparent);
  }
  button:disabled {
    opacity: 0.5;
    cursor: default;
  }
</style>
