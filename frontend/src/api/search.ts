import client from './client'
import type { SearchResponse } from '@/types'

export async function searchDocuments(body: {
  query: string
  top_k?: number
  course_name?: string
  content_type?: string
}): Promise<SearchResponse> {
  const { data } = await client.post('/search/documents', body)
  return data
}
