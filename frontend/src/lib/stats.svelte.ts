// Shared reactive index (counts + streak). The editor's save response carries a
// freshly-rebuilt index, so writes update the book/ember without a refetch.
import {
  getEntries,
  getIndex,
  type EntryMeta,
  type Index,
  type SaveResult,
} from "./api";

export const stats = $state<{
  index: Index | null;
  entries: EntryMeta[];
  loaded: boolean;
}>({
  index: null,
  entries: [],
  loaded: false,
});

export async function refreshStats(): Promise<void> {
  try {
    const [index, entries] = await Promise.all([getIndex(), getEntries()]);
    stats.index = index;
    stats.entries = entries;
  } catch {
    // leave the previous value; the UI shows an empty/loading state
  } finally {
    stats.loaded = true;
  }
}

export async function refreshEntries(): Promise<void> {
  try {
    stats.entries = await getEntries();
  } catch {
    // keep prior list
  }
}

export function applySave(result: SaveResult): void {
  stats.index = result.index;
  stats.loaded = true;
  // The entry list may have gained or lost a day; refresh it.
  void refreshEntries();
}
