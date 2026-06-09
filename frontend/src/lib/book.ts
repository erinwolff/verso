// Geometry + labels for the filling book (verso-plan.md §6). Pure functions so
// they're unit-testable and reusable by the growth tween (P7).

export const BOOK = {
  // Front cover placement + size in SVG user units.
  coverX: 96,
  coverY: 120,
  W: 188,
  H: 210,
  // Oblique (cabinet-ish) projection: depth marches up-and-right, foreshortened.
  ux: Math.cos((32 * Math.PI) / 180) * 0.62, //  ~0.526 per unit thickness
  uy: -Math.sin((32 * Math.PI) / 180) * 0.62, // ~-0.329 (up)
  // Thickness curve: width = clamp(6, 6 + log2(n+1)*k, max). Log keeps every
  // entry additive without overflowing at year five.
  base: 6,
  k: 20,
  max: 220,
} as const;

export type Pt = { x: number; y: number };

export function thicknessUnits(count: number): number {
  const t = BOOK.base + Math.log2(count + 1) * BOOK.k;
  return Math.min(Math.max(t, BOOK.base), BOOK.max);
}

function poly(pts: Pt[]): string {
  return pts.map((p) => `${round(p.x)},${round(p.y)}`).join(" ");
}

function round(n: number): number {
  return Math.round(n * 100) / 100;
}

export type BookGeometry = {
  cover: { x: number; y: number; w: number; h: number };
  topFace: string; // points string for the top page-edge face
  rightFace: string; // points string for the fore-edge face
  /** Alternating page-edge leaf lines on the two visible faces. */
  leaves: { x1: number; y1: number; x2: number; y2: number; shade: boolean }[];
};

/** Build the page-block geometry for a given thickness in SVG units. */
export function geometryFor(thickness: number): BookGeometry {
  const { coverX: X, coverY: Y, W, H, ux, uy } = BOOK;
  const dx = thickness * ux;
  const dy = thickness * uy;

  const FTL = { x: X, y: Y };
  const FTR = { x: X + W, y: Y };
  const FBR = { x: X + W, y: Y + H };

  const rightFace = poly([
    FTR,
    FBR,
    { x: FBR.x + dx, y: FBR.y + dy },
    { x: FTR.x + dx, y: FTR.y + dy },
  ]);
  const topFace = poly([
    FTL,
    FTR,
    { x: FTR.x + dx, y: FTR.y + dy },
    { x: FTL.x + dx, y: FTL.y + dy },
  ]);

  // Decorative leaf lines: count scales with thickness, capped for sanity.
  const n = Math.min(Math.max(Math.round(thickness / 3), 2), 90);
  const leaves: BookGeometry["leaves"] = [];
  for (let i = 1; i <= n; i++) {
    const t = i / n;
    const ox = dx * t;
    const oy = dy * t;
    const shade = i % 2 === 0;
    // fore-edge (right face): vertical leaf edges marching back along depth
    leaves.push({
      x1: round(FTR.x + ox),
      y1: round(FTR.y + oy),
      x2: round(FBR.x + ox),
      y2: round(FBR.y + oy),
      shade,
    });
    // top face: leaf edges parallel to the cover's top edge
    leaves.push({
      x1: round(FTL.x + ox),
      y1: round(FTL.y + oy),
      x2: round(FTR.x + ox),
      y2: round(FTR.y + oy),
      shade,
    });
  }

  return {
    cover: { x: X, y: Y, w: W, h: H },
    topFace,
    rightFace,
    leaves,
  };
}

/** Caption thickness, entries*0.5mm rendered in cm to one decimal. */
export function thicknessLabel(count: number): string {
  const cm = (count * 0.5) / 10;
  return `${cm.toFixed(1)} cm`;
}
