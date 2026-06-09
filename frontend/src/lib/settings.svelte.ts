// Small persisted UI preferences. The firelight flicker is OFF by default —
// it shouldn't distract or burn phone battery (verso-plan.md §5, §8).
const FLICKER_KEY = "verso:flicker";

function loadFlicker(): boolean {
  try {
    return localStorage.getItem(FLICKER_KEY) === "1";
  } catch {
    return false;
  }
}

export const settings = $state<{ flicker: boolean }>({
  flicker: loadFlicker(),
});

export function setFlicker(on: boolean): void {
  settings.flicker = on;
  try {
    localStorage.setItem(FLICKER_KEY, on ? "1" : "0");
  } catch {
    // private mode / storage disabled — keep the in-memory value only
  }
}
