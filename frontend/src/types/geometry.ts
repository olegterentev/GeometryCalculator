export type PointObject = {
    id: string
    type: 'point'
    label: string
    command: string
    x: number
    y: number
}

export type LineObject = {
    id: string
    type: 'line'
    label: string
    command: string
    x1: number
    y1: number
    x2: number
    y2: number
}

export type SegmentObject = {
    id: string
    type: 'segment'
    label: string
    command: string
    x1: number
    y1: number
    x2: number
    y2: number
    length: number
}

export type RayObject = {
    id: string
    type: 'ray'
    label: string
    command: string
    x1: number
    y1: number
    x2: number
    y2: number
}

export type CircleObject = {
    id: string
    type: 'circle'
    label: string
    command: string
    cx: number
    cy: number
    r: number
    area: number
    perimeter: number
}

export type SquareObject = {
    id: string
    type: 'square'
    label: string
    command: string
    x1: number
    y1: number
    x2: number
    y2: number
    x3: number
    y3: number
    x4: number
    y4: number
    area: number
    perimeter: number
}

export type TriangleObject = {
    id: string
    type: 'triangle'
    label: string
    command: string
    x1: number
    y1: number
    x2: number
    y2: number
    x3: number
    y3: number
    area: number
    perimeter: number
}

export type RhombusObject = {
    id: string
    type: 'rhombus'
    label: string
    command: string
    x1: number
    y1: number
    x2: number
    y2: number
    x3: number
    y3: number
    x4: number
    y4: number
    area: number
    perimeter: number
}

export type ParallelogramObject = {
    id: string
    type: 'parallelogram'
    label: string
    command: string
    x1: number
    y1: number
    x2: number
    y2: number
    x3: number
    y3: number
    x4: number
    y4: number
    area: number
    perimeter: number
}

export type PolygonObject = {
    id: string
    type: 'polygon'
    label: string
    command: string
    vertices: { x: number; y: number }[]
    perimeter: number
}

export type ActiveFunction = 'length' | 'area' | 'perimeter'

export type ActiveTool = 'move' | 'point' | 'segment' | 'ray' | 'line' | 'circle' | 'square' | 'triangle' | 'rhombus' | 'parallelogram' | 'polygon'
export type GeoObject = PointObject | LineObject | SegmentObject | RayObject | CircleObject | SquareObject | TriangleObject | RhombusObject | ParallelogramObject | PolygonObject