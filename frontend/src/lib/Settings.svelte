<script lang="ts">
  // Settings + export panel (§4). Opened from a corner gear. Exports are plain
  // download links to the API (Content-Disposition triggers the save).
  import { settings, setFlicker } from "./settings.svelte";

  let open = $state(false);
  let mdOrder = $state<"newest" | "oldest">("newest");
</script>

<button
  class="gear"
  type="button"
  aria-expanded={open}
  title="Settings & export"
  onclick={() => (open = !open)}
>
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <path
      fill="currentColor"
      d="M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8zm9 4c0-.6-.05-1.18-.14-1.74l2.02-1.58-2-3.46-2.4.97a7.9 7.9 0 0 0-3.01-1.74L15.1 1h-4l-.37 2.45a7.9 7.9 0 0 0-3.01 1.74l-2.4-.97-2 3.46 2.02 1.58a8 8 0 0 0 0 3.48L1.32 14.3l2 3.46 2.4-.97a7.9 7.9 0 0 0 3.01 1.74L11.1 21h4l.37-2.45a7.9 7.9 0 0 0 3.01-1.74l2.4.97 2-3.46-2.02-1.58c.09-.56.14-1.14.14-1.74z"
      opacity="0.92"
    />
  </svg>
  <span class="sr-only">Open settings</span>
</button>

{#if open}
  <button
    class="scrim"
    type="button"
    aria-label="Close settings"
    onclick={() => (open = false)}
  ></button>
  <div class="panel" role="dialog" aria-label="Settings and export">
    <h2>Firelight</h2>
    <label class="switch">
      <input
        type="checkbox"
        checked={settings.flicker}
        onchange={(e) => setFlicker(e.currentTarget.checked)}
      />
      <span>Flicker the hearth</span>
    </label>
    <p class="hint">Off by default — gentler on the eyes and phone battery.</p>

    <h2>Export</h2>
    <p class="hint">
      Your journal is plain markdown. Take it with you any time.
    </p>
    <div class="exports">
      <a class="exp" href="/api/export/zip">
        <span class="exp-title">Markdown (.zip)</span>
        <span class="exp-sub">the entries folder, as-is — lossless</span>
      </a>
      <a class="exp" href={`/api/export/markdown?order=${mdOrder}`}>
        <span class="exp-title">Combined (.md)</span>
        <span class="exp-sub">all entries in one file</span>
      </a>
      <a class="exp" href="/api/export/json">
        <span class="exp-title">JSON (.json)</span>
        <span class="exp-sub">for piping elsewhere</span>
      </a>
    </div>
    <label class="order">
      Combined order:
      <select bind:value={mdOrder}>
        <option value="newest">newest first</option>
        <option value="oldest">oldest first</option>
      </select>
    </label>
  </div>
{/if}

<style>
  .gear {
    position: fixed;
    right: 1rem;
    bottom: 1rem;
    z-index: 6;
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
  .gear:hover {
    color: var(--fire-soft);
    border-color: color-mix(in srgb, var(--fire) 40%, var(--surface-edge));
  }
  .gear svg {
    width: 1.15rem;
    height: 1.15rem;
  }

  .scrim {
    position: fixed;
    inset: 0;
    z-index: 6;
    border: 0;
    background: rgba(0, 0, 0, 0.4);
    cursor: default;
  }
  .panel {
    position: fixed;
    right: 1rem;
    bottom: 3.6rem;
    z-index: 7;
    width: min(92vw, 22rem);
    max-height: 80vh;
    overflow-y: auto;
    padding: 1.25rem 1.35rem 1.5rem;
    border: 1px solid var(--surface-edge);
    border-radius: 10px;
    background: color-mix(in srgb, var(--bg) 96%, #000);
    box-shadow: 0 24px 60px -28px rgba(0, 0, 0, 0.9);
    color: var(--ink);
    font-family: var(--sans);
  }
  h2 {
    font-family: var(--serif);
    font-size: 1.05rem;
    font-weight: 500;
    color: var(--ink-bright);
    margin: 0.25rem 0 0.6rem;
  }
  h2:not(:first-child) {
    margin-top: 1.4rem;
  }
  .hint {
    margin: 0.3rem 0 0.6rem;
    font-size: 0.78rem;
    color: var(--muted);
    line-height: 1.5;
  }
  .switch {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.88rem;
    cursor: pointer;
  }
  .switch input {
    accent-color: var(--fire);
    width: 1rem;
    height: 1rem;
  }

  .exports {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  .exp {
    display: flex;
    flex-direction: column;
    gap: 0.1rem;
    padding: 0.6rem 0.75rem;
    border: 1px solid var(--surface-edge);
    border-radius: 7px;
    text-decoration: none;
    color: var(--ink);
    transition: border-color 0.2s ease, background 0.2s ease;
  }
  .exp:hover {
    border-color: color-mix(in srgb, var(--fire) 45%, var(--surface-edge));
    background: color-mix(in srgb, var(--fire) 8%, transparent);
  }
  .exp-title {
    font-size: 0.9rem;
    color: var(--ink-bright);
  }
  .exp-sub {
    font-size: 0.74rem;
    color: var(--muted);
  }
  .order {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 0.8rem;
    font-size: 0.78rem;
    color: var(--muted);
  }
  .order select {
    background: var(--bg);
    color: var(--ink);
    border: 1px solid var(--surface-edge);
    border-radius: 5px;
    padding: 0.2rem 0.4rem;
    font-family: var(--sans);
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
