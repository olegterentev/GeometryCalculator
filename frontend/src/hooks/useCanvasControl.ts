import { useEffect, useRef, useState } from 'react'
import type { MouseEvent } from 'react'

import type { ActiveTool } from '../types/geometry'

export function useCanvasControl(activeTool: ActiveTool) {
  const svgRef = useRef<SVGSVGElement | null>(null)

  const [svgSize, setSvgSize] = useState({ width: 0, height: 0 })

  const [center, setCenter] = useState({ x: 0, y: 0 })

  const [drag, setDrag] = useState({
    isDragging: false,
    startX: 0,
    startY: 0,
    centerX: 0,
    centerY: 0,
  })

  useEffect(() => {
    function updateSvgSize() {
      if (!svgRef.current)
        return

      const rect = svgRef.current.getBoundingClientRect()
      setSvgSize({
        width: rect.width,
        height: rect.height,
      })
    }

    updateSvgSize()
    window.addEventListener('resize', updateSvgSize)

    return () => {
      window.removeEventListener('resize', updateSvgSize)
    }
  }, [])

  const pixelsPerUnit = 35
  const viewWidth = svgSize.width > 0 ? svgSize.width / pixelsPerUnit : 40
  const viewHeight = svgSize.height > 0 ? svgSize.height / pixelsPerUnit : 20

  const viewX = center.x - viewWidth / 2
  const viewY = -center.y - viewHeight / 2

  const xStart = Math.floor(center.x - viewWidth / 2)
  const xEnd = Math.ceil(center.x + viewWidth / 2)
  const yStart = Math.floor(center.y - viewHeight / 2)
  const yEnd = Math.ceil(center.y + viewHeight / 2)

  function handleMouseDown(event: MouseEvent<SVGSVGElement>) {
    if (activeTool !== 'move') {
      return
    }

    setDrag({
      isDragging: true,
      startX: event.clientX,
      startY: event.clientY,
      centerX: center.x,
      centerY: center.y,
    })
  }

  function handleMouseMove(event: MouseEvent<SVGSVGElement>) {
    if (!drag.isDragging || svgSize.width === 0 || svgSize.height === 0 || activeTool !== 'move') {
      return
    }

    const dx = ((event.clientX - drag.startX) / svgSize.width) * viewWidth
    const dy = ((event.clientY - drag.startY) / svgSize.height) * viewHeight

    setCenter({
      x: drag.centerX - dx,
      y: drag.centerY + dy,
    })
  }

  function stopDragging() {
    if (activeTool === 'move') {
      setDrag((currentDrag) => ({
        ...currentDrag,
        isDragging: false,
      }))
    }
  }

  function resetCenter() {
    setCenter({ x: 0, y: 0 })
  }

  function getSvgPoint(event: MouseEvent<SVGSVGElement>) {
    if (!svgRef.current) {
      return null
    }

    const svgPoint = svgRef.current.createSVGPoint()
    svgPoint.x = event.clientX
    svgPoint.y = event.clientY

    const screenMatrix = svgRef.current.getScreenCTM()
    if (!screenMatrix) {
      return null
    }

    const point = svgPoint.matrixTransform(screenMatrix.inverse())

    return {
      x: point.x,
      y: -point.y,
    }
  }

  return {
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
    resetCenter,
    getSvgPoint,
  }
}
