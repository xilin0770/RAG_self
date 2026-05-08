import client from './client'
import type { Conversation, ConversationDetail } from '@/types'

export async function listConversations(params: {
  offset?: number
  limit?: number
}): Promise<Conversation[]> {
  const { data } = await client.get('/conversations', { params })
  return data
}

export async function createConversation(title: string): Promise<{ id: number; title: string }> {
  const { data } = await client.post('/conversations', { title })
  return data
}

export async function getConversation(id: number): Promise<ConversationDetail> {
  const { data } = await client.get(`/conversations/${id}`)
  return data
}

export async function deleteConversation(id: number): Promise<{ deleted: boolean }> {
  const { data } = await client.delete(`/conversations/${id}`)
  return data
}
