import type { GeoObject } from '../../../types/geometry'
import PointShape from './PointShape'
import SegmentShape from './SegmentShape'
import LineShape from './LineShape'
import RayShape from './RayShape'
import CircleShape from './CircleShape'
import SquareShape from './SquareShape'
import TriangleShape from './TriangleShape'
import RhombusShape from './RhombusShape'
import ParallelogramShape from './ParallelogramShape'
import PolygonShape from './PolygonShape'

type ObjectsProps = {
  objects: GeoObject[]
}

function ObjectsLayer({ objects }: ObjectsProps) {
  return (
    <>
      {objects.map((obj) => {
        if (obj.type === 'point') {
          return <PointShape key={obj.id} object={obj} />
        }
        if (obj.type === 'segment') {
          return <SegmentShape key={obj.id} object={obj} />
        }
        if (obj.type === 'line') {
          return <LineShape key={obj.id} object={obj} />
        }
        if (obj.type === 'ray') {
          return <RayShape key={obj.id} object={obj} />
        }
        if (obj.type === 'circle') {
          return <CircleShape key={obj.id} object={obj} />
        }
        if (obj.type === 'square') {
          return <SquareShape key={obj.id} object={obj} />
        }
        if (obj.type === 'triangle') {
          return <TriangleShape key={obj.id} object={obj} />
        }
        if (obj.type === 'rhombus') {
          return <RhombusShape key={obj.id} object={obj} />
        }
        if (obj.type === 'parallelogram') {
          return <ParallelogramShape key={obj.id} object={obj} />
        }
        if (obj.type === 'polygon') {
          return <PolygonShape key={obj.id} object={obj} />
        }
        return null
      })}
    </>
  )
}

export default ObjectsLayer
