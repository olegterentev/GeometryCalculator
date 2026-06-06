function round2(n: number): number {
  return Number(n.toFixed(2))
}

export function parallelogramVertices(
  p1x: number,
  p1y: number,
  p2x: number,
  p2y: number,
  p4x: number,
  p4y: number,
) {
  const x1 = round2(p1x)
  const y1 = round2(p1y)
  const x2 = round2(p2x)
  const y2 = round2(p2y)
  const x4 = round2(p4x)
  const y4 = round2(p4y)

  const px = x4 - x1
  const py = y4 - y1

  return {
    x1,
    y1,
    x2,
    y2,
    x3: round2(x2 + px),
    y3: round2(y2 + py),
    x4,
    y4,
  }
}
