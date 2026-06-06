function round2(n: number): number {
  return Number(n.toFixed(2))
}

export function squareVerticesFromSide(
  p1x: number,
  p1y: number,
  p2x: number,
  p2y: number,
) {
  const x1 = round2(p1x)
  const y1 = round2(p1y)
  const x2 = round2(p2x)
  const y2 = round2(p2y)

  const vx = x2 - x1
  const vy = y2 - y1
  const px = -vy
  const py = vx

  return {
    x1,
    y1,
    x2,
    y2,
    x3: round2(x2 + px),
    y3: round2(y2 + py),
    x4: round2(x1 + px),
    y4: round2(y1 + py),
  }
}
