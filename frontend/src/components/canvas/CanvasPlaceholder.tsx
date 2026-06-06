import { useState } from 'react'
import type { MouseEvent } from 'react'

import GridLayer from './GridLayer'
import AxisLayer, { AxisLines } from './AxisLayer'
import CanvasControls from './CanvasControls'
import ConstructionPreview from './ConstructionPreview'
import ObjectsLayer from './objects/ObjectsLayer'
import PointLabelsLayer from './objects/PointLabelsLayer'
import type { ActiveFunction, ActiveTool, GeoObject } from '../../types/geometry'
import { useCanvasControl } from '../../hooks/useCanvasControl'
import { findSnap, type SnapAnchor } from '../../utils/constructionClick'

type CanvasProps = {
  objects: GeoObject[]
  activeTool: ActiveTool
  activeFunction: ActiveFunction | null
  pendingSnaps: SnapAnchor[]
  readOnly?: boolean
  onCanvasClick: (point: { x: number; y: number }) => void
  onFinishPolygon: () => void
  onClear: () => void
}

function CanvasPlaceholder({
  objects,
  activeTool,
  activeFunction,
  pendingSnaps,
  readOnly = false,
  onCanvasClick,
  onFinishPolygon,
  onClear,
}: CanvasProps) {
  const [cursorSnap, setCursorSnap] = useState<SnapAnchor | null>(null)

  const {
    svgRef,
    viewX,
    viewY,
    viewWidth,
    viewHeight,
    xStart,
    xEnd,
    yStart,
    yEnd,
    drag,
    handleMouseDown,
    handleMouseMove,
    stopDragging,
    getSvgPoint,
    resetCenter,
  } = useCanvasControl(activeTool)

  function handleResetCenter(event: MouseEvent<HTMLButtonElement>) {
    event.stopPropagation()
    resetCenter()
  }

  function handleFinishPolygonClick(event: MouseEvent<HTMLButtonElement>) {
    event.stopPropagation()
    onFinishPolygon()
  }

  function handleClearClick(event: MouseEvent<HTMLButtonElement>) {
    event.stopPropagation()
    onClear()
  }

  function handleSvgMouseMove(event: MouseEvent<SVGSVGElement>) {
    handleMouseMove(event)

    if (activeTool === 'move' && activeFunction === null) {
      setCursorSnap(null)
      return
    }

    const point = getSvgPoint(event)
    if (!point) {
      return
    }

    setCursorSnap(findSnap(point, objects))
  }

  function handleSvgMouseLeave() {
    stopDragging()
    setCursorSnap(null)
  }

  function handleSvgClick(event: MouseEvent<SVGSVGElement>) {
    if (activeTool === 'move' && activeFunction === null) {
      return
    }

    if (drag.isDragging) {
      return
    }

    const point = getSvgPoint(event)
    if (!point) {
      return
    }

    onCanvasClick(point)
  }

  return (
    <section className="canvas-panel">
      <div className="canvas-placeholder">
        <svg
          ref={svgRef}
          className={`drawing-svg drawing-svg-${activeFunction ?? activeTool}`}
          viewBox={`${viewX} ${viewY} ${viewWidth} ${viewHeight}`}
          onMouseDown={handleMouseDown}
          onMouseMove={handleSvgMouseMove}
          onMouseUp={stopDragging}
          onMouseLeave={handleSvgMouseLeave}
          onClick={handleSvgClick}
        >
          <g transform="scale(1 -1)">
            <GridLayer xStart={xStart} xEnd={xEnd} yStart={yStart} yEnd={yEnd}/>
            <AxisLines xStart={xStart} xEnd={xEnd} yStart={yStart} yEnd={yEnd}/>
            <ObjectsLayer objects={objects} />
            <ConstructionPreview
              activeTool={activeTool}
              pendingSnaps={pendingSnaps}
              cursorSnap={cursorSnap}
            />
          </g>
          <AxisLayer xStart={xStart} xEnd={xEnd} yStart={yStart} yEnd={yEnd} viewY={viewY}/>
          <PointLabelsLayer objects={objects} />
        </svg>
        <CanvasControls
          onResetCenter={handleResetCenter}
          onClear={handleClearClick}
          readOnly={readOnly}
          showFinishPolygon={!readOnly && activeTool === 'polygon' && pendingSnaps.length >= 3}
          onFinishPolygon={handleFinishPolygonClick}
        />
      </div>
    </section>
  )
}

export default CanvasPlaceholder
