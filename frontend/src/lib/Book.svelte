<script lang="ts">
  // The filling book (§6). Renders an oblique-projection closed leather book
  // whose page-block thickens with the entry count, a faint full-size ghost
  // outline behind it, and the caption. The displayed thickness is driven by
  // `count`; P7 animates this by tweening the value passed in.
  import {
    BOOK,
    geometryFor,
    thicknessUnits,
    thicknessLabel,
  } from "./book";

  let { count = 0 }: { count?: number } = $props();

  const geom = $derived(geometryFor(thicknessUnits(count)));
  const ghost = $derived(geometryFor(BOOK.max));
  const label = $derived(thicknessLabel(count));

  // Diamond crest centred on the cover.
  const cx = BOOK.coverX + BOOK.W / 2;
  const cy = BOOK.coverY + BOOK.H / 2;
</script>

<figure class="book">
  <svg
    viewBox="0 0 420 380"
    role="img"
    aria-label={count === 0
      ? "An empty book"
      : `A book of ${count} entries`}
  >
    <!-- soft contact shadow -->
    <ellipse cx="210" cy="346" rx="150" ry="16" fill="rgba(0,0,0,0.35)" />

    <!-- ghost: full-size silhouette of what the book will become -->
    <g class="ghost" aria-hidden="true">
      <polygon points={ghost.topFace} />
      <polygon points={ghost.rightFace} />
      <rect
        x={ghost.cover.x}
        y={ghost.cover.y}
        width={ghost.cover.w}
        height={ghost.cover.h}
        rx="4"
      />
    </g>

    <!-- page block: top + fore-edge faces, then the leaf lines -->
    <g class="pages">
      <polygon class="page-fill" points={geom.topFace} />
      <polygon class="page-fill" points={geom.rightFace} />
      {#each geom.leaves as leaf}
        <line
          x1={leaf.x1}
          y1={leaf.y1}
          x2={leaf.x2}
          y2={leaf.y2}
          class={leaf.shade ? "leaf leaf--shade" : "leaf"}
        />
      {/each}
    </g>

    <!-- front cover: leather + gilt inset border + diamond crest -->
    <g class="cover">
      <rect
        x={geom.cover.x}
        y={geom.cover.y}
        width={geom.cover.w}
        height={geom.cover.h}
        rx="4"
        class="leather"
      />
      <rect
        x={geom.cover.x + 12}
        y={geom.cover.y + 12}
        width={geom.cover.w - 24}
        height={geom.cover.h - 24}
        rx="3"
        class="gilt-border"
      />
      <polygon
        class="gilt-line"
        points={`${cx},${cy - 28} ${cx + 28},${cy} ${cx},${cy + 28} ${cx - 28},${cy}`}
      />
      <polygon
        class="gilt-line"
        points={`${cx},${cy - 12} ${cx + 12},${cy} ${cx},${cy + 12} ${cx - 12},${cy}`}
      />
    </g>
  </svg>

  <figcaption>
    {#if count === 0}
      <span class="empty">Your book is empty. Write the first page.</span>
    {:else}
      <span class="count">{count}</span>
      {count === 1 ? "entry" : "entries"} bound · {label} thick
    {/if}
  </figcaption>
</figure>

<style>
  .book {
    margin: auto;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.25rem;
    width: 100%;
  }
  svg {
    width: min(100%, 420px);
    height: auto;
    display: block;
    overflow: visible;
  }

  .ghost polygon,
  .ghost rect {
    fill: none;
    stroke: var(--page);
    stroke-width: 1;
    opacity: 0.1;
  }

  .page-fill {
    fill: var(--page);
  }
  .leaf {
    stroke: var(--page);
    stroke-width: 1;
  }
  .leaf--shade {
    stroke: var(--page-shade);
  }

  .leather {
    fill: var(--leather);
  }
  .gilt-border,
  .gilt-line {
    fill: none;
    stroke: var(--gilt);
    stroke-width: 1.5;
  }

  figcaption {
    font-family: var(--serif);
    color: var(--muted);
    font-size: 0.95rem;
    text-align: center;
    letter-spacing: 0.01em;
  }
  .count {
    color: var(--ink-bright);
    font-size: 1.15rem;
  }
  .empty {
    font-style: italic;
    opacity: 0.85;
  }
</style>
