import { extendLine } from '../../utils/extendLine'
import { parallelogramVertices } from '../../utils/parallelogramVertices'
import { rhombusVerticesFromSideAndDirection } from '../../utils/rhombusVertices'
import { squareVerticesFromSide } from '../../utils/squareVertices'
import type { ActiveTool } from '../../types/geometry'
import { isSnapTarget, type SnapAnchor } from '../../utils/constructionClick'

type ConstructionPreviewProps = {
  activeTool: ActiveTool
  pendingSnaps: SnapAnchor[]
  cursorSnap: SnapAnchor | null
}

function ConstructionPreview({ activeTool, pendingSnaps, cursorSnap }: ConstructionPreviewProps) {
  const isTwoClickTool =
    activeTool === 'segment' ||
    activeTool === 'ray' ||
    activeTool === 'line' ||
    activeTool === 'circle' ||
    activeTool === 'square'

  const pendingSnap = pendingSnaps[0] ?? null

  return (
    <>
      {isSnapTarget(cursorSnap) && (
        <circle
          cx={cursorSnap.x}
          cy={cursorSnap.y}
          r={0.3}
          fill="none"
          stroke="#0066cc"
          strokeWidth={0.06}
        />
      )}

      {isTwoClickTool && pendingSnap && cursorSnap && (
        <>
          <circle
            cx={pendingSnap.x}
            cy={pendingSnap.y}
            r={0.25}
            fill="none"
            stroke="#0066cc"
            strokeWidth={0.08}
            strokeDasharray="0.15 0.1"
          />
          {activeTool === 'segment' && (
            <line
              x1={pendingSnap.x}
              y1={pendingSnap.y}
              x2={cursorSnap.x}
              y2={cursorSnap.y}
              stroke="#0066cc"
              strokeWidth={0.08}
              strokeDasharray="0.15 0.1"
            />
          )}
          {activeTool === 'circle' && (
            <circle
              cx={pendingSnap.x}
              cy={pendingSnap.y}
              r={Math.hypot(cursorSnap.x - pendingSnap.x, cursorSnap.y - pendingSnap.y)}
              fill="none"
              stroke="#0066cc"
              strokeWidth={0.08}
              strokeDasharray="0.15 0.1"
            />
          )}
          {activeTool === 'square' && (() => {
            const v = squareVerticesFromSide(
              pendingSnap.x,
              pendingSnap.y,
              cursorSnap.x,
              cursorSnap.y,
            )
            const points = `${v.x1},${v.y1} ${v.x2},${v.y2} ${v.x3},${v.y3} ${v.x4},${v.y4}`
            return (
              <polygon
                points={points}
                fill="none"
                stroke="#0066cc"
                strokeWidth={0.08}
                strokeDasharray="0.15 0.1"
              />
            )
          })()}
          {(activeTool === 'line' || activeTool === 'ray') && (() => {
            const extended = extendLine(
              pendingSnap.x,
              pendingSnap.y,
              cursorSnap.x,
              cursorSnap.y,
              activeTool,
            )
            if (!extended) {
              return null
            }
            return (
              <line
                x1={extended.x1}
                y1={extended.y1}
                x2={extended.x2}
                y2={extended.y2}
                stroke="#0066cc"
                strokeWidth={0.08}
                strokeDasharray="0.15 0.1"
              />
            )
          })()}
        </>
      )}

      {(activeTool === 'triangle' || activeTool === 'rhombus' || activeTool === 'parallelogram') && cursorSnap && (
        <>
          {pendingSnaps.map((snap, index) => (
            <circle
              key={`${snap.x}-${snap.y}-${index}`}
              cx={snap.x}
              cy={snap.y}
              r={0.25}
              fill="none"
              stroke="#0066cc"
              strokeWidth={0.08}
              strokeDasharray="0.15 0.1"
            />
          ))}
          {pendingSnaps.length === 1 && (
            <line
              x1={pendingSnaps[0].x}
              y1={pendingSnaps[0].y}
              x2={cursorSnap.x}
              y2={cursorSnap.y}
              stroke="#0066cc"
              strokeWidth={0.08}
              strokeDasharray="0.15 0.1"
            />
          )}
          {pendingSnaps.length === 2 && activeTool === 'triangle' && (
            <>
              <line
                x1={pendingSnaps[0].x}
                y1={pendingSnaps[0].y}
                x2={pendingSnaps[1].x}
                y2={pendingSnaps[1].y}
                stroke="#0066cc"
                strokeWidth={0.08}
                strokeDasharray="0.15 0.1"
              />
              <polygon
                points={`${pendingSnaps[0].x},${pendingSnaps[0].y} ${pendingSnaps[1].x},${pendingSnaps[1].y} ${cursorSnap.x},${cursorSnap.y}`}
                fill="none"
                stroke="#0066cc"
                strokeWidth={0.08}
                strokeDasharray="0.15 0.1"
              />
            </>
          )}
          {pendingSnaps.length === 2 && activeTool === 'rhombus' && (() => {
            const v = rhombusVerticesFromSideAndDirection(
              pendingSnaps[0].x,
              pendingSnaps[0].y,
              pendingSnaps[1].x,
              pendingSnaps[1].y,
              cursorSnap.x,
              cursorSnap.y,
            )
            if (!v) {
              return (
                <line
                  x1={pendingSnaps[0].x}
                  y1={pendingSnaps[0].y}
                  x2={pendingSnaps[1].x}
                  y2={pendingSnaps[1].y}
                  stroke="#0066cc"
                  strokeWidth={0.08}
                  strokeDasharray="0.15 0.1"
                />
              )
            }
            const points = `${v.x1},${v.y1} ${v.x2},${v.y2} ${v.x3},${v.y3} ${v.x4},${v.y4}`
            return (
              <polygon
                points={points}
                fill="none"
                stroke="#0066cc"
                strokeWidth={0.08}
                strokeDasharray="0.15 0.1"
              />
            )
          })()}
          {pendingSnaps.length === 2 && activeTool === 'parallelogram' && (() => {
            const v = parallelogramVertices(
              pendingSnaps[0].x,
              pendingSnaps[0].y,
              pendingSnaps[1].x,
              pendingSnaps[1].y,
              cursorSnap.x,
              cursorSnap.y,
            )
            const points = `${v.x1},${v.y1} ${v.x2},${v.y2} ${v.x3},${v.y3} ${v.x4},${v.y4}`
            return (
              <polygon
                points={points}
                fill="none"
                stroke="#0066cc"
                strokeWidth={0.08}
                strokeDasharray="0.15 0.1"
              />
            )
          })()}
        </>
      )}

      {activeTool === 'polygon' && cursorSnap && (
        <>
          {pendingSnaps.map((snap, index) => (
            <circle
              key={`${snap.x}-${snap.y}-${index}`}
              cx={snap.x}
              cy={snap.y}
              r={0.25}
              fill="none"
              stroke="#0066cc"
              strokeWidth={0.08}
              strokeDasharray="0.15 0.1"
            />
          ))}
          {pendingSnaps.map((snap, index) => {
            if (index === 0) {
              return null
            }
            const prev = pendingSnaps[index - 1]
            return (
              <line
                key={`line-${index}`}
                x1={prev.x}
                y1={prev.y}
                x2={snap.x}
                y2={snap.y}
                stroke="#0066cc"
                strokeWidth={0.08}
                strokeDasharray="0.15 0.1"
              />
            )
          })}
          {pendingSnaps.length > 0 && (
            <line
              x1={pendingSnaps[pendingSnaps.length - 1].x}
              y1={pendingSnaps[pendingSnaps.length - 1].y}
              x2={cursorSnap.x}
              y2={cursorSnap.y}
              stroke="#0066cc"
              strokeWidth={0.08}
              strokeDasharray="0.15 0.1"
            />
          )}
          {pendingSnaps.length >= 2 && (
            <polygon
              points={[...pendingSnaps, cursorSnap].map((snap) => `${snap.x},${snap.y}`).join(' ')}
              fill="none"
              stroke="#0066cc"
              strokeWidth={0.08}
              strokeDasharray="0.15 0.1"
            />
          )}
        </>
      )}
    </>
  )
}

export default ConstructionPreview
