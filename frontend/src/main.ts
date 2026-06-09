import { mount } from "svelte";
// Self-hosted EB Garamond (OFL), bundled into the build — no Google Fonts call.
import "@fontsource-variable/eb-garamond";
import "@fontsource-variable/eb-garamond/wght-italic.css";
import "./lib/tokens.css";
import "./app.css";
import App from "./App.svelte";

const app = mount(App, {
  target: document.getElementById("app")!,
});

// Register the service worker (offline reading + installable PWA). Dev runs
// over plain http on localhost, which SW allows; skip if unsupported.
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js").catch(() => {
      // non-fatal: the app still works without offline support
    });
  });
}

export default app;
