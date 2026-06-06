import type { GeoObject } from '../types/geometry'
import type { HistoryEntry } from '../types/user'

const API_URL = 'http://127.0.0.1:8000/commands'

export type CommandResult =
  | {
      success: true
      objects: GeoObject[]
      history: HistoryEntry[]
      error: string
    }
  | {
      success: false
      error: string
    }

export async function sendCommand(command: string): Promise<CommandResult> {
  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ command }),
    })

    if (!response.ok) {
      return {
        success: false,
        error: `Ошибка сервера: ${response.status}`,
      }
    }

    const data = await response.json()

    return {
      success: true,
      objects: data.objects ?? [],
      history: data.history ?? [],
      error: data.error ?? '',
    }
  } catch {
    return {
      success: false,
      error: 'Не удалось связаться с сервером. Запущен ли backend?',
    }
  }
}
