import type { RhombusObject } from '../../../types/geometry'
import { closedShapeProps } from './closedShapeStyle'

type RhombusShapeProps = {
  object: RhombusObject
}

function RhombusShape({ object }: RhombusShapeProps) {
  const points = `${object.x1},${object.y1} ${object.x2},${object.y2} ${object.x3},${object.y3} ${object.x4},${object.y4}`

  return (
    <polygon
      points={points}
      {...closedShapeProps}
    />
  )
}

export default RhombusShape
