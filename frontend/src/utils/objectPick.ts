import type { GeoObject } from '../types/geometry'

const PICK_THRESHOLD = 0.5

function hypot(x: number, y: number): number {
  return Math.hypot(x, y)
}

function pointSegmentDistance(
  px: number,
  py: number,
  x1: number,
  y1: number,
  x2: number,
  y2: number,
): number {
  const dx = x2 - x1
  const dy = y2 - y1
  const lenSq = dx * dx + dy * dy

  if (lenSq < 1e-12) {
    return hypot(px - x1, py - y1)
  }

  let t = ((px - x1) * dx + (py - y1) * dy) / lenSq
  t = Math.max(0, Math.min(1, t))

  const projX = x1 + t * dx
  const projY = y1 + t * dy
  return hypot(px - projX, py - projY)
}

function pointInPolygon(px: number, py: number, vertices: { x: number; y: number }[]): boolean {
  let inside = false

  for (let i = 0, j = vertices.length - 1; i < vertices.length; j = i, i += 1) {
    const xi = vertices[i].x
    const yi = vertices[i].y
    const xj = vertices[j].x
    const yj = vertices[j].y

    const intersects = ((yi > py) !== (yj > py))
      && (px < ((xj - xi) * (py - yi)) / (yj - yi + 1e-12) + xi)

    if (intersects) {
      inside = !inside
    }
  }

  return inside
}

function quadVertices(obj: {
  x1: number
  y1: number
  x2: number
  y2: number
  x3: number
  y3: number
  x4: number
  y4: number
}) {
  return [
    { x: obj.x1, y: obj.y1 },
    { x: obj.x2, y: obj.y2 },
    { x: obj.x3, y: obj.y3 },
    { x: obj.x4, y: obj.y4 },
  ]
}

function distanceToObject(obj: GeoObject, px: number, py: number): number {
  if (obj.type === 'point') {
    return hypot(px - obj.x, py - obj.y)
  }

  if (obj.type === 'segment') {
    return pointSegmentDistance(px, py, obj.x1, obj.y1, obj.x2, obj.y2)
  }

  if (obj.type === 'line' || obj.type === 'ray') {
    const segDist = pointSegmentDistance(px, py, obj.x1, obj.y1, obj.x2, obj.y2)
    if (obj.type === 'line') {
      return segDist
    }

    const dx = obj.x2 - obj.x1
    const dy = obj.y2 - obj.y1
    const t = ((px - obj.x1) * dx + (py - obj.y1) * dy) / (dx * dx + dy * dy + 1e-12)
    if (t >= 0) {
      return segDist
    }

    return hypot(px - obj.x1, py - obj.y1)
  }

  if (obj.type === 'circle') {
    const centerDist = hypot(px - obj.cx, py - obj.cy)
    if (centerDist <= obj.r) {
      return 0
    }
    return centerDist - obj.r
  }

  if (obj.type === 'triangle') {
    const vertices = [
      { x: obj.x1, y: obj.y1 },
      { x: obj.x2, y: obj.y2 },
      { x: obj.x3, y: obj.y3 },
    ]
    if (pointInPolygon(px, py, vertices)) {
      return 0
    }
    return Math.min(
      pointSegmentDistance(px, py, obj.x1, obj.y1, obj.x2, obj.y2),
      pointSegmentDistance(px, py, obj.x2, obj.y2, obj.x3, obj.y3),
      pointSegmentDistance(px, py, obj.x3, obj.y3, obj.x1, obj.y1),
    )
  }

  if (obj.type === 'square' || obj.type === 'rhombus' || obj.type === 'parallelogram') {
    const vertices = quadVertices(obj)
    if (pointInPolygon(px, py, vertices)) {
      return 0
    }
    return Math.min(
      ...vertices.map((vertex, index) => {
        const next = vertices[(index + 1) % vertices.length]
        return pointSegmentDistance(px, py, vertex.x, vertex.y, next.x, next.y)
      }),
    )
  }

  if (obj.type === 'polygon') {
    if (pointInPolygon(px, py, obj.vertices)) {
      return 0
    }
    return Math.min(
      ...obj.vertices.map((vertex, index) => {
        const next = obj.vertices[(index + 1) % obj.vertices.length]
        return pointSegmentDistance(px, py, vertex.x, vertex.y, next.x, next.y)
      }),
    )
  }

  return Number.POSITIVE_INFINITY
}

/** 0 = точка, 1 = отрезок (и прямая/луч), 2 = фигура — для выбора метрик */
function metricPickTier(type: GeoObject['type']): number {
  if (type === 'point') {
    return 0
  }
  if (type === 'segment' || type === 'line' || type === 'ray') {
    return 1
  }
  return 2
}

function isBetterMetricPick(
  candidate: { distance: number; object: GeoObject },
  current: { distance: number; object: GeoObject },
): boolean {
  const candidateTier = metricPickTier(candidate.object.type)
  const currentTier = metricPickTier(current.object.type)

  if (candidateTier !== currentTier) {
    return candidateTier < currentTier
  }

  return candidate.distance < current.distance
}

/** Объект под курсором при клике для метрик (длина / площадь / периметр). */
export function findObjectAt(
  click: { x: number; y: number },
  objects: GeoObject[],
): GeoObject | null {
  let best: { distance: number; object: GeoObject } | null = null

  for (const obj of objects) {
    const distance = distanceToObject(obj, click.x, click.y)
    if (distance > PICK_THRESHOLD) {
      continue
    }

    const candidate = { distance, object: obj }
    if (best === null || isBetterMetricPick(candidate, best)) {
      best = candidate
    }
  }

  return best?.object ?? null
}
