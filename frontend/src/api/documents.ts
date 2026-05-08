import client from './client'
import type { DocumentListResponse } from '@/types'

export async function listDocuments(params: {
  page?: number
  page_size?: number
  content_type?: string
  course_name?: string
  search?: string
} = {}): Promise<DocumentListResponse> {
  const { data } = await client.get<DocumentListResponse>('/documents', { params })
  return data
}

export async function deleteDocument(id: number): Promise<void> {
  await client.delete(`/documents/${id}`)
}
