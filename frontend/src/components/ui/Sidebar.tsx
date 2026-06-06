import { useState } from 'react'
import type { ActiveFunction, ActiveTool, GeoObject } from '../../types/geometry'

type SidebarProps = {
  objects: GeoObject[]
  commandText: string
  commandError: string
  functionMessage: string
  functionError: string
  activeTool: ActiveTool
  activeFunction: ActiveFunction | null
  readOnly?: boolean
  onCommandChange: (value: string) => void
  onToolChange: (tool: ActiveTool) => void
  onFunctionChange: (fn: ActiveFunction) => void
  onDeleteObject: (id: string) => void
}

type SidebarTab = 'navigation' | 'construction' | 'commands'

const FUNCTION_LABELS: Record<ActiveFunction, string> = {
  length: 'Длина отрезка',
  area: 'Площадь',
  perimeter: 'Периметр',
}

function Sidebar({
  objects,
  commandText,
  commandError,
  functionMessage,
  functionError,
  activeTool,
  activeFunction,
  readOnly = false,
  onCommandChange,
  onToolChange,
  onFunctionChange,
  onDeleteObject,
}: SidebarProps) {
  const [activeTab, setActiveTab] = useState<SidebarTab>('commands')

  return (
    <aside className="tools-panel">
      <div className="brand">
        <strong>Geo Mini</strong>
        <span>Инструменты</span>
      </div>
      <nav className="toolbar-tabs" aria-label="Разделы панели">
        <button
          type="button"
          className={activeTab === 'navigation' ? 'active' : ''}
          onClick={() => setActiveTab('navigation')}
        >
          Навигация
        </button>
        <button
          type="button"
          className={activeTab === 'construction' ? 'active' : ''}
          onClick={() => setActiveTab('construction')}
        >
          Построение
        </button>
        <button
          type="button"
          className={activeTab === 'commands' ? 'active' : ''}
          onClick={() => setActiveTab('commands')}
        >
          Команды
        </button>
      </nav>
      <div className="tools-panel-body">
      {activeTab === 'navigation' && (
        <section className="tool-section">
          <h2>Навигация</h2>
          <p>Перемещай холст мышью. Кнопка центрирования находится на холсте.</p>
          <button
            type="button"
            className={activeTool === 'move' ? 'active' : ''}
            onClick={() => onToolChange('move')}
          >
            перемещение
          </button>
        </section>
      )}

      {activeTab === 'construction' && (
        <section className="tool-section">
          <h2>Построение</h2>
          {readOnly && <p className="readonly-hint">Режим просмотра: построение недоступно.</p>}
          {!readOnly && (
          <>
          <button
            type="button"
            className={activeTool === 'point' ? 'active' : ''}
            onClick={() => onToolChange('point')}
          >
            Добавить точку
          </button>
          <button
            type="button"
            className={activeTool === 'segment' ? 'active' : ''}
            onClick={() => onToolChange('segment')}
          >
            Отрезок
          </button>
          <button
            type="button"
            className={activeTool === 'ray' ? 'active' : ''}
            onClick={() => onToolChange('ray')}
          >
            Луч
          </button>
          <button
            type="button"
            className={activeTool === 'line' ? 'active' : ''}
            onClick={() => onToolChange('line')}
          >
            Прямая
          </button>
          <button
            type="button"
            className={activeTool === 'circle' ? 'active' : ''}
            onClick={() => onToolChange('circle')}
          >
            Окружность
          </button>
          <button
            type="button"
            className={activeTool === 'square' ? 'active' : ''}
            onClick={() => onToolChange('square')}
          >
            Квадрат
          </button>
          <button
            type="button"
            className={activeTool === 'triangle' ? 'active' : ''}
            onClick={() => onToolChange('triangle')}
          >
            Треугольник
          </button>
          <button
            type="button"
            className={activeTool === 'rhombus' ? 'active' : ''}
            onClick={() => onToolChange('rhombus')}
          >
            Ромб
          </button>
          <button
            type="button"
            className={activeTool === 'parallelogram' ? 'active' : ''}
            onClick={() => onToolChange('parallelogram')}
          >
            Параллелограмм
          </button>
          <button
            type="button"
            className={activeTool === 'polygon' ? 'active' : ''}
            onClick={() => onToolChange('polygon')}
          >
            Полигон
          </button>
          </>
          )}

          <h2 className="tool-subsection-title">Функции</h2>
          <button
            type="button"
            className={activeFunction === 'length' ? 'active' : ''}
            onClick={() => onFunctionChange('length')}
          >
            Длина отрезка
          </button>
          <button
            type="button"
            className={activeFunction === 'area' ? 'active' : ''}
            onClick={() => onFunctionChange('area')}
          >
            Площадь
          </button>
          <button
            type="button"
            className={activeFunction === 'perimeter' ? 'active' : ''}
            onClick={() => onFunctionChange('perimeter')}
          >
            Периметр
          </button>
          {functionMessage && <p className="function-result">{functionMessage}</p>}
          {functionError && <p className="function-error">{functionError}</p>}
        </section>
      )}

      {activeTab === 'commands' && (
        <section className="tool-section tool-section-commands">
          <h2>Команды</h2>
          <div className="command-list">
            {objects.map((object) => (
              <div className="command-row" key={object.id}>
                <input
                  value={object.command}
                  readOnly
                />
                {!readOnly && (
                  <button
                    className="delete-object-button"
                    type="button"
                    onClick={() => onDeleteObject(object.id)}
                    aria-label={`Удалить ${object.label}`}
                  >
                    X
                  </button>
                )}
              </div>
            ))}
          </div>
          <div className="command-input-area">
            <input
              value={commandText}
              onChange={(event) => onCommandChange(event.target.value)}
              placeholder="Введите команду"
              readOnly={readOnly}
              disabled={readOnly}
            />
            {commandError && <p className="command-error">{commandError}</p>}
          </div>
        </section>
      )}
      </div>

      <section className="tool-section active-tool-section">
        <h2>Активный инструмент</h2>
        <p>{activeFunction ? FUNCTION_LABELS[activeFunction] : activeTool}</p>
      </section>
    </aside>
  )
}

export default Sidebar
