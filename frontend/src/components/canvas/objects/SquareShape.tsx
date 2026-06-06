import type { SquareObject } from '../../../types/geometry'
import { closedShapeProps } from './closedShapeStyle'

type SquareShapeProps = {
  object: SquareObject
}

function SquareShape({ object }: SquareShapeProps) {
  const points = `${object.x1},${object.y1} ${object.x2},${object.y2} ${object.x3},${object.y3} ${object.x4},${object.y4}`

  return (
    <polygon
      points={points}
      {...closedShapeProps}
    />
  )
}

export default SquareShape
