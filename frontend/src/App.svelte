<script lang="ts">
  // P0 scaffold: confirm the SPA mounts and can reach the FastAPI /api.
  let health = $state<string>("checking…");

  $effect(() => {
    fetch("/api/health")
      .then((r) => r.json())
      .then((d) => (health = `${d.app}: ${d.status}`))
      .catch(() => (health = "api unreachable"));
  });
</script>

<main>
  <h1>Verso</h1>
  <p class="sub">a quiet place to write</p>
  <p class="health">{health}</p>
</main>

<style>
  main {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.25rem;
  }
  h1 {
    font-weight: 500;
    letter-spacing: 0.04em;
    margin: 0;
  }
  .sub {
    margin: 0;
    opacity: 0.6;
    font-style: italic;
  }
  .health {
    margin-top: 1.5rem;
    font-size: 0.8rem;
    opacity: 0.4;
    font-family: ui-monospace, monospace;
  }
</style>
