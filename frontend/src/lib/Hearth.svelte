<script lang="ts">
  // Firelight: a non-interactive radial glow low in one corner of the room
  // (§8). Flicker is opt-in and gentle (~5s opacity drift).
  import { settings } from "./settings.svelte";
</script>

<div class="hearth" class:flicker={settings.flicker} aria-hidden="true"></div>

<style>
  .hearth {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background: radial-gradient(
      120% 90% at 18% 118%,
      rgba(var(--fire-glow), 0.34),
      rgba(var(--fire-glow), 0.12) 32%,
      transparent 60%
    );
  }
  .flicker {
    animation: ember-flicker 5s ease-in-out infinite;
  }
  @keyframes ember-flicker {
    0%, 100% { opacity: 1; }
    42% { opacity: 0.82; }
    63% { opacity: 0.93; }
    78% { opacity: 0.86; }
  }
  @media (prefers-reduced-motion: reduce) {
    .flicker { animation: none; }
  }
</style>
