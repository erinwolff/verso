<script lang="ts">
  // The streak as an ember pill (§8): flame + "kept alight", with a one-day
  // "warm embers" grace before it goes cold.
  import type { Streak } from "./api";

  let { streak }: { streak: Streak } = $props();

  const days = $derived(streak.count === 1 ? "day" : "days");
</script>

<div class="ember ember--{streak.state}" title="Your writing streak">
  <svg class="flame" viewBox="0 0 24 24" aria-hidden="true">
    <path
      d="M12 2C9 6 7 8 7 13a5 5 0 0 0 10 0c0-2-1-4-2-5 0 1.5-1 2.5-2 2.5 0-3 1-6-1-8.5z"
      fill="currentColor"
    />
  </svg>
  <span class="text">
    {#if streak.state === "lit"}
      {streak.count} {days} kept alight
    {:else if streak.state === "warm"}
      {streak.count} {days} · embers still warm
    {:else}
      the hearth is cold
    {/if}
  </span>
</div>

<style>
  .ember {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.4rem 0.9rem;
    border-radius: 999px;
    border: 1px solid var(--surface-edge);
    background: color-mix(in srgb, var(--bg) 70%, transparent);
    font-family: var(--sans);
    font-size: 0.8rem;
    letter-spacing: 0.03em;
    color: var(--fire-soft);
  }
  .flame {
    width: 0.95rem;
    height: 0.95rem;
    flex: none;
  }

  /* lit: bright, with a soft glow */
  .ember--lit {
    color: var(--fire-soft);
  }
  .ember--lit .flame {
    color: var(--fire);
    filter: drop-shadow(0 0 4px rgba(var(--fire-glow), 0.6));
  }
  /* warm: grace state, dimmer flame */
  .ember--warm .flame {
    color: color-mix(in srgb, var(--fire) 70%, var(--muted));
  }
  /* cold: muted, no glow */
  .ember--cold {
    color: var(--muted);
  }
  .ember--cold .flame {
    color: var(--muted);
    opacity: 0.6;
  }
</style>
