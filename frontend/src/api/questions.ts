import client from './client'
import type { Question, QuestionListItem } from '@/types'

export async function listQuestions(params: {
  keyword?: string
  course_name?: string
  question_type?: string
  question_bank_name?: string
  offset?: number
  limit?: number
}): Promise<QuestionListItem[]> {
  const { data } = await client.get('/questions', { params })
  return data
}

export async function getQuestion(id: number): Promise<Question> {
  const { data } = await client.get(`/questions/${id}`)
  return data
}

export async function createQuestion(body: {
  content: string
  question_type: string
  options?: string[]
  answer?: string
  explanation?: string
  question_bank_name?: string
  question_code?: string
  course_name?: string
  source_file?: string
}): Promise<{ id: number; content: string; question_type: string }> {
  const { data } = await client.post('/questions', body)
  return data
}
