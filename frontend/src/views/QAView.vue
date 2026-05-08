<template>
  <div class="qa-view">
    <el-card>
      <template #header>知识问答</template>

      <el-form :inline="true">
        <el-form-item label="对话">
          <el-select
            v-model="conversationId"
            placeholder="选择已有对话..."
            clearable
            style="width: 280px"
          >
            <el-option
              v-for="c in conversations"
              :key="c.id"
              :label="`#${c.id} ${c.title}`"
              :value="c.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button size="small" @click="newConversation">新建对话</el-button>
        </el-form-item>
      </el-form>

      <el-input
        v-model="query"
        type="textarea"
        :rows="4"
        placeholder="输入问题..."
        :disabled="streaming"
      />

      <div style="margin-top: 12px; display: flex; gap: 8px">
        <el-button type="primary" :loading="streaming" :disabled="!query.trim()" @click="doAsk">
          开始流式回答
        </el-button>
        <el-button :disabled="!streaming" @click="doStop">停止</el-button>
      </div>
    </el-card>

    <el-card style="margin-top: 16px">
      <template #header>
        <div class="card-header">
          <span>实时输出</span>
          <el-tag :type="streamStateType" size="small">{{ streamStateLabel }}</el-tag>
        </div>
      </template>
      <StreamOutput :text="answer" />
    </el-card>

    <el-card style="margin-top: 16px">
      <template #header>引用来源</template>
      <CitationPanel :citations="citations" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import StreamOutput from '@/components/StreamOutput.vue'
import CitationPanel from '@/components/CitationPanel.vue'
import { createStreamUrl } from '@/api/qa'
import { listConversations, createConversation } from '@/api/conversations'
import type { Conversation, Citation } from '@/types'

const query = ref('')
const answer = ref('')
const citations = ref<Citation[]>([])
const streaming = ref(false)
const streamState = ref<'idle' | 'streaming' | 'done' | 'error'>('idle')
const conversationId = ref<number | undefined>()
const conversations = ref<Conversation[]>([])

let abortController: AbortController | null = null

const streamStateType = {
  idle: 'info', streaming: '', done: 'success', error: 'danger',
} as const

const streamStateLabel = {
  idle: '空闲', streaming: '流式输出中', done: '已完成', error: '出错',
} as const

async function fetchConversations() {
  try {
    conversations.value = await listConversations({ limit: 50 })
  } catch { /* handled */ }
}

async function newConversation() {
  try {
    const c = await createConversation('新对话')
    conversations.value.unshift({ id: c.id, title: c.title, created_at: new Date().toISOString() })
    conversationId.value = c.id
    ElMessage.success('新对话已创建')
  } catch { /* handled */ }
}

async function doAsk() {
  if (!query.value.trim() || streaming.value) return

  streaming.value = true
  streamState.value = 'streaming'
  answer.value = ''
  citations.value = []
  abortController = new AbortController()

  const url = createStreamUrl()
  const body = JSON.stringify({ query: query.value, conversation_id: conversationId.value })

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body,
      signal: abortController.signal,
    })

    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    if (!response.body) throw new Error('不支持流式读取')

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        const payload = line.slice(6).trim()

        if (payload === '[DONE]') {
          streamState.value = 'done'
          return
        }
        if (payload.startsWith('[ERROR]')) {
          streamState.value = 'error'
          answer.value += `\n[错误] ${payload.slice(7)}`
          return
        }
        if (payload.startsWith('[CITATIONS]')) {
          try {
            citations.value = JSON.parse(payload.slice(11))
          } catch { /* ignore */ }
          continue
        }
        answer.value += payload
      }
    }

    if (streamState.value === 'streaming') {
      streamState.value = 'done'
    }
  } catch (err: any) {
    if (err.name === 'AbortError') {
      streamState.value = 'idle'
    } else {
      streamState.value = 'error'
      answer.value += `\n[错误] ${err.message}`
    }
  } finally {
    streaming.value = false
    abortController = null
  }
}

function doStop() {
  abortController?.abort()
}

onMounted(fetchConversations)
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
