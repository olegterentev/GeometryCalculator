import type { MouseEvent } from 'react'

type CanvasControlsProps = {
  onResetCenter: (event: MouseEvent<HTMLButtonElement>) => void
  onClear: (event: MouseEvent<HTMLButtonElement>) => void
  readOnly?: boolean
  showFinishPolygon?: boolean
  onFinishPolygon?: (event: MouseEvent<HTMLButtonElement>) => void
}

function CanvasControls({
  onResetCenter,
  onClear,
  readOnly = false,
  showFinishPolygon = false,
  onFinishPolygon,
}: CanvasControlsProps) {
  return (
    <div className="canvas-actions">
      <button
        className="canvas-action-button"
        type="button"
        onMouseDown={(event) => event.stopPropagation()}
        onClick={onResetCenter}
      >
        Центр
      </button>
      {showFinishPolygon && onFinishPolygon && (
        <button
          className="canvas-action-button"
          type="button"
          onMouseDown={(event) => event.stopPropagation()}
          onClick={onFinishPolygon}
        >
          Завершить
        </button>
      )}
      {!readOnly && (
        <button
          className="canvas-action-button"
          type="button"
          onMouseDown={(event) => event.stopPropagation()}
          onClick={onClear}
        >
          Очистить
        </button>
      )}
    </div>
  )
}

export default CanvasControls
