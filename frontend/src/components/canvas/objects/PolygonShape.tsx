import type { PolygonObject } from '../../../types/geometry'
import { closedShapeProps } from './closedShapeStyle'

type PolygonShapeProps = {
  object: PolygonObject
}

function PolygonShape({ object }: PolygonShapeProps) {
  const points = object.vertices.map((vertex) => `${vertex.x},${vertex.y}`).join(' ')

  return (
    <polygon
      points={points}
      {...closedShapeProps}
    />
  )
}

export default PolygonShape
