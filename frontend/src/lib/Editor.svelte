<script lang="ts">
  import { getEntry, saveEntry, type SaveResult } from "./api";

  let {
    date,
    onsaved,
  }: {
    date: string;
    onsaved?: (result: SaveResult) => void;
  } = $props();

  let body = $state("");
  let status = $state<"idle" | "loading" | "saving" | "saved" | "error">(
    "loading",
  );
  let saveTimer: ReturnType<typeof setTimeout> | undefined;
  let savedTimer: ReturnType<typeof setTimeout> | undefined;
  // Guards autosave from firing on the programmatic load below.
  let currentDate = $state("");

  const words = $derived(body.trim() ? body.trim().split(/\s+/).length : 0);

  const heading = $derived(
    new Date(date + "T00:00:00").toLocaleDateString(undefined, {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    }),
  );

  // Load whenever the date changes; flush any pending save for the old date.
  $effect(() => {
    const d = date;
    if (saveTimer) {
      clearTimeout(saveTimer);
      saveTimer = undefined;
    }
    status = "loading";
    getEntry(d)
      .then((e) => {
        if (date !== d) return; // a newer date won the race
        body = e.body;
        currentDate = d;
        status = "idle";
      })
      .catch(() => (status = "error"));
  });

  async function flush() {
    if (saveTimer) {
      clearTimeout(saveTimer);
      saveTimer = undefined;
    }
    const d = currentDate;
    if (!d) return;
    status = "saving";
    try {
      const result = await saveEntry(d, body);
      status = "saved";
      onsaved?.(result);
      if (savedTimer) clearTimeout(savedTimer);
      savedTimer = setTimeout(() => {
        if (status === "saved") status = "idle";
      }, 1600);
    } catch {
      status = "error";
    }
  }

  function onInput() {
    if (status === "loading") return;
    if (saveTimer) clearTimeout(saveTimer);
    saveTimer = setTimeout(flush, 800);
  }

  // Flush a pending edit if the tab is hidden / app closed mid-thought.
  $effect(() => {
    const handler = () => {
      if (saveTimer) flush();
    };
    window.addEventListener("beforeunload", handler);
    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "hidden" && saveTimer) flush();
    });
    return () => window.removeEventListener("beforeunload", handler);
  });
</script>

<div class="editor">
  <header class="head">
    <p class="wordmark">Verso</p>
    <h1 class="date">{heading}</h1>
  </header>

  <textarea
    class="ink"
    bind:value={body}
    oninput={onInput}
    spellcheck="true"
    placeholder="Write the day…"
    aria-label="Journal entry for {heading}"
  ></textarea>

  <footer class="foot">
    <span class="words">{words} {words === 1 ? "word" : "words"}</span>
    <span class="status status--{status}">
      {#if status === "saving"}saving…
      {:else if status === "saved"}saved
      {:else if status === "error"}couldn't save
      {:else if status === "loading"}…
      {:else}&nbsp;{/if}
    </span>
  </footer>
</div>

<style>
  .editor {
    display: flex;
    flex-direction: column;
    height: 100%;
    min-height: 0;
  }
  .head {
    margin-bottom: 1.25rem;
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
    font-size: clamp(1.3rem, 2.6vmin, 1.9rem);
    font-weight: 500;
    color: var(--ink-bright);
  }

  .ink {
    flex: 1;
    min-height: 0;
    width: 100%;
    resize: none;
    border: 0;
    outline: none;
    background: transparent;
    color: var(--ink);
    caret-color: var(--fire);
    font-family: var(--serif);
    font-size: 1.18rem;
    line-height: 1.75;
    padding: 0;
  }
  .ink::placeholder {
    color: var(--muted);
    font-style: italic;
    opacity: 0.6;
  }

  .foot {
    margin-top: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    font-family: var(--sans);
    font-size: 0.72rem;
    letter-spacing: 0.04em;
    color: var(--muted);
  }
  .status {
    transition: opacity 0.4s ease, color 0.4s ease;
  }
  .status--saving { color: var(--fire-soft); }
  .status--saved { color: var(--fire); }
  .status--error { color: #c96a4a; }
</style>
