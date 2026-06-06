import type { ActiveTool, GeoObject } from '../types/geometry'

export type SnapAnchor = {
  kind: 'free' | 'point' | 'grid'
  x: number
  y: number
  label?: string
}

const POINT_SNAP_THRESHOLD = 0.5
const CLOSE_POLYGON_THRESHOLD = 0.85
const GRID_SNAP_THRESHOLD = 0.15

export function isSnapTarget(snap: SnapAnchor | null): snap is SnapAnchor {
  return snap !== null && snap.kind === 'point'
}

function snapToGrid(click: { x: number; y: number }): SnapAnchor {
  const gridX = Math.round(click.x)
  const gridY = Math.round(click.y)
  const dx = Math.abs(click.x - gridX)
  const dy = Math.abs(click.y - gridY)

  if (dx <= GRID_SNAP_THRESHOLD && dy <= GRID_SNAP_THRESHOLD) {
    return {
      kind: 'grid',
      x: gridX,
      y: gridY,
    }
  }

  return {
    kind: 'free',
    x: click.x,
    y: click.y,
  }
}

function formatCoord(n: number): string {
  return Number(n.toFixed(2)).toString()
}

export function findSnap(
  click: { x: number; y: number },
  objects: GeoObject[],
): SnapAnchor {
  let best: { distance: number; anchor: SnapAnchor } | null = null

  for (const obj of objects) {
    if (obj.type !== 'point') {
      continue
    }

    const distance = Math.hypot(obj.x - click.x, obj.y - click.y)
    if (distance > POINT_SNAP_THRESHOLD) {
      continue
    }

    if (best === null || distance < best.distance) {
      best = {
        distance,
        anchor: {
          kind: 'point',
          x: obj.x,
          y: obj.y,
          label: obj.label,
        },
      }
    }
  }

  if (best !== null) {
    return best.anchor
  }

  return snapToGrid(click)
}

function snapToArgs(s: SnapAnchor): string[] {
  if (s.kind === 'point' && s.label) {
    return [s.label]
  }
  return [formatCoord(s.x), formatCoord(s.y)]
}

function buildTwoPointArgs(a: SnapAnchor, b: SnapAnchor): string {
  const aRef = a.kind === 'point' && a.label
  const bRef = b.kind === 'point' && b.label

  if (aRef && bRef) {
    return `${a.label}, ${b.label}`
  }
  if (aRef && !bRef) {
    return `${a.label}, ${formatCoord(b.x)}, ${formatCoord(b.y)}`
  }
  if (!aRef && bRef) {
    return `${formatCoord(a.x)}, ${formatCoord(a.y)}, ${b.label}`
  }
  return `${formatCoord(a.x)}, ${formatCoord(a.y)}, ${formatCoord(b.x)}, ${formatCoord(b.y)}`
}

function buildMultiPointArgs(snaps: SnapAnchor[]): string {
  return snaps.flatMap((snap) => snapToArgs(snap)).join(', ')
}

function buildThreePointArgs(a: SnapAnchor, b: SnapAnchor, c: SnapAnchor): string {
  return buildMultiPointArgs([a, b, c])
}

function isNearPoint(a: SnapAnchor, b: SnapAnchor): boolean {
  return Math.hypot(a.x - b.x, a.y - b.y) <= CLOSE_POLYGON_THRESHOLD
}

export function buildPolygonCommand(snaps: SnapAnchor[]): string | null {
  if (snaps.length < 3) {
    return null
  }

  return `Polygon(${buildMultiPointArgs(snaps)})`
}

const THREE_CLICK_OPS: Record<string, string> = {
  triangle: 'Triangle',
  rhombus: 'Rhombus',
  parallelogram: 'Parallelogram',
}

export function buildConstructionCommand(
  activeTool: ActiveTool,
  snap: SnapAnchor,
  pendingSnaps: SnapAnchor[],
): { command: string | null; pendingSnaps: SnapAnchor[] } {
  if (activeTool === 'point') {
    if (snap.kind === 'point') {
      return { command: null, pendingSnaps: [] }
    }
    return {
      command: `Point(${formatCoord(snap.x)}, ${formatCoord(snap.y)})`,
      pendingSnaps: [],
    }
  }

  if (activeTool === 'segment' || activeTool === 'line' || activeTool === 'ray' || activeTool === 'circle' || activeTool === 'square') {
    if (pendingSnaps.length === 0) {
      return { command: null, pendingSnaps: [snap] }
    }

    const op =
      activeTool === 'segment' ? 'Segment' :
      activeTool === 'ray' ? 'Ray' :
      activeTool === 'line' ? 'Line' :
      activeTool === 'circle' ? 'Circle' :
      'Square'

    return {
      command: `${op}(${buildTwoPointArgs(pendingSnaps[0], snap)})`,
      pendingSnaps: [],
    }
  }

  if (activeTool in THREE_CLICK_OPS) {
    if (pendingSnaps.length < 2) {
      return { command: null, pendingSnaps: [...pendingSnaps, snap] }
    }

    return {
      command: `${THREE_CLICK_OPS[activeTool]}(${buildThreePointArgs(pendingSnaps[0], pendingSnaps[1], snap)})`,
      pendingSnaps: [],
    }
  }

  if (activeTool === 'polygon') {
    if (pendingSnaps.length >= 3 && isNearPoint(snap, pendingSnaps[0])) {
      return {
        command: buildPolygonCommand(pendingSnaps),
        pendingSnaps: [],
      }
    }

    return { command: null, pendingSnaps: [...pendingSnaps, snap] }
  }

  return { command: null, pendingSnaps: [] }
}
