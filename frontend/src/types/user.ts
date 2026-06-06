export type HistoryEntry = {
  id: string
  command: string
}

export type User = {
  id: string
  name: string
  email: string
  age: number | null
}

export type CanvasSummary = {
  id: string
  title: string
  updated_at: string
  published?: boolean
}

export type PublishedCanvasSummary = CanvasSummary & {
  author_name: string
}
