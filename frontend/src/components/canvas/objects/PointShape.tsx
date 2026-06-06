import type { PointObject } from '../../../types/geometry'

type PointShapeProps = {
  object: PointObject
}

function PointShape({ object }: PointShapeProps) {
  return (
    <circle
      cx={object.x}
      cy={object.y}
      r={0.2}
      fill="blue"
    />
  )
}

export default PointShape
