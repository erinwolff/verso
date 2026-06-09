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

export default app;
