// Tiny typed client for the Verso JSON API.

export type Streak = { count: number; state: "lit" | "warm" | "cold" };

export type Index = {
  entries: number;
  words: number;
  first: string | null;
  last: string | null;
  streak: Streak;
  generated: string;
};

export type Entry = {
  date: string;
  body: string;
  words: number;
  created: string | null;
  updated: string | null;
  exists: boolean;
};

export type EntryMeta = {
  date: string;
  updated: string;
  words: number;
  preview: string;
};

export type SaveResult = {
  entry: Omit<Entry, "exists"> | null;
  deleted: boolean;
  index: Index;
};

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) {
    throw new Error(`${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export function getEntry(date: string): Promise<Entry> {
  return fetch(`/api/entry/${date}`).then((r) => json<Entry>(r));
}

export function saveEntry(date: string, body: string): Promise<SaveResult> {
  return fetch(`/api/entry/${date}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ body }),
  }).then((r) => json<SaveResult>(r));
}

export function getEntries(): Promise<EntryMeta[]> {
  return fetch("/api/entries")
    .then((r) => json<{ entries: EntryMeta[] }>(r))
    .then((d) => d.entries);
}

export function getIndex(): Promise<Index> {
  return fetch("/api/index").then((r) => json<Index>(r));
}
