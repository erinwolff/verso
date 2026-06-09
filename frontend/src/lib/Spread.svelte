<script lang="ts">
  // The desktop two-page spread frame (verso-plan.md §1). Empty in P1 — the
  // editor (P3) fills the verso; the book (P5) fills the recto. This component
  // owns only the open-journal shell: two page surfaces and the binding gutter.
  import type { Snippet } from "svelte";

  let { verso, recto }: { verso?: Snippet; recto?: Snippet } = $props();
</script>

<div class="spread-wrap">
  <article class="spread">
    <section class="page page--verso">
      {#if verso}{@render verso()}{:else}
        <p class="placeholder">verso — today's page</p>
      {/if}
    </section>
    <div class="gutter" aria-hidden="true"></div>
    <section class="page page--recto">
      {#if recto}{@render recto()}{:else}
        <p class="placeholder">recto — the book</p>
      {/if}
    </section>
  </article>
</div>

<style>
  .spread-wrap {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: clamp(1rem, 4vmin, 3rem);
  }

  /* The open journal: two surfaces meeting at a sunken binding. Lifted a hair
     off the room with a warm border and a soft drop, like a book on a desk. */
  .spread {
    position: relative;
    display: grid;
    grid-template-columns: 1fr 1px 1fr;
    width: min(1120px, 100%);
    aspect-ratio: 16 / 10;
    max-height: calc(100vh - 4rem);
    border: 1px solid var(--surface-edge);
    border-radius: 10px;
    background:
      linear-gradient(180deg,
        color-mix(in srgb, var(--bg) 92%, var(--ink) 8%) 0%,
        var(--bg) 100%);
    box-shadow:
      0 1px 0 color-mix(in srgb, var(--ink) 10%, transparent) inset,
      0 24px 60px -30px rgba(0, 0, 0, 0.8);
  }

  .page {
    position: relative;
    padding: clamp(1.5rem, 4vmin, 3.25rem);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  /* The binding: a soft trough of shadow + a single gilt-faint hairline. */
  .gutter {
    background: var(--surface-edge);
    position: relative;
  }
  .spread::before {
    content: "";
    position: absolute;
    inset: 0 calc(50% - 28px);
    pointer-events: none;
    background: radial-gradient(
      60% 90% at 50% 50%,
      rgba(0, 0, 0, 0.28),
      transparent 70%
    );
  }

  .placeholder {
    margin: auto;
    color: var(--muted);
    font-style: italic;
    letter-spacing: 0.03em;
    opacity: 0.7;
  }

  /* Mobile: single column, none of the spread machinery (§1). Editor on top,
     small book + streak below; the dark room shows through directly. */
  @media (max-width: 760px) {
    .spread-wrap {
      padding: 0;
      align-items: stretch;
      min-height: 100dvh;
    }
    .spread {
      display: block;
      width: 100%;
      aspect-ratio: auto;
      max-height: none;
      border: none;
      border-radius: 0;
      background: none;
      box-shadow: none;
    }
    .gutter,
    .spread::before { display: none; }
    .page {
      padding: 1.25rem 1.15rem;
      overflow: visible;
    }
    .page--recto {
      border-top: 1px solid var(--surface-edge);
      margin-top: 0.25rem;
      padding-top: 1.75rem;
    }
  }
</style>
