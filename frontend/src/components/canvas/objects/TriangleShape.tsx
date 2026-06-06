import type { TriangleObject } from '../../../types/geometry'
import { closedShapeProps } from './closedShapeStyle'

type TriangleShapeProps = {
  object: TriangleObject
}

function TriangleShape({ object }: TriangleShapeProps) {
  const points = `${object.x1},${object.y1} ${object.x2},${object.y2} ${object.x3},${object.y3}`

  return (
    <polygon
      points={points}
      {...closedShapeProps}
    />
  )
}

export default TriangleShape
