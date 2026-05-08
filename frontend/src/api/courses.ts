import client from './client'
import type { Course, CourseListItem } from '@/types'

export async function listCourses(params: {
  keyword?: string
  offset?: number
  limit?: number
}): Promise<CourseListItem[]> {
  const { data } = await client.get('/courses', { params })
  return data
}

export async function getCourse(id: number): Promise<Course> {
  const { data } = await client.get(`/courses/${id}`)
  return data
}

export async function createCourse(body: {
  name: string
  description?: string
  prerequisites?: string
  target_audience?: string
  learning_goals?: string
}): Promise<{ id: number; name: string }> {
  const { data } = await client.post('/courses', body)
  return data
}

export async function addChapter(courseId: number, body: { name: string; order: number }) {
  const { data } = await client.post(`/courses/${courseId}/chapters`, body)
  return data
}

export async function addProject(courseId: number, body: { name: string; description?: string }) {
  const { data } = await client.post(`/courses/${courseId}/projects`, body)
  return data
}
