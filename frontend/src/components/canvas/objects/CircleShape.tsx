import type { CircleObject } from '../../../types/geometry'
import { closedShapeProps } from './closedShapeStyle'

type CircleShapeProps = {
  object: CircleObject
}

function CircleShape({ object }: CircleShapeProps) {
  return (
    <circle
      cx={object.cx}
      cy={object.cy}
      r={object.r}
      {...closedShapeProps}
    />
  )
}

export default CircleShape
