import { apiFetch } from './http'
import type { CanvasSummary, HistoryEntry, PublishedCanvasSummary } from '../types/user'

type OpenCanvasResponse = {
  objects: unknown[]
  history: HistoryEntry[]
  error: string
  readonly: boolean
  author_name?: string
  canvas: CanvasSummary & { readonly?: boolean }
}

export async function fetchCanvases(): Promise<CanvasSummary[]> {
  const data = await apiFetch<{ canvases: CanvasSummary[] }>('/canvases')
  return data.canvases
}

export async function fetchPublishedCanvases(): Promise<PublishedCanvasSummary[]> {
  const data = await apiFetch<{ canvases: PublishedCanvasSummary[] }>('/canvases/published')
  return data.canvases
}

export async function setCanvasPublished(canvasId: string, published: boolean): Promise<CanvasSummary> {
  const data = await apiFetch<{ canvas: CanvasSummary }>(`/canvases/${canvasId}/publish`, {
    method: 'PATCH',
    body: { published },
  })
  return data.canvas
}

export async function createCanvas(title: string): Promise<CanvasSummary> {
  const data = await apiFetch<{ canvas: CanvasSummary }>('/canvases', {
    method: 'POST',
    body: { title },
  })
  return data.canvas
}

export async function openCanvas(canvasId: string): Promise<OpenCanvasResponse> {
  return apiFetch<OpenCanvasResponse>(`/canvases/${canvasId}/open`, {
    method: 'POST',
  })
}

export async function saveCanvas(canvasId: string, history: HistoryEntry[]): Promise<CanvasSummary> {
  const data = await apiFetch<{ canvas: CanvasSummary }>(`/canvases/${canvasId}`, {
    method: 'PUT',
    body: { history },
  })
  return data.canvas
}

export async function renameCanvas(canvasId: string, title: string): Promise<CanvasSummary> {
  const data = await apiFetch<{ canvas: CanvasSummary }>(`/canvases/${canvasId}`, {
    method: 'PATCH',
    body: { title },
  })
  return data.canvas
}

export async function deleteCanvas(canvasId: string): Promise<void> {
  await apiFetch(`/canvases/${canvasId}`, {
    method: 'DELETE',
  })
}

export async function resetGuestSession(): Promise<void> {
  await apiFetch('/session/reset', { method: 'POST', auth: false })
}
