import client from './client'
import type { ImportTask, ImportSubmitResult } from '@/types'

export async function uploadFiles(
  files: File[],
  metadata: Record<string, string>,
  chunkSize: number,
  chunkOverlap: number,
): Promise<ImportSubmitResult[]> {
  const formData = new FormData()
  files.forEach((f) => formData.append('files', f))
  formData.append('content_type', metadata.content_type)
  formData.append('course_name', metadata.course_name)
  formData.append('project_name', metadata.project_name)
  formData.append('chapter_name', metadata.chapter_name)
  formData.append('source_path', metadata.source_path)
  formData.append('chunk_size', String(chunkSize))
  formData.append('chunk_overlap', String(chunkOverlap))

  const { data } = await client.post<ImportSubmitResult[]>('/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return Array.isArray(data) ? data : [data]
}

export async function getImportStatus(taskId: number): Promise<ImportTask> {
  const { data } = await client.get<ImportTask>(`/import/${taskId}/status`)
  return data
}
