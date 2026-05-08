import client from './client'

export async function askSync(query: string, conversationId?: number) {
  const { data } = await client.post('/qa', { query, conversation_id: conversationId })
  return data
}

export function createStreamUrl(): string {
  const base = client.defaults.baseURL as string
  return `${base}/qa/stream`
}
