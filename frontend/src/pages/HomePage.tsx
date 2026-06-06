import { Link, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'

import { fetchMe } from '../api/auth'
import {
  createCanvas,
  deleteCanvas,
  fetchCanvases,
  fetchPublishedCanvases,
  renameCanvas,
  setCanvasPublished,
} from '../api/canvases'
import { clearAuthToken } from '../auth/token'
import type { CanvasSummary, PublishedCanvasSummary, User } from '../types/user'

type CanvasTab = 'mine' | 'public'

function HomePage() {
  const navigate = useNavigate()
  const [user, setUser] = useState<User | null>(null)
  const [activeTab, setActiveTab] = useState<CanvasTab>('mine')
  const [canvases, setCanvases] = useState<CanvasSummary[]>([])
  const [publishedCanvases, setPublishedCanvases] = useState<PublishedCanvasSummary[]>([])
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const me = await fetchMe()
        setUser(me.user)

        if (me.user) {
          const [mine, published] = await Promise.all([
            fetchCanvases(),
            fetchPublishedCanvases(),
          ])
          setCanvases(mine)
          setPublishedCanvases(published)
        }
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : 'Ошибка загрузки')
      } finally {
        setIsLoading(false)
      }
    }

    load()
  }, [])

  async function handleCreateCanvas() {
    try {
      const canvas = await createCanvas('Новый холст')
      navigate(`/canvas/${canvas.id}`)
    } catch (createError) {
      setError(createError instanceof Error ? createError.message : 'Не удалось создать холст')
    }
  }

  async function handleRename(canvasId: string, title: string) {
    const trimmed = title.trim()
    if (!trimmed) {
      setError('Название не может быть пустым')
      return
    }

    try {
      const updated = await renameCanvas(canvasId, trimmed)
      setCanvases((items) => items.map((item) => (
        item.id === canvasId ? updated : item
      )))
      setError('')
    } catch (renameError) {
      setError(renameError instanceof Error ? renameError.message : 'Не удалось переименовать')
    }
  }

  async function handleDelete(canvasId: string) {
    try {
      await deleteCanvas(canvasId)
      setCanvases((items) => items.filter((item) => item.id !== canvasId))
      setPublishedCanvases((items) => items.filter((item) => item.id !== canvasId))
      setError('')
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : 'Не удалось удалить')
    }
  }

  async function handlePublishToggle(canvasId: string, published: boolean) {
    try {
      const updated = await setCanvasPublished(canvasId, published)
      setCanvases((items) => items.map((item) => (
        item.id === canvasId ? updated : item
      )))
      if (published) {
        setPublishedCanvases((items) => items.filter((item) => item.id !== canvasId))
      }
      setError('')
    } catch (publishError) {
      setError(publishError instanceof Error ? publishError.message : 'Не удалось изменить публикацию')
    }
  }

  function handleLogout() {
    clearAuthToken()
    setUser(null)
    setCanvases([])
    setPublishedCanvases([])
  }

  return (
    <div className="home-page">
      <header className="home-header">
        <div>
          <h1>Geo Mini</h1>
          <p>Геометрический редактор</p>
        </div>
        <div className="home-header-actions">
          {user ? (
            <>
              <span>{user.name}</span>
              <button type="button" onClick={handleLogout}>Выйти</button>
            </>
          ) : (
            <>
              <Link to="/login">Войти</Link>
              <Link to="/register">Регистрация</Link>
            </>
          )}
        </div>
      </header>

      <main className="home-main">
        {isLoading && <p>Загрузка...</p>}
        {error && <p className="home-error">{error}</p>}

        {!isLoading && !user && (
          <section className="home-section">
            <h2>Работа без регистрации</h2>
            <p>Один временный холст в памяти сервера. Сохранение недоступно.</p>
            <button type="button" onClick={() => navigate('/guest')}>
              Открыть гостевой холст
            </button>
          </section>
        )}

        {user && (
          <section className="home-section">
            <div className="home-section-header">
              <h2>Холсты</h2>
              {activeTab === 'mine' && (
                <button type="button" onClick={handleCreateCanvas}>
                  Создать холст
                </button>
              )}
            </div>

            <div className="canvas-tabs" role="tablist" aria-label="Разделы холстов">
              <button
                type="button"
                role="tab"
                aria-selected={activeTab === 'mine'}
                className={activeTab === 'mine' ? 'active' : ''}
                onClick={() => setActiveTab('mine')}
              >
                Мои холсты
              </button>
              <button
                type="button"
                role="tab"
                aria-selected={activeTab === 'public'}
                className={activeTab === 'public' ? 'active' : ''}
                onClick={() => setActiveTab('public')}
              >
                Доступные для просмотра
              </button>
            </div>

            {activeTab === 'mine' && (
              canvases.length === 0 ? (
                <p>Пока нет сохранённых холстов.</p>
              ) : (
                <ul className="canvas-list">
                  {canvases.map((canvas) => (
                    <li key={canvas.id} className="canvas-row">
                      <input
                        className="canvas-row-title"
                        value={canvas.title}
                        onChange={(event) => {
                          const nextTitle = event.target.value
                          setCanvases((items) => items.map((item) => (
                            item.id === canvas.id ? { ...item, title: nextTitle } : item
                          )))
                        }}
                        onBlur={(event) => handleRename(canvas.id, event.target.value)}
                        onKeyDown={(event) => {
                          if (event.key === 'Enter') {
                            event.currentTarget.blur()
                          }
                        }}
                      />
                      <span className="canvas-row-date">
                        {new Date(canvas.updated_at).toLocaleString()}
                      </span>
                      <label className="canvas-publish-toggle" title="Опубликовать в общий доступ">
                        <span>Опубликовать</span>
                        <input
                          type="checkbox"
                          checked={Boolean(canvas.published)}
                          onChange={(event) => handlePublishToggle(canvas.id, event.target.checked)}
                        />
                        <span className="canvas-publish-slider" aria-hidden="true" />
                      </label>
                      <button
                        type="button"
                        className="canvas-row-open"
                        onClick={() => navigate(`/canvas/${canvas.id}`)}
                      >
                        Открыть
                      </button>
                      <button
                        type="button"
                        className="canvas-row-delete"
                        onClick={() => handleDelete(canvas.id)}
                      >
                        Удалить
                      </button>
                    </li>
                  ))}
                </ul>
              )
            )}

            {activeTab === 'public' && (
              publishedCanvases.length === 0 ? (
                <p>Пока нет опубликованных холстов других пользователей.</p>
              ) : (
                <ul className="canvas-list">
                  {publishedCanvases.map((canvas) => (
                    <li key={canvas.id} className="canvas-row canvas-row-public">
                      <span className="canvas-row-title-static">{canvas.title}</span>
                      <span className="canvas-row-author">{canvas.author_name}</span>
                      <span className="canvas-row-date">
                        {new Date(canvas.updated_at).toLocaleString()}
                      </span>
                      <button
                        type="button"
                        className="canvas-row-open"
                        onClick={() => navigate(`/canvas/${canvas.id}`)}
                      >
                        Просмотр
                      </button>
                    </li>
                  ))}
                </ul>
              )
            )}
          </section>
        )}
      </main>
    </div>
  )
}

export default HomePage
