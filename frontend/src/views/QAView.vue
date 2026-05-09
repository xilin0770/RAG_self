<template>
  <div class="qa-view">
    <!-- Top toolbar -->
    <div class="qa-toolbar">
      <el-select
        v-model="conversationId"
        placeholder="选择已有对话..."
        clearable
        style="width: 300px"
        @change="onConversationChange"
      >
        <el-option
          v-for="c in conversations"
          :key="c.id"
          :label="`#${c.id} ${c.title}`"
          :value="c.id"
        />
      </el-select>
      <el-button @click="newConversation">新建对话</el-button>
    </div>

    <!-- Main area -->
    <div class="qa-main" v-if="conversationId">
      <!-- Left: chat area -->
      <div class="qa-chat">
        <div class="chat-messages" ref="chatContainerRef">
          <el-empty v-if="messages.length === 0 && !streaming" description="开始提问吧" :image-size="80" />
          <div
            v-for="msg in messages"
            :key="msg.id"
            class="chat-message"
            :class="{ 'chat-user': msg.role === 'user', 'chat-assistant': msg.role === 'assistant' }"
            @click="onMessageClick(msg)"
          >
            <div class="chat-bubble" :class="{ selected: selectedMessageId === msg.id }">
              <div class="chat-role">{{ msg.role === 'user' ? '你' : 'AI' }}</div>
              <div class="chat-content">{{ msg.content }}</div>
              <div class="chat-time">{{ formatTime(msg.created_at) }}</div>
            </div>
          </div>
          <!-- Streaming bubble -->
          <div v-if="streaming" class="chat-message chat-assistant">
            <div class="chat-bubble streaming">
              <div class="chat-role">AI</div>
              <div class="chat-content">{{ streamingContent }}<span class="cursor-blink">|</span></div>
            </div>
          </div>
        </div>
        <!-- Input area -->
        <div class="chat-input">
          <el-input
            v-model="query"
            type="textarea"
            :rows="3"
            placeholder="输入问题，回车发送..."
            :disabled="streaming"
            @keydown.enter.exact.prevent="doAsk"
          />
          <div class="chat-input-actions">
            <el-button type="primary" :loading="streaming" :disabled="!query.trim()" @click="doAsk">
              发送
            </el-button>
            <el-button :disabled="!streaming" @click="doStop">停止</el-button>
          </div>
        </div>
      </div>

      <!-- Right: citation panel -->
      <div class="qa-citations">
        <div class="citations-header">引用来源</div>
        <el-collapse v-if="selectedCitations.length > 0">
          <el-collapse-item
            v-for="(item, idx) in selectedCitations"
            :key="idx"
            :title="`引用 #${item.index}`"
          >
            <div class="citation-content">{{ item.content }}</div>
            <div class="citation-meta">
              <el-tag v-if="item.course_name" size="small">课程: {{ item.course_name }}</el-tag>
              <el-tag v-if="item.chapter_name" size="small" type="info">章节: {{ item.chapter_name }}</el-tag>
              <el-tag v-if="item.source_file" size="small" type="warning">来源: {{ item.source_file }}</el-tag>
            </div>
          </el-collapse-item>
        </el-collapse>
        <el-empty v-else description="点击 AI 消息查看引用" :image-size="60" />
      </div>
    </div>

    <!-- Empty state when no conversation selected -->
    <div class="qa-empty" v-else>
      <el-empty description="选择一个对话或新建对话开始知识问答" :image-size="100" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createStreamUrl } from '@/api/qa'
import { listConversations, createConversation, getConversation } from '@/api/conversations'
import type { Conversation, Message, Citation } from '@/types'

const route = useRoute()
const router = useRouter()

const query = ref('')
const streaming = ref(false)
const streamingContent = ref('')
const conversationId = ref<number | undefined>()
const conversations = ref<Conversation[]>([])
const messages = ref<Message[]>([])
const selectedMessageId = ref<number | null>(null)
const selectedCitations = ref<Citation[]>([])
const chatContainerRef = ref<HTMLElement>()

let abortController: AbortController | null = null

function formatTime(iso: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

async function fetchConversations() {
  try {
    conversations.value = await listConversations({ limit: 50 })
  } catch { /* handled */ }
}

async function loadConversationMessages(id: number) {
  try {
    const detail = await getConversation(id)
    messages.value = detail.messages || []
    if (detail.messages && detail.messages.length > 0) {
      const lastAssistant = [...detail.messages].reverse().find(m => m.role === 'assistant')
      if (lastAssistant && lastAssistant.citations) {
        selectedCitations.value = lastAssistant.citations
        selectedMessageId.value = lastAssistant.id
      }
    }
  } catch {
    messages.value = []
  }
}

function onConversationChange(id: number | undefined) {
  if (id) {
    router.replace({ query: { conversation_id: String(id) } })
    loadConversationMessages(id)
  } else {
    router.replace({ query: {} })
    messages.value = []
    selectedCitations.value = []
    selectedMessageId.value = null
  }
}

function onMessageClick(msg: Message) {
  if (msg.role === 'assistant' && msg.citations && msg.citations.length > 0) {
    selectedMessageId.value = msg.id
    selectedCitations.value = msg.citations
  }
}

async function newConversation() {
  try {
    const c = await createConversation('新对话')
    conversations.value.unshift({ id: c.id, title: c.title, created_at: new Date().toISOString() })
    conversationId.value = c.id
    messages.value = []
    selectedCitations.value = []
    selectedMessageId.value = null
    router.replace({ query: { conversation_id: String(c.id) } })
    ElMessage.success('新对话已创建')
  } catch { /* handled */ }
}

async function doAsk() {
  if (!query.value.trim() || streaming.value || !conversationId.value) return

  streaming.value = true
  streamingContent.value = ''
  abortController = new AbortController()

  const url = createStreamUrl()
  const body = JSON.stringify({ query: query.value, conversation_id: conversationId.value })
  const userQuery = query.value
  query.value = ''

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
    let receivedCitations: Citation[] = []

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
          break
        }
        if (payload.startsWith('[ERROR]')) {
          streamingContent.value += `\n[错误] ${payload.slice(7)}`
          break
        }
        if (payload.startsWith('[CITATIONS]')) {
          try {
            receivedCitations = JSON.parse(payload.slice(11))
            selectedCitations.value = receivedCitations
          } catch { /* ignore */ }
          continue
        }
        if (payload.startsWith('[CONV_ID]')) {
          try {
            const info = JSON.parse(payload.slice(9))
            if (info.conversation_id && !conversationId.value) {
              conversationId.value = info.conversation_id
              fetchConversations()
            }
          } catch { /* ignore */ }
          continue
        }
        streamingContent.value += payload
      }
    }

    // Save completed messages to the messages list
    messages.value.push({ id: Date.now(), role: 'user', content: userQuery, created_at: new Date().toISOString() })
    const assistantId = Date.now() + 1
    messages.value.push({
      id: assistantId,
      role: 'assistant',
      content: streamingContent.value,
      created_at: new Date().toISOString(),
      citations: receivedCitations,
    })
    selectedMessageId.value = assistantId
    selectedCitations.value = receivedCitations
    streamingContent.value = ''
  } catch (err: any) {
    if (err.name !== 'AbortError') {
      streamingContent.value += `\n[错误] ${err.message}`
    }
  } finally {
    streaming.value = false
    abortController = null
    await nextTick()
    scrollToBottom()
  }
}

function doStop() {
  abortController?.abort()
}

function scrollToBottom() {
  if (chatContainerRef.value) {
    chatContainerRef.value.scrollTop = chatContainerRef.value.scrollHeight
  }
}

watch(streamingContent, async () => {
  await nextTick()
  scrollToBottom()
})

onMounted(async () => {
  await fetchConversations()
  const idParam = route.query.conversation_id
  if (idParam) {
    const id = Number(idParam)
    if (!isNaN(id)) {
      conversationId.value = id
      await loadConversationMessages(id)
    }
  }
})
</script>

<style scoped>
.qa-view {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px);
  gap: 12px;
}

.qa-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.qa-main {
  display: flex;
  flex: 1;
  gap: 12px;
  min-height: 0;
}

.qa-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-message {
  display: flex;
}

.chat-user {
  justify-content: flex-end;
}

.chat-assistant {
  justify-content: flex-start;
}

.chat-bubble {
  max-width: 75%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  cursor: default;
}

.chat-user .chat-bubble {
  background: #409eff;
  color: #fff;
  border-bottom-right-radius: 4px;
}

.chat-assistant .chat-bubble {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-bottom-left-radius: 4px;
}

.chat-assistant .chat-bubble:hover,
.chat-bubble.selected {
  border-color: #409eff;
}

.chat-bubble.streaming {
  border-color: #67c23a;
}

.chat-role {
  font-size: 11px;
  font-weight: 600;
  margin-bottom: 4px;
  opacity: 0.7;
}

.chat-content {
  white-space: pre-wrap;
  word-break: break-word;
}

.chat-time {
  font-size: 11px;
  opacity: 0.6;
  margin-top: 4px;
  text-align: right;
}

.cursor-blink {
  animation: blink 1s step-end infinite;
  color: #67c23a;
}

@keyframes blink {
  50% { opacity: 0; }
}

.chat-input {
  margin-top: 8px;
  padding: 12px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.chat-input-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  justify-content: flex-end;
}

.qa-citations {
  width: 320px;
  flex-shrink: 0;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  padding: 12px;
  overflow-y: auto;
}

.citations-header {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 12px;
}

.citation-content {
  background: #f9fafb;
  padding: 10px;
  border-radius: 6px;
  margin-bottom: 8px;
  line-height: 1.6;
  font-size: 13px;
}

.citation-meta {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.qa-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
