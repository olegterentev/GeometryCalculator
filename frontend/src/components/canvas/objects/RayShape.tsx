import type { RayObject } from '../../../types/geometry'
import { extendLine } from '../../../utils/extendLine'

type RayShapeProps = {
  object: RayObject
}

function RayShape({ object }: RayShapeProps) {
  const extended = extendLine(
    object.x1,
    object.y1,
    object.x2,
    object.y2,
    'ray',
  )

  if (extended === null) {
    return null
  }

  return (
    <line
      x1={extended.x1}
      y1={extended.y1}
      x2={extended.x2}
      y2={extended.y2}
      stroke="blue"
      strokeWidth={0.08}
    />
  )
}

export default RayShape
