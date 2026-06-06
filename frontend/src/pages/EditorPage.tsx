import { Link, useParams } from 'react-router-dom'

import Sidebar from '../components/ui/Sidebar'
import Topbar from '../components/ui/Topbar'
import CanvasPlaceholder from '../components/canvas/CanvasPlaceholder'
import { useGeoEditor } from '../hooks/useGeoEditor'

function EditorPage({ mode }: { mode: 'guest' | 'canvas' }) {
  const { canvasId } = useParams()
  const {
    commandText,
    commandError,
    functionMessage,
    functionError,
    objects,
    canvasTitle,
    saveMessage,
    saveError,
    isReady,
    canSave,
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
    readOnly,
    authorName,
  } = useGeoEditor({ mode, canvasId })

  if (!isReady) {
    return <div className="editor-loading">Загрузка холста...</div>
  }

  return (
    <main className="app-shell">
      <Sidebar
        objects={objects}
        commandText={commandText}
        commandError={commandError}
        functionMessage={functionMessage}
        functionError={functionError}
        activeTool={activeTool}
        activeFunction={activeFunction}
        readOnly={readOnly}
        onCommandChange={handleCommandChange}
        onToolChange={handleToolChange}
        onFunctionChange={handleFunctionChange}
        onDeleteObject={handleDeleteObject}
      />

      <section className="workspace">
        <Topbar
          title={canvasTitle}
          canSave={canSave}
          saveMessage={saveMessage}
          saveError={saveError}
          onSave={handleSave}
        />
        <div className="editor-toolbar-row">
          <Link to="/">← На главную</Link>
          {mode === 'guest' && <span className="guest-badge">Гостевой режим</span>}
          {readOnly && (
            <span className="readonly-badge">
              Только просмотр
              {authorName ? ` · ${authorName}` : ''}
            </span>
          )}
        </div>
        <CanvasPlaceholder
          objects={objects}
          activeTool={activeTool}
          activeFunction={activeFunction}
          pendingSnaps={pendingSnaps}
          readOnly={readOnly}
          onCanvasClick={handleCanvasClick}
          onFinishPolygon={handleFinishPolygon}
          onClear={handleClear}
        />
      </section>
    </main>
  )
}

export default EditorPage
