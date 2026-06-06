type AxisLinesProps = {
  xStart: number
  xEnd: number
  yStart: number
  yEnd: number
}

export function AxisLines({ xStart, xEnd, yStart, yEnd }: AxisLinesProps) {
  return (
    <>
      <line
        x1={xStart}
        y1={0}
        x2={xEnd}
        y2={0}
        stroke="black"
        strokeWidth={0.1}
      />
      <line
        x1={0}
        y1={yStart}
        x2={0}
        y2={yEnd}
        stroke="black"
        strokeWidth={0.1}
      />
    </>
  )
}

type AxisLayerProps = {
  xStart: number
  xEnd: number
  yStart: number
  yEnd: number
  viewY: number
}

function AxisLayer({ xStart, xEnd, yStart, yEnd, viewY }: AxisLayerProps) {
  const xLabels = []
  const yLabels = []

  for (let x = xStart; x <= xEnd; x++) {
    if (x === 0)
      continue

    xLabels.push(
      <text
        key={`x-label-${x}`}
        x={x - 0.2}
        y={0.8}
        fontSize={0.45}
        fill="black"
      >
        {x}
      </text>,
    )
  }

  for (let y = yStart; y <= yEnd; y++) {
    if (y === 0)
      continue

    yLabels.push(
      <text
        key={`y-label-${y}`}
        x={0.3}
        y={-y + 0.15}
        fontSize={0.45}
        fill="black"
      >
        {y}
      </text>,
    )
  }

  return (
    <>
      <text x={-0.5} y={0.5} fontSize={0.6} fill="black">
        o
      </text>
      <text x={xEnd - 1} y={-0.3} fontSize={0.7} fill="black">
        x
      </text>
      <text x={-0.7} y={viewY + 1} fontSize={0.7} fill="black">
        y
      </text>
      {xLabels}
      {yLabels}
    </>
  )
}

export default AxisLayer
