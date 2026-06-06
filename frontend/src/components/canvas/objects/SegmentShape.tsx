import type { SegmentObject } from '../../../types/geometry'

type SegmentShapeProps = {
  object: SegmentObject
}

function SegmentShape({ object }: SegmentShapeProps) {
  return (
    <line
      x1={object.x1}
      y1={object.y1}
      x2={object.x2}
      y2={object.y2}
      stroke="blue"
      strokeWidth={0.08}
    />
  )
}

export default SegmentShape
