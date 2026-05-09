import client from './client'
import type { DocumentListResponse, DocumentSourceListResponse } from '@/types'

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

export async function listDocumentSources(params: {
  page?: number
  page_size?: number
  content_type?: string
  course_name?: string
  search?: string
} = {}): Promise<DocumentSourceListResponse> {
  const { data } = await client.get<DocumentSourceListResponse>('/documents/sources', { params })
  return data
}

export async function deleteDocument(id: number): Promise<void> {
  await client.delete(`/documents/${id}`)
}

export async function deleteDocumentSource(
  sourceFile: string,
  courseName: string = '',
  projectName: string = '',
): Promise<{ deleted: boolean; fragments_removed: number }> {
  const { data } = await client.delete('/documents/sources', {
    params: { source_file: sourceFile, course_name: courseName, project_name: projectName },
  })
  return data
}
