// Shared reactive index (counts + streak). The editor's save response carries a
// freshly-rebuilt index, so writes update the book/ember without a refetch.
import { getIndex, type Index, type SaveResult } from "./api";

export const stats = $state<{ index: Index | null; loaded: boolean }>({
  index: null,
  loaded: false,
});

export async function refreshStats(): Promise<void> {
  try {
    stats.index = await getIndex();
  } catch {
    // leave the previous value; the UI shows an empty/loading state
  } finally {
    stats.loaded = true;
  }
}

export function applySave(result: SaveResult): void {
  stats.index = result.index;
  stats.loaded = true;
}
