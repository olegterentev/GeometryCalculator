export function extendLine(
  x1: number,
  y1: number,
  x2: number,
  y2: number,
  mode: 'ray' | 'line',
) {
  const dx = x2 - x1
  const dy = y2 - y1
  const len = Math.hypot(dx, dy)

  if (len < 1e-9) {
    return null
  }

  const ux = dx / len
  const uy = dy / len
  const L = 5000

  if (mode === 'ray') {
    return {
      x1,
      y1,
      x2: x1 + ux * L,
      y2: y1 + uy * L,
    }
  }

  return {
    x1: x1 - ux * L,
    y1: y1 - uy * L,
    x2: x1 + ux * L,
    y2: y1 + uy * L,
  }
}
