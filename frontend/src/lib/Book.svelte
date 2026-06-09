<script lang="ts">
  // The filling book (§6). Renders an oblique-projection closed leather book
  // whose page-block thickens with the entry count, a faint full-size ghost
  // outline behind it, and the caption. The displayed thickness is driven by
  // `count`; P7 animates this by tweening the value passed in.
  //
  // The fore-edge is also a scrubber: hovering it snaps to the nearest real
  // entry (front edge = most recent, deeper = older), shows the date, and
  // clicking opens that day. Desktop-only; touch falls back to the Nav list.
  import { Tween } from "svelte/motion";
  import { cubicOut } from "svelte/easing";
  import {
    BOOK,
    geometryFor,
    thicknessUnits,
    thicknessLabel,
  } from "./book";
  import { formatLong } from "./dates";

  let {
    count = 0,
    dates = [],
    activeDate = "",
    onnavigate,
  }: {
    count?: number;
    /** Entry dates, newest-first (front of the book = most recent). */
    dates?: string[];
    activeDate?: string;
    onnavigate?: (date: string) => void;
  } = $props();

  const reduceMotion =
    typeof window !== "undefined" &&
    window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;

  // The page-block thickness tweens so a new entry visibly widens the book by
  // a leaf (~500ms). Starts at the empty thickness; the first effect snaps to
  // the real count with duration 0, so only later saves animate.
  const thick = new Tween(thicknessUnits(0), {
    duration: reduceMotion ? 0 : 520,
    easing: cubicOut,
  });
  let primed = false;
  $effect(() => {
    const target = thicknessUnits(count);
    if (!primed) {
      thick.set(target, { duration: 0 });
      primed = true;
    } else {
      thick.set(target);
    }
  });

  const geom = $derived(geometryFor(thick.current));
  const ghost = $derived(geometryFor(BOOK.max));
  const label = $derived(thicknessLabel(count));

  // Diamond crest centred on the cover.
  const cx = BOOK.coverX + BOOK.W / 2;
  const cy = BOOK.coverY + BOOK.H / 2;

  // --- fore-edge scrubbing ---------------------------------------------
  const FTRx = BOOK.coverX + BOOK.W;
  const FTRy = BOOK.coverY;
  const FBRy = BOOK.coverY + BOOK.H;

  let svgEl: SVGSVGElement | undefined = $state();
  let figureEl: HTMLElement | undefined = $state();
  let hoverIdx = $state<number | null>(null);
  let tipX = $state(0);
  let tipY = $state(0);

  const interactive = $derived(!!onnavigate && dates.length >= 1);
  const activeIdx = $derived(activeDate ? dates.indexOf(activeDate) : -1);
  const hoverDate = $derived(
    hoverIdx !== null && dates[hoverIdx] ? dates[hoverIdx] : null,
  );

  // Depth offset (SVG units) for the leaf at fractional position t in [0,1].
  function leafLine(idx: number) {
    const t = dates.length > 1 ? idx / (dates.length - 1) : 0;
    const ox = t * thick.current * BOOK.ux;
    const oy = t * thick.current * BOOK.uy;
    return {
      x1: FTRx + ox,
      y1: FTRy + oy,
      x2: FTRx + ox,
      y2: FBRy + oy,
    };
  }

  // Project a cursor point onto the depth axis → fraction t in [0,1].
  function depthFraction(e: MouseEvent): number | null {
    if (!svgEl) return null;
    const pt = svgEl.createSVGPoint();
    pt.x = e.clientX;
    pt.y = e.clientY;
    const ctm = svgEl.getScreenCTM();
    if (!ctm) return null;
    const p = pt.matrixTransform(ctm.inverse());
    const dx = thick.current * BOOK.ux;
    const dy = thick.current * BOOK.uy;
    const dd = dx * dx + dy * dy;
    if (dd === 0) return 0;
    const t = ((p.x - FTRx) * dx + (p.y - FTRy) * dy) / dd;
    return Math.max(0, Math.min(1, t));
  }

  function onMove(e: MouseEvent) {
    if (!interactive) return;
    const t = depthFraction(e);
    if (t === null) return;
    hoverIdx = dates.length > 1 ? Math.round(t * (dates.length - 1)) : 0;
    if (figureEl) {
      const r = figureEl.getBoundingClientRect();
      tipX = e.clientX - r.left;
      tipY = e.clientY - r.top;
    }
  }

  function onLeave() {
    hoverIdx = null;
  }

  function onClick() {
    if (hoverDate) onnavigate?.(hoverDate);
  }
</script>

<figure class="book" bind:this={figureEl}>
  <svg
    bind:this={svgEl}
    viewBox="0 0 420 380"
    role="img"
    class:scrubbable={interactive}
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

    <!-- marker for the currently-open day; brighter highlight while scrubbing -->
    {#if activeIdx >= 0 && activeIdx !== hoverIdx}
      {@const m = leafLine(activeIdx)}
      <line class="leaf-active" x1={m.x1} y1={m.y1} x2={m.x2} y2={m.y2} />
    {/if}
    {#if hoverIdx !== null}
      {@const h = leafLine(hoverIdx)}
      <line class="leaf-hover" x1={h.x1} y1={h.y1} x2={h.x2} y2={h.y2} />
    {/if}

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

    <!-- transparent hit target over the page faces (desktop hover only) -->
    {#if interactive}
      <!-- svelte-ignore a11y_click_events_have_key_events -->
      <!-- svelte-ignore a11y_no_static_element_interactions -->
      <g
        class="hit"
        onmousemove={onMove}
        onmouseleave={onLeave}
        onclick={onClick}
      >
        <polygon points={geom.rightFace} />
        <polygon points={geom.topFace} />
      </g>
    {/if}
  </svg>

  {#if hoverDate}
    <div class="tip" style="left:{tipX}px; top:{tipY}px;">
      {formatLong(hoverDate)}
    </div>
  {/if}

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
    position: relative;
    margin: auto;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.25rem;
    width: 100%;
  }

  /* Touch devices have no hover, so disable the scrubber — the Nav 'past
     entries' list is the browse path there. */
  @media (hover: none) {
    .hit {
      pointer-events: none;
    }
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

  /* a faint mark for the open day, a bright one under the cursor */
  .leaf-active {
    stroke: var(--fire);
    stroke-width: 1.5;
    opacity: 0.45;
  }
  .leaf-hover {
    stroke: var(--fire);
    stroke-width: 2.5;
    filter: drop-shadow(0 0 3px rgba(var(--fire-glow), 0.9));
  }

  /* transparent hit area; 'transparent' fill is hit-testable, 'none' is not */
  .hit polygon {
    fill: transparent;
    stroke: none;
  }
  svg.scrubbable .hit {
    cursor: pointer;
  }

  .tip {
    position: absolute;
    transform: translate(-50%, -135%);
    pointer-events: none;
    white-space: nowrap;
    padding: 0.25rem 0.55rem;
    border-radius: 6px;
    background: color-mix(in srgb, var(--bg) 92%, #000);
    border: 1px solid var(--surface-edge);
    color: var(--fire-soft);
    font-family: var(--sans);
    font-size: 0.72rem;
    letter-spacing: 0.02em;
    box-shadow: 0 8px 20px -10px rgba(0, 0, 0, 0.8);
    z-index: 3;
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

  /* Mobile: a smaller book sitting below the editor (§1). */
  @media (max-width: 760px) {
    svg {
      width: min(70%, 240px);
    }
    .book {
      gap: 0.9rem;
    }
    figcaption {
      font-size: 0.88rem;
    }
  }
</style>
