type GridLayerProps = {
  xStart: number
  xEnd: number
  yStart: number
  yEnd: number
}

function GridLayer({ xStart, xEnd, yStart, yEnd }: GridLayerProps) {
  const gridLines = []

  for (let x = xStart; x <= xEnd; x++) {
    gridLines.push(
      <line
        key={`vertical-${x}`}
        x1={x}
        y1={yStart}
        x2={x}
        y2={yEnd}
        stroke="#cccccc"
        strokeWidth={0.03}
      />,
    )
  }

  for (let y = yStart; y <= yEnd; y++) {
    gridLines.push(
      <line
        key={`horizontal-${y}`}
        x1={xStart}
        y1={y}
        x2={xEnd}
        y2={y}
        stroke="#cccccc"
        strokeWidth={0.03}
      />,
    )
  }

  return <>{gridLines}</>
}

export default GridLayer
