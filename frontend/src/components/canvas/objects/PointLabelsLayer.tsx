import type { GeoObject } from '../../../types/geometry'

type PointLabelsLayerProps = {
  objects: GeoObject[]
}

function PointLabelsLayer({ objects }: PointLabelsLayerProps) {
  return (
    <>
      {objects.map((object) => {
        if (object.type !== 'point') {
          return null
        }

        return (
          <text
            key={`${object.id}-label`}
            x={object.x + 0.3}
            y={-object.y - 0.3}
            fontSize={0.5}
            fill="black"
          >
            {object.label}
          </text>
        )
      })}
    </>
  )
}

export default PointLabelsLayer
