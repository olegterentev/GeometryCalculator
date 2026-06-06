import { useEffect, useState } from 'react'

import { sendCommand } from '../api/commands'
import { openCanvas, resetGuestSession, saveCanvas } from '../api/canvases'
import { applyFunction } from '../utils/applyFunction'
import {
  buildConstructionCommand,
  buildPolygonCommand,
  findSnap,
  type SnapAnchor,
} from '../utils/constructionClick'
import { findObjectAt } from '../utils/objectPick'
import type { ActiveFunction, ActiveTool, GeoObject } from '../types/geometry'
import type { HistoryEntry } from '../types/user'

type UseGeoEditorOptions = {
  mode: 'guest' | 'canvas'
  canvasId?: string
}

export function useGeoEditor({ mode, canvasId }: UseGeoEditorOptions) {
  const [commandText, setCommandText] = useState('')
  const [commandError, setCommandError] = useState('')
  const [functionMessage, setFunctionMessage] = useState('')
  const [functionError, setFunctionError] = useState('')
  const [objects, setObjects] = useState<GeoObject[]>([])
  const [history, setHistory] = useState<HistoryEntry[]>([])
  const [canvasTitle, setCanvasTitle] = useState('Гостевой холст')
  const [saveMessage, setSaveMessage] = useState('')
  const [saveError, setSaveError] = useState('')
  const [isReady, setIsReady] = useState(false)
  const [activeTool, setActiveTool] = useState<ActiveTool>('move')
  const [activeFunction, setActiveFunction] = useState<ActiveFunction | null>(null)
  const [pendingSnaps, setPendingSnaps] = useState<SnapAnchor[]>([])
  const [readOnly, setReadOnly] = useState(false)
  const [authorName, setAuthorName] = useState('')

  useEffect(() => {
    let cancelled = false

    async function loadSession() {
      try {
        if (mode === 'guest') {
          await resetGuestSession()
          if (cancelled) {
            return
          }
          setObjects([])
          setHistory([])
          setCanvasTitle('Гостевой холст')
          setReadOnly(false)
          setAuthorName('')
        } else if (canvasId) {
          const result = await openCanvas(canvasId)
          if (cancelled) {
            return
          }
          if (result.error) {
            setCommandError(result.error)
            return
          }
          setObjects(result.objects as GeoObject[])
          setHistory(result.history)
          setCanvasTitle(result.canvas.title)
          setReadOnly(Boolean(result.readonly))
          setAuthorName(result.author_name ?? '')
        }
      } catch (error) {
        if (!cancelled) {
          setCommandError(error instanceof Error ? error.message : 'Не удалось открыть холст')
        }
      } finally {
        if (!cancelled) {
          setIsReady(true)
        }
      }
    }

    setIsReady(false)
    loadSession()

    return () => {
      cancelled = true
    }
  }, [mode, canvasId])

  async function execute(command: string) {
    if (readOnly) {
      return
    }

    const result = await sendCommand(command)

    if (!result.success) {
      setCommandError(result.error)
      return
    }

    if (result.error) {
      setCommandError(result.error)
      return
    }

    setObjects(result.objects)
    setHistory(result.history)
    setCommandError('')
    setCommandText('')
  }

  async function handleSave() {
    if (mode !== 'canvas' || !canvasId) {
      return
    }

    setSaveMessage('')
    setSaveError('')

    try {
      await saveCanvas(canvasId, history)
      setSaveMessage('Сохранено')
    } catch (error) {
      setSaveError(error instanceof Error ? error.message : 'Не удалось сохранить')
    }
  }

  function handleDeleteObject(id: string) {
    execute(`Delete(${id})`)
  }

  function handleToolChange(tool: ActiveTool) {
    setPendingSnaps([])
    setActiveFunction(null)
    setFunctionMessage('')
    setFunctionError('')
    setActiveTool(tool)
  }

  function handleFunctionChange(fn: ActiveFunction) {
    setPendingSnaps([])
    setActiveTool('move')
    setActiveFunction(fn)
    setFunctionMessage('')
    setFunctionError('')
  }

  function handleCanvasClick(point: { x: number; y: number }) {
    if (readOnly && activeFunction === null) {
      return
    }

    if (activeFunction !== null) {
      const object = findObjectAt(point, objects)

      if (object === null) {
        setFunctionMessage('')
        setFunctionError('Кликните по объекту на холсте')
        return
      }

      const result = applyFunction(object, activeFunction)
      if (result.ok) {
        setFunctionMessage(result.message)
        setFunctionError('')
      } else {
        setFunctionMessage('')
        setFunctionError(result.message)
      }
      return
    }

    const snap = findSnap(point, objects)
    const { command, pendingSnaps: nextPending } = buildConstructionCommand(
      activeTool,
      snap,
      pendingSnaps,
    )

    if (command === null) {
      setPendingSnaps(nextPending)
      return
    }

    setPendingSnaps([])
    execute(command)
  }

  function handleFinishPolygon() {
    const command = buildPolygonCommand(pendingSnaps)
    if (command === null) {
      return
    }

    setPendingSnaps([])
    execute(command)
  }

  function handleClear() {
    setPendingSnaps([])
    setActiveFunction(null)
    setFunctionMessage('')
    setFunctionError('')
    setActiveTool('move')
    execute('Clear()')
  }

  function handleCommandChange(value: string) {
    setCommandText(value)
    setCommandError('')

    if (value.trim() === '') {
      return
    }

    execute(value)
  }

  return {
    commandText,
    commandError,
    functionMessage,
    functionError,
    objects,
    canvasTitle,
    saveMessage,
    saveError,
    isReady,
    readOnly,
    authorName,
    canSave: mode === 'canvas' && Boolean(canvasId) && !readOnly,
    activeTool,
    activeFunction,
    pendingSnaps,
    handleCommandChange,
    handleToolChange,
    handleFunctionChange,
    handleDeleteObject,
    handleCanvasClick,
    handleFinishPolygon,
    handleClear,
    handleSave,
  }
}
