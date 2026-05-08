# Vue 3 + Element Plus 前端重构实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将现有纯 HTML/JS 单页控制台重构为 Vue 3 + TypeScript + Element Plus 企业级前端，覆盖全部 6 个 API 模块，新增切分配置与文档搜索高亮。

**Architecture:** Vue 3 Composition API + Vite 构建，Element Plus 组件库提供企业后台布局。前端项目位于 `frontend/`，构建输出到 `app/web/static/`，复用 FastAPI 已有静态文件挂载。后端仅需微调 import 接口以支持切分参数和多文件。

**Tech Stack:** Vue 3.5, TypeScript, Element Plus 2.10, Vite 7, Vue Router 4, Pinia 3, Axios 1.9, pnpm

---

### Task 1: 项目脚手架

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/tsconfig.node.json`
- Create: `frontend/index.html`
- Create: `frontend/src/main.ts`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/env.d.ts`
- Create: `frontend/.gitignore`

- [ ] **Step 1: 创建 frontend 目录并初始化 package.json**

```bash
mkdir -p /home/xilin/project/RAG_self/frontend/src
```

写入 `frontend/package.json`:

```json
{
  "name": "rag-self-frontend",
  "private": true,
  "version": "0.2.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc -b && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.5.13",
    "vue-router": "^4.5.1",
    "pinia": "^3.0.3",
    "axios": "^1.9.0",
    "element-plus": "^2.10.2",
    "@element-plus/icons-vue": "^2.3.1"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.2.4",
    "typescript": "~5.8.3",
    "vite": "^7.0.6",
    "vue-tsc": "^2.2.12"
  }
}
```

- [ ] **Step 2: 安装依赖**

```bash
cd /home/xilin/project/RAG_self/frontend && pnpm install
```

Expected: `pnpm install` 成功，生成 `node_modules/` 和 `pnpm-lock.yaml`

- [ ] **Step 3: 创建 Vite 配置**

写入 `frontend/vite.config.ts`:

```ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
  build: {
    outDir: resolve(__dirname, '../app/web/static'),
    emptyOutDir: true,
  },
})
```

- [ ] **Step 4: 创建 TypeScript 配置**

写入 `frontend/tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "jsx": "preserve",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "noEmit": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

写入 `frontend/tsconfig.node.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "noEmit": true,
    "skipLibCheck": true
  },
  "include": ["vite.config.ts"]
}
```

- [ ] **Step 5: 创建 env.d.ts**

写入 `frontend/src/env.d.ts`:

```ts
/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}
```

- [ ] **Step 6: 创建入口 HTML 和最小 App**

写入 `frontend/index.html`:

```html
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>教育知识库 RAG 系统</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

写入 `frontend/src/main.ts`:

```ts
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import App from './App.vue'

const app = createApp(App)
app.use(ElementPlus, { locale: zhCn })
app.mount('#app')
```

写入 `frontend/src/App.vue`:

```vue
<template>
  <div>教育知识库 RAG 系统 — Vue 前端已就绪</div>
</template>
```

- [ ] **Step 7: 创建 .gitignore**

写入 `frontend/.gitignore`:

```
node_modules
dist
*.local
```

- [ ] **Step 8: 验证 dev server 启动**

```bash
cd /home/xilin/project/RAG_self/frontend && pnpm dev
```

启动后访问 `http://localhost:5173`，应看到占位文本。Ctrl+C 停止。

- [ ] **Step 9: 验证构建**

```bash
cd /home/xilin/project/RAG_self/frontend && pnpm build
```

Expected: 构建成功，`app/web/static/` 下生成 `index.html`、`assets/` 目录。

- [ ] **Step 10: Commit**

```bash
cd /home/xilin/project/RAG_self
git add frontend/package.json frontend/pnpm-lock.yaml frontend/vite.config.ts \
  frontend/tsconfig.json frontend/tsconfig.node.json frontend/index.html \
  frontend/src/main.ts frontend/src/App.vue frontend/src/env.d.ts \
  frontend/.gitignore
git commit -m "feat: scaffold Vue 3 + Vite + Element Plus frontend project"
```

---

### Task 2: TypeScript 类型定义

**Files:**
- Create: `frontend/src/types/index.ts`

- [ ] **Step 1: 写入所有共享类型定义**

写入 `frontend/src/types/index.ts`:

```ts
// ---- Import ----
export interface ImportTask {
  task_id: number
  file_name: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  total_chunks: number
  completed_chunks: number
  error_message?: string
  created_at: string
}

export interface ImportSubmitResult {
  task_id: number
  status: string
  file_name: string
}

export interface ImportMetadata {
  content_type: string
  course_name: string
  project_name: string
  chapter_name: string
  source_path: string
}

// ---- Course ----
export interface Course {
  id: number
  name: string
  description: string
  prerequisites: string
  target_audience: string
  learning_goals: string
  chapters: Chapter[]
  projects: Project[]
}

export interface CourseListItem {
  id: number
  name: string
  description: string
  target_audience: string
}

export interface Chapter {
  id: number
  name: string
  order: number
}

export interface Project {
  id: number
  name: string
  description: string
}

// ---- Question ----
export interface Question {
  id: number
  content: string
  question_type: 'single_choice' | 'multi_choice' | 'true_false' | 'fill_blank' | 'short_answer'
  options: string[]
  answer: string
  explanation: string
  question_bank_name: string
  question_code: string
  course_name: string
  source_file: string
}

export interface QuestionListItem {
  id: number
  content: string
  question_type: string
  question_bank_name: string
  question_code: string
  course_name: string
}

// ---- Search ----
export interface SearchResult {
  chunk_id: string
  content: string
  score: number
  course_name: string
  project_name: string
  chapter_name: string
  content_type: string
  source_file: string
  source_path: string
}

export interface SearchResponse {
  query: string
  total: number
  results: SearchResult[]
}

// ---- QA ----
export interface QARequest {
  query: string
  conversation_id?: number
}

export interface Citation {
  index: number
  content: string
  course_name?: string
  chapter_name?: string
  source_file?: string
}

// ---- Conversation ----
export interface Conversation {
  id: number
  title: string
  created_at: string
}

export interface ConversationDetail {
  id: number
  title: string
  messages: Message[]
}

export interface Message {
  id: number
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

// ---- API ----
export interface ApiError {
  detail: string
}
```

- [ ] **Step 2: Commit**

```bash
cd /home/xilin/project/RAG_self
git add frontend/src/types/index.ts
git commit -m "feat: add TypeScript type definitions for all API entities"
```

---

### Task 3: API 客户端层

**Files:**
- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/api/import.ts`
- Create: `frontend/src/api/courses.ts`
- Create: `frontend/src/api/search.ts`
- Create: `frontend/src/api/questions.ts`
- Create: `frontend/src/api/qa.ts`
- Create: `frontend/src/api/conversations.ts`

- [ ] **Step 1: 创建 Axios 实例与拦截器**

写入 `frontend/src/api/client.ts`:

```ts
import axios from 'axios'
import { ElMessage } from 'element-plus'

const client = axios.create({
  baseURL: localStorage.getItem('api_base_url') || window.location.origin,
  timeout: 30000,
})

client.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    ElMessage.error(message)
    return Promise.reject(error)
  },
)

export function setBaseUrl(url: string) {
  client.defaults.baseURL = url
  localStorage.setItem('api_base_url', url)
}

export function getBaseUrl(): string {
  return client.defaults.baseURL as string
}

export default client
```

- [ ] **Step 2: 创建 Import API**

写入 `frontend/src/api/import.ts`:

```ts
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
```

- [ ] **Step 3: 创建 Courses API**

写入 `frontend/src/api/courses.ts`:

```ts
import client from './client'
import type { Course, CourseListItem, Chapter, Project } from '@/types'

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
```

- [ ] **Step 4: 创建 Search API**

写入 `frontend/src/api/search.ts`:

```ts
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
```

- [ ] **Step 5: 创建 Questions API**

写入 `frontend/src/api/questions.ts`:

```ts
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
```

- [ ] **Step 6: 创建 QA API**

写入 `frontend/src/api/qa.ts`:

```ts
import client from './client'

export async function askSync(query: string, conversationId?: number) {
  const { data } = await client.post('/qa', { query, conversation_id: conversationId })
  return data
}

export function createStreamUrl(): string {
  const base = client.defaults.baseURL as string
  return `${base}/qa/stream`
}
```

- [ ] **Step 7: 创建 Conversations API**

写入 `frontend/src/api/conversations.ts`:

```ts
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
```

- [ ] **Step 8: Commit**

```bash
cd /home/xilin/project/RAG_self
git add frontend/src/api/
git commit -m "feat: add API client layer with all 6 module endpoints"
```

---

### Task 4: 高亮工具函数

**Files:**
- Create: `frontend/src/utils/highlight.ts`

- [ ] **Step 1: 写入高亮工具函数**

写入 `frontend/src/utils/highlight.ts`:

```ts
export function highlightText(text: string, query: string): string {
  if (!query.trim()) return escapeHtml(text)

  const escaped = query.trim().replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const terms = escaped.split(/\s+/).filter(Boolean)

  let result = escapeHtml(text)
  for (const term of terms) {
    const regex = new RegExp(`(${term})`, 'gi')
    result = result.replace(regex, '<mark>$1</mark>')
  }
  return result
}

function escapeHtml(raw: string): string {
  return raw
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;')
}
```

- [ ] **Step 2: Commit**

```bash
cd /home/xilin/project/RAG_self
git add frontend/src/utils/highlight.ts
git commit -m "feat: add search keyword highlight utility"
```

---

### Task 5: Vue Router 配置

**Files:**
- Create: `frontend/src/router/index.ts`

- [ ] **Step 1: 写入路由配置**

写入 `frontend/src/router/index.ts`:

```ts
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory('/web'),
  routes: [
    {
      path: '/',
      component: () => import('@/components/AppLayout.vue'),
      redirect: '/import',
      children: [
        {
          path: 'import',
          name: 'import',
          component: () => import('@/views/ImportView.vue'),
          meta: { title: '内容导入' },
        },
        {
          path: 'courses',
          name: 'courses',
          component: () => import('@/views/CourseListView.vue'),
          meta: { title: '课程管理' },
        },
        {
          path: 'courses/:id',
          name: 'course-detail',
          component: () => import('@/views/CourseDetailView.vue'),
          meta: { title: '课程详情' },
        },
        {
          path: 'questions',
          name: 'questions',
          component: () => import('@/views/QuestionListView.vue'),
          meta: { title: '题库管理' },
        },
        {
          path: 'search',
          name: 'search',
          component: () => import('@/views/SearchView.vue'),
          meta: { title: '文档检索' },
        },
        {
          path: 'qa',
          name: 'qa',
          component: () => import('@/views/QAView.vue'),
          meta: { title: '知识问答' },
        },
        {
          path: 'conversations',
          name: 'conversations',
          component: () => import('@/views/ConversationListView.vue'),
          meta: { title: '对话管理' },
        },
      ],
    },
  ],
})

export default router
```

- [ ] **Step 2: 更新 main.ts 注册 router**

修改 `frontend/src/main.ts`:

```ts
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(ElementPlus, { locale: zhCn })
app.use(router)
app.mount('#app')
```

修改 `frontend/src/App.vue`:

```vue
<template>
  <router-view />
</template>
```

- [ ] **Step 3: Commit**

```bash
cd /home/xilin/project/RAG_self
git add frontend/src/router/index.ts frontend/src/main.ts frontend/src/App.vue
git commit -m "feat: add Vue Router with all 6 module routes"
```

---

### Task 6: AppLayout 布局组件

**Files:**
- Create: `frontend/src/components/AppLayout.vue`

- [ ] **Step 1: 写入 AppLayout 组件**

写入 `frontend/src/components/AppLayout.vue`:

```vue
<template>
  <el-container class="app-layout">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="app-aside">
      <div class="logo" @click="$router.push('/')">
        <span v-if="!isCollapse">教育知识库</span>
        <span v-else>RAG</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/import">
          <el-icon><Upload /></el-icon>
          <span>内容导入</span>
        </el-menu-item>
        <el-menu-item index="/courses">
          <el-icon><Reading /></el-icon>
          <span>课程管理</span>
        </el-menu-item>
        <el-menu-item index="/questions">
          <el-icon><EditPen /></el-icon>
          <span>题库管理</span>
        </el-menu-item>
        <el-menu-item index="/search">
          <el-icon><Search /></el-icon>
          <span>文档检索</span>
        </el-menu-item>
        <el-menu-item index="/qa">
          <el-icon><ChatDotSquare /></el-icon>
          <span>知识问答</span>
        </el-menu-item>
        <el-menu-item index="/conversations">
          <el-icon><List /></el-icon>
          <span>对话管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="app-header">
        <div class="header-left">
          <el-button
            :icon="isCollapse ? Expand : Fold"
            text
            @click="isCollapse = !isCollapse"
          />
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentTitle">{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-tag :type="apiConnected ? 'success' : 'danger'" size="small">
            {{ apiConnected ? 'API 已连接' : 'API 断开' }}
          </el-tag>
        </div>
      </el-header>

      <el-main>
        <router-view />
      </el-main>

      <el-footer class="app-footer">
        教育知识库 RAG 系统 v0.2.0
      </el-footer>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  Upload, Reading, EditPen, Search, ChatDotSquare, List, Expand, Fold,
} from '@element-plus/icons-vue'

const route = useRoute()
const isCollapse = ref(false)
const apiConnected = ref(true)

const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/courses')) return '/courses'
  return path || '/import'
})

const currentTitle = computed(() => route.meta.title as string | undefined)
</script>

<style scoped>
.app-layout {
  height: 100vh;
}
.app-aside {
  background-color: #304156;
  overflow-y: auto;
  transition: width 0.3s;
}
.logo {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  padding: 0 16px;
  height: 56px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.app-footer {
  text-align: center;
  color: #999;
  font-size: 13px;
  line-height: 40px;
  border-top: 1px solid #e6e6e6;
}
</style>
```

- [ ] **Step 2: Commit**

```bash
cd /home/xilin/project/RAG_self
git add frontend/src/components/AppLayout.vue
git commit -m "feat: add AppLayout with collapsible sidebar and breadcrumb"
```

---

### Task 7: 后端改动 — Import 端点 + Web 路由

**Files:**
- Modify: `app/api/importer.py`
- Modify: `app/services/importer.py`
- Modify: `app/main.py`

- [ ] **Step 1: 修改 import API 端点支持多文件和切分参数**

修改 `app/api/importer.py`，将单文件改为多文件，新增 chunk_size 和 chunk_overlap：

```py
import json
from datetime import datetime
from typing import List

from fastapi import APIRouter, UploadFile, File, Form, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.import_task import ImportTask
from app.services.importer import run_import

router = APIRouter(prefix="/import", tags=["内容导入"])


@router.post("")
async def import_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    content_type: str = Form(default="doc_fragment"),
    course_name: str = Form(default=""),
    project_name: str = Form(default=""),
    chapter_name: str = Form(default=""),
    source_path: str = Form(default=""),
    chunk_size: int = Form(default=500),
    chunk_overlap: int = Form(default=50),
    db: Session = Depends(get_db),
):
    """上传一个或多个文档并异步导入到知识库。"""
    metadata = {
        "content_type": content_type,
        "course_name": course_name,
        "project_name": project_name,
        "chapter_name": chapter_name,
        "source_path": source_path,
    }
    results = []

    for file in files:
        file_bytes = await file.read()

        task = ImportTask(
            file_name=file.filename or "unknown",
            status="pending",
            metadata_json=json.dumps(metadata, ensure_ascii=False),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        background_tasks.add_task(
            run_import, task.id, file_bytes, file.filename, metadata,
            chunk_size, chunk_overlap,
        )
        results.append({"task_id": task.id, "status": task.status, "file_name": task.file_name})

    return results
```

- [ ] **Step 2: 修改 importer service 接收切分参数**

修改 `app/services/importer.py` 的 `run_import` 函数签名和 chunker 调用：

```py
from datetime import datetime

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.database import SessionLocal
from app.models.import_task import ImportTask
from app.models.document import DocumentFragment
from app.services.parser import parse_document
from app.services.embedding import embed_texts
from app.services.vector_store import add_chunks


def run_import(
    task_id: int,
    file_bytes: bytes,
    filename: str,
    metadata: dict,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
):
    """Run the full import pipeline and update task status."""
    db = SessionLocal()
    try:
        task = db.query(ImportTask).get(task_id)
        if not task:
            return

        task.status = "processing"
        task.updated_at = datetime.utcnow()
        db.commit()

        # 1. Parse
        text = parse_document(file_bytes, filename)

        # 2. Chunk with user-specified parameters
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", ".", " ", ""],
        )
        chunks = splitter.split_text(text)
        chunks = [c.strip() for c in chunks if c.strip()]
        if not chunks:
            raise ValueError("No text chunks produced")

        task.total_chunks = len(chunks)
        db.commit()

        # 3. Embed
        embeddings = embed_texts(chunks)

        # 4. Store in vector DB
        chunk_metadatas = [
            {
                "content_type": metadata.get("content_type", ""),
                "course_name": metadata.get("course_name", ""),
                "project_name": metadata.get("project_name", ""),
                "chapter_name": metadata.get("chapter_name", ""),
                "source_file": filename,
                "source_path": metadata.get("source_path", ""),
            }
            for _ in chunks
        ]
        chunk_ids = add_chunks(chunks, embeddings, chunk_metadatas)

        # 5. Write metadata to SQL
        for i, chunk in enumerate(chunks):
            fragment = DocumentFragment(
                content=chunk,
                content_type=metadata.get("content_type", ""),
                course_name=metadata.get("course_name", ""),
                project_name=metadata.get("project_name", ""),
                chapter_name=metadata.get("chapter_name", ""),
                source_file=filename,
                source_path=metadata.get("source_path", ""),
                chunk_id=chunk_ids[i],
            )
            db.add(fragment)

        # 6. Complete
        task.status = "completed"
        task.completed_chunks = len(chunks)
        task.progress = 100.0
        task.updated_at = datetime.utcnow()
        db.commit()

    except Exception as e:
        db.rollback()
        task = db.query(ImportTask).get(task_id)
        if task:
            task.status = "failed"
            task.error_message = str(e)
            task.updated_at = datetime.utcnow()
            db.commit()
    finally:
        db.close()
```

- [ ] **Step 3: 修改 main.py Web 路由支持 SPA 回退**

修改 `app/main.py` 的 `/web` 路由部分，添加 catch-all 路由：

```py
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.database import init_db
from app.api import importer, courses, search, questions, qa, conversations

WEB_DIR = Path(__file__).resolve().parent / "web"
WEB_STATIC_DIR = WEB_DIR / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="教育知识库 RAG 系统",
    description="面向教育培训场景的智能知识库系统，支持内容导入、课程检索、文档检索、题库检索和知识问答",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(importer.router)
app.include_router(courses.router)
app.include_router(search.router)
app.include_router(questions.router)
app.include_router(qa.router)
app.include_router(conversations.router)
app.mount("/web/static", StaticFiles(directory=str(WEB_STATIC_DIR)), name="web-static")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )


@app.get("/")
def root():
    return {"message": "教育知识库 RAG 系统 API", "docs": "/docs"}


@app.get("/web", include_in_schema=False)
@app.get("/web/", include_in_schema=False)
def web_console():
    return FileResponse(str(WEB_DIR / "index.html"))


@app.get("/web/{rest:path}", include_in_schema=False)
def web_spa_fallback(rest: str):
    """SPA fallback — return index.html for all /web/* routes."""
    index_path = WEB_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return JSONResponse(status_code=404, content={"error": "Web console not built"})
```

- [ ] **Step 4: 运行后端测试验证**

```bash
cd /home/xilin/project/RAG_self && python -m pytest tests/ -v
```

Expected: 已有测试通过，改动不破坏现有功能。

- [ ] **Step 5: Commit**

```bash
cd /home/xilin/project/RAG_self
git add app/api/importer.py app/services/importer.py app/main.py
git commit -m "feat: support multi-file upload, configurable chunk params, and SPA fallback"
```

---

### Task 8: ImportView — 内容导入页面

**Files:**
- Create: `frontend/src/views/ImportView.vue`

- [ ] **Step 1: 写入 ImportView 组件**

写入 `frontend/src/views/ImportView.vue`:

```vue
<template>
  <div class="import-view">
    <el-card class="upload-card">
      <template #header>内容导入</template>

      <!-- Upload area -->
      <el-upload
        v-model:file-list="fileList"
        :auto-upload="false"
        drag
        multiple
        :accept="'.pdf,.md,.docx,.txt,.markdown,.doc'"
        :on-remove="onRemove"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">拖拽文件到此处或 <em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">支持 PDF、Markdown、DOCX、TXT 格式，可多选</div>
        </template>
      </el-upload>

      <!-- Chunk config -->
      <el-row :gutter="16" style="margin-top: 16px">
        <el-col :span="12">
          <el-form-item label="Chunk Size">
            <el-input-number v-model="chunkSize" :min="100" :max="2000" :step="50" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Chunk Overlap">
            <el-input-number v-model="chunkOverlap" :min="0" :max="500" :step="10" />
          </el-form-item>
        </el-col>
      </el-row>

      <!-- Metadata form -->
      <el-form :model="metadata" label-width="80px" :inline="true">
        <el-form-item label="内容类型">
          <el-input v-model="metadata.content_type" placeholder="doc_fragment" />
        </el-form-item>
        <el-form-item label="课程名">
          <el-input v-model="metadata.course_name" placeholder="Python 入门" />
        </el-form-item>
        <el-form-item label="项目名">
          <el-input v-model="metadata.project_name" placeholder="RAG 实战" />
        </el-form-item>
        <el-form-item label="章节名">
          <el-input v-model="metadata.chapter_name" placeholder="向量检索" />
        </el-form-item>
        <el-form-item label="来源路径">
          <el-input v-model="metadata.source_path" placeholder="course/python/chapter1.md" />
        </el-form-item>
      </el-form>

      <el-button type="primary" :loading="uploading" :disabled="fileList.length === 0" @click="submitImport">
        {{ uploading ? '提交中...' : '开始导入' }}
      </el-button>
    </el-card>

    <!-- Task list -->
    <el-card class="task-card" style="margin-top: 16px">
      <template #header>
        <div class="card-header">
          <span>导入任务</span>
          <el-button :type="polling ? 'danger' : 'default'" size="small" @click="togglePolling">
            {{ polling ? '停止轮询' : '自动轮询' }}
          </el-button>
        </div>
      </template>

      <el-table :data="tasks" stripe>
        <el-table-column prop="task_id" label="任务ID" width="80" />
        <el-table-column prop="file_name" label="文件名" min-width="180" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag
              :type="statusTagType(row.status)"
              size="small"
            >{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="进度" width="200">
          <template #default="{ row }">
            <el-progress
              :percentage="row.progress || 0"
              :status="row.status === 'failed' ? 'exception' : row.status === 'completed' ? 'success' : undefined"
            />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="更新时间" width="170" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" @click="refreshTask(row.task_id)">刷新</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import type { UploadFile } from 'element-plus'
import { uploadFiles, getImportStatus } from '@/api/import'
import type { ImportTask } from '@/types'

const fileList = ref<UploadFile[]>([])
const chunkSize = ref(500)
const chunkOverlap = ref(50)
const uploading = ref(false)
const tasks = ref<ImportTask[]>([])

const metadata = reactive({
  content_type: 'doc_fragment',
  course_name: '',
  project_name: '',
  chapter_name: '',
  source_path: '',
})

let pollTimer: ReturnType<typeof setInterval> | null = null
const polling = ref(false)

function onRemove(file: UploadFile) {
  const idx = fileList.value.indexOf(file)
  if (idx > -1) fileList.value.splice(idx, 1)
}

async function submitImport() {
  const files = fileList.value.map((f) => f.raw!).filter(Boolean)
  if (files.length === 0) return

  uploading.value = true
  try {
    const results = await uploadFiles(files, { ...metadata }, chunkSize.value, chunkOverlap.value)
    for (const r of results) {
      tasks.value.unshift({
        task_id: r.task_id,
        file_name: r.file_name,
        status: 'pending',
        progress: 0,
        total_chunks: 0,
        completed_chunks: 0,
        created_at: new Date().toISOString(),
      })
    }
    ElMessage.success(`${results.length} 个文件已提交导入`)
    fileList.value = []
    if (!polling.value) startPolling()
  } catch {
    // error handled by interceptor
  } finally {
    uploading.value = false
  }
}

async function refreshTask(taskId: number) {
  try {
    const data = await getImportStatus(taskId)
    const idx = tasks.value.findIndex((t) => t.task_id === taskId)
    if (idx > -1) tasks.value[idx] = data
  } catch {
    // handled by interceptor
  }
}

async function refreshAllTasks() {
  const pendingTasks = tasks.value.filter(
    (t) => !['completed', 'failed'].includes(t.status),
  )
  for (const t of pendingTasks) {
    await refreshTask(t.task_id)
  }
}

function startPolling() {
  polling.value = true
  pollTimer = setInterval(refreshAllTasks, 2000)
}

function stopPolling() {
  polling.value = false
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

function togglePolling() {
  polling.value ? stopPolling() : startPolling()
}

function statusTagType(status: string) {
  const map: Record<string, string> = {
    pending: 'info', processing: 'warning', completed: 'success', failed: 'danger',
  }
  return map[status] || 'info'
}

function statusLabel(status: string) {
  const map: Record<string, string> = {
    pending: '等待中', processing: '处理中', completed: '已完成', failed: '失败',
  }
  return map[status] || status
}

onUnmounted(() => stopPolling())
</script>

<style scoped>
.upload-card :deep(.el-upload) {
  width: 100%;
}
.upload-card :deep(.el-upload-dragger) {
  width: 100%;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
```

- [ ] **Step 2: Commit**

```bash
cd /home/xilin/project/RAG_self
git add frontend/src/views/ImportView.vue
git commit -m "feat: add ImportView with multi-file upload, chunk config, and task polling"
```

---

### Task 9: SearchView + SearchHighlight — 文档检索页面

**Files:**
- Create: `frontend/src/views/SearchView.vue`
- Create: `frontend/src/components/SearchHighlight.vue`

- [ ] **Step 1: 创建 SearchHighlight 组件**

写入 `frontend/src/components/SearchHighlight.vue`:

```vue
<template>
  <span v-html="highlighted" />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { highlightText } from '@/utils/highlight'

const props = defineProps<{
  text: string
  query: string
}>()

const highlighted = computed(() => highlightText(props.text, props.query))
</script>
```

- [ ] **Step 2: 创建 SearchView**

写入 `frontend/src/views/SearchView.vue`:

```vue
<template>
  <div class="search-view">
    <el-card>
      <template #header>文档检索</template>

      <el-form :inline="true" :model="form">
        <el-form-item label="搜索关键词">
          <el-input
            v-model="form.query"
            placeholder="输入关键词..."
            style="width: 360px"
            clearable
            @keyup.enter="doSearch"
          />
        </el-form-item>
        <el-form-item label="课程筛选">
          <el-select v-model="form.course_name" placeholder="全部" clearable style="width: 180px">
            <el-option
              v-for="c in courseOptions"
              :key="c.value"
              :label="c.label"
              :value="c.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="内容类型">
          <el-select v-model="form.content_type" placeholder="全部" clearable style="width: 140px">
            <el-option label="文档片段" value="doc_fragment" />
            <el-option label="课程介绍" value="course_intro" />
            <el-option label="项目资料" value="project_material" />
          </el-select>
        </el-form-item>
        <el-form-item label="Top-K">
          <el-input-number v-model="form.top_k" :min="1" :max="20" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="searching" @click="doSearch">搜索</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <div v-if="results.length > 0" class="results-info" style="margin-top: 12px">
      共 {{ results.length }} 条结果
    </div>

    <el-card v-for="(item, idx) in results" :key="item.chunk_id" style="margin-top: 12px">
      <div class="result-header">
        <el-tag type="success" size="small">相似度: {{ (item.score * 100).toFixed(1) }}%</el-tag>
        <el-tag v-if="item.course_name" size="small">课程: {{ item.course_name }}</el-tag>
        <el-tag v-if="item.chapter_name" type="info" size="small">章节: {{ item.chapter_name }}</el-tag>
        <span class="result-index">#{{ idx + 1 }}</span>
      </div>
      <div class="result-content">
        <SearchHighlight :text="item.content" :query="lastQuery" />
      </div>
      <div v-if="item.source_file" class="result-meta">
        来源: {{ item.source_file }}
        <span v-if="item.project_name"> | 项目: {{ item.project_name }}</span>
      </div>
    </el-card>

    <el-empty v-if="searched && results.length === 0" description="未找到匹配的文档片段" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import SearchHighlight from '@/components/SearchHighlight.vue'
import { searchDocuments } from '@/api/search'
import { listCourses } from '@/api/courses'
import type { SearchResult } from '@/types'

const form = reactive({
  query: '',
  course_name: '',
  content_type: '',
  top_k: 5,
})

const results = ref<SearchResult[]>([])
const searching = ref(false)
const searched = ref(false)
const lastQuery = ref('')
const courseOptions = ref<{ label: string; value: string }[]>([])

onMounted(async () => {
  try {
    const courses = await listCourses({ limit: 100 })
    courseOptions.value = courses.map((c) => ({ label: c.name, value: c.name }))
  } catch { /* ignore */ }
})

async function doSearch() {
  if (!form.query.trim()) return
  searching.value = true
  searched.value = false
  try {
    const data = await searchDocuments({
      query: form.query,
      top_k: form.top_k,
      course_name: form.course_name || undefined,
      content_type: form.content_type || undefined,
    })
    results.value = data.results
    lastQuery.value = form.query
    searched.value = true
  } catch {
    // handled by interceptor
  } finally {
    searching.value = false
  }
}
</script>

<style scoped>
.result-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}
.result-index {
  margin-left: auto;
  color: #999;
  font-size: 13px;
}
.result-content {
  background: #f9fafb;
  padding: 12px;
  border-radius: 6px;
  line-height: 1.7;
  font-size: 14px;
}
.result-content :deep(mark) {
  background: #fff3cd;
  padding: 1px 2px;
  border-radius: 2px;
}
.result-meta {
  margin-top: 8px;
  color: #909399;
  font-size: 13px;
}
.results-info {
  color: #606266;
  font-size: 14px;
}
</style>
```

- [ ] **Step 3: Commit**

```bash
cd /home/xilin/project/RAG_self
git add frontend/src/components/SearchHighlight.vue frontend/src/views/SearchView.vue
git commit -m "feat: add SearchView with keyword highlighting and filters"
```

---

### Task 10: CourseListView + CourseDetailView — 课程管理页面

**Files:**
- Create: `frontend/src/views/CourseListView.vue`
- Create: `frontend/src/views/CourseDetailView.vue`

- [ ] **Step 1: 创建 CourseListView**

写入 `frontend/src/views/CourseListView.vue`:

```vue
<template>
  <div class="course-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>课程管理</span>
          <el-button type="primary" size="small" @click="openCreate">新增课程</el-button>
        </div>
      </template>

      <el-form :inline="true">
        <el-form-item label="搜索">
          <el-input v-model="keyword" placeholder="课程名..." clearable @keyup.enter="fetchCourses" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchCourses">搜索</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="courses" stripe @row-click="goDetail">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="课程名" min-width="180" />
        <el-table-column prop="target_audience" label="受众" min-width="120" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
      </el-table>

      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="100"
        layout="prev, pager, next"
        style="margin-top: 16px; justify-content: center"
        @current-change="fetchCourses"
      />
    </el-card>

    <!-- Create dialog -->
    <el-dialog v-model="dialogVisible" title="新增课程" width="520px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="课程名" required>
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="先修要求">
          <el-input v-model="form.prerequisites" />
        </el-form-item>
        <el-form-item label="目标受众">
          <el-input v-model="form.target_audience" />
        </el-form-item>
        <el-form-item label="学习目标">
          <el-input v-model="form.learning_goals" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="doCreate">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { listCourses, createCourse } from '@/api/courses'
import type { CourseListItem } from '@/types'

const router = useRouter()
const courses = ref<CourseListItem[]>([])
const keyword = ref('')
const page = ref(1)
const pageSize = 20

const dialogVisible = ref(false)
const creating = ref(false)
const form = ref({
  name: '',
  description: '',
  prerequisites: '',
  target_audience: '',
  learning_goals: '',
})

async function fetchCourses() {
  try {
    courses.value = await listCourses({ keyword: keyword.value || undefined, offset: (page.value - 1) * pageSize, limit: pageSize })
  } catch { /* handled */ }
}

function goDetail(row: CourseListItem) {
  router.push(`/courses/${row.id}`)
}

function openCreate() {
  form.value = { name: '', description: '', prerequisites: '', target_audience: '', learning_goals: '' }
  dialogVisible.value = true
}

async function doCreate() {
  creating.value = true
  try {
    await createCourse({ ...form.value })
    ElMessage.success('课程已创建')
    dialogVisible.value = false
    fetchCourses()
  } catch { /* handled */ } finally {
    creating.value = false
  }
}

onMounted(fetchCourses)
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
```

- [ ] **Step 2: 创建 CourseDetailView**

写入 `frontend/src/views/CourseDetailView.vue`:

```vue
<template>
  <div class="course-detail">
    <el-button text @click="$router.push('/courses')">&larr; 返回课程列表</el-button>

    <el-card v-if="course" style="margin-top: 12px">
      <template #header>{{ course.name }}</template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="描述">{{ course.description || '-' }}</el-descriptions-item>
        <el-descriptions-item label="目标受众">{{ course.target_audience || '-' }}</el-descriptions-item>
        <el-descriptions-item label="先修要求">{{ course.prerequisites || '-' }}</el-descriptions-item>
        <el-descriptions-item label="学习目标">{{ course.learning_goals || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-row :gutter="16" style="margin-top: 16px">
      <!-- Chapters -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>章节结构</span>
              <el-button size="small" type="primary" @click="openChapterDialog">添加章节</el-button>
            </div>
          </template>
          <el-table :data="course?.chapters || []">
            <el-table-column prop="order" label="顺序" width="80" />
            <el-table-column prop="name" label="章节名" />
          </el-table>
        </el-card>
      </el-col>

      <!-- Projects -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>项目列表</span>
              <el-button size="small" type="primary" @click="openProjectDialog">添加项目</el-button>
            </div>
          </template>
          <el-table :data="course?.projects || []">
            <el-table-column prop="name" label="项目名" />
            <el-table-column prop="description" label="描述" show-overflow-tooltip />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- Add chapter dialog -->
    <el-dialog v-model="chapterDialog" title="添加章节" width="400px">
      <el-form :model="chapterForm" label-width="80px">
        <el-form-item label="章节名">
          <el-input v-model="chapterForm.name" />
        </el-form-item>
        <el-form-item label="顺序">
          <el-input-number v-model="chapterForm.order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="chapterDialog = false">取消</el-button>
        <el-button type="primary" :loading="addingChapter" @click="doAddChapter">确定</el-button>
      </template>
    </el-dialog>

    <!-- Add project dialog -->
    <el-dialog v-model="projectDialog" title="添加项目" width="400px">
      <el-form :model="projectForm" label-width="80px">
        <el-form-item label="项目名">
          <el-input v-model="projectForm.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="projectForm.description" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="projectDialog = false">取消</el-button>
        <el-button type="primary" :loading="addingProject" @click="doAddProject">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getCourse, addChapter, addProject } from '@/api/courses'
import type { Course } from '@/types'

const route = useRoute()
const course = ref<Course | null>(null)

const chapterDialog = ref(false)
const chapterForm = ref({ name: '', order: 0 })
const addingChapter = ref(false)

const projectDialog = ref(false)
const projectForm = ref({ name: '', description: '' })
const addingProject = ref(false)

async function fetchCourse() {
  try {
    course.value = await getCourse(Number(route.params.id))
  } catch { /* handled */ }
}

function openChapterDialog() {
  chapterForm.value = { name: '', order: (course.value?.chapters.length || 0) + 1 }
  chapterDialog.value = true
}

async function doAddChapter() {
  addingChapter.value = true
  try {
    await addChapter(course.value!.id, { ...chapterForm.value })
    ElMessage.success('章节已添加')
    chapterDialog.value = false
    fetchCourse()
  } catch { /* handled */ } finally {
    addingChapter.value = false
  }
}

function openProjectDialog() {
  projectForm.value = { name: '', description: '' }
  projectDialog.value = true
}

async function doAddProject() {
  addingProject.value = true
  try {
    await addProject(course.value!.id, { ...projectForm.value })
    ElMessage.success('项目已添加')
    projectDialog.value = false
    fetchCourse()
  } catch { /* handled */ } finally {
    addingProject.value = false
  }
}

onMounted(fetchCourse)
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
```

- [ ] **Step 3: Commit**

```bash
cd /home/xilin/project/RAG_self
git add frontend/src/views/CourseListView.vue frontend/src/views/CourseDetailView.vue
git commit -m "feat: add course management views (list + detail with chapters/projects)"
```

---

### Task 11: QuestionListView — 题库管理页面

**Files:**
- Create: `frontend/src/views/QuestionListView.vue`

- [ ] **Step 1: 写入 QuestionListView**

写入 `frontend/src/views/QuestionListView.vue`:

```vue
<template>
  <div class="question-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>题库管理</span>
          <el-button type="primary" size="small" @click="openCreate">新增题目</el-button>
        </div>
      </template>

      <el-form :inline="true">
        <el-form-item label="课程">
          <el-input v-model="filters.course_name" placeholder="课程名" clearable />
        </el-form-item>
        <el-form-item label="题型">
          <el-select v-model="filters.question_type" placeholder="全部" clearable style="width: 140px">
            <el-option label="单选题" value="single_choice" />
            <el-option label="多选题" value="multi_choice" />
            <el-option label="判断题" value="true_false" />
            <el-option label="填空题" value="fill_blank" />
            <el-option label="简答题" value="short_answer" />
          </el-select>
        </el-form-item>
        <el-form-item label="题库">
          <el-input v-model="filters.question_bank_name" placeholder="题库名" clearable />
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="filters.keyword" placeholder="搜索内容..." clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchQuestions">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="questions" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="content" label="内容" min-width="240" show-overflow-tooltip />
        <el-table-column prop="question_type" label="题型" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ typeLabel(row.question_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="question_bank_name" label="题库" width="120" />
        <el-table-column prop="course_name" label="课程" width="120" />
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button size="small" @click="openDetail(row.id)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="100"
        layout="prev, pager, next"
        style="margin-top: 16px; justify-content: center"
        @current-change="fetchQuestions"
      />
    </el-card>

    <!-- Detail drawer -->
    <el-drawer v-model="drawerVisible" title="题目详情" size="480px">
      <template v-if="detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="ID">{{ detail.id }}</el-descriptions-item>
          <el-descriptions-item label="题型">
            <el-tag size="small">{{ typeLabel(detail.question_type) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="内容">{{ detail.content }}</el-descriptions-item>
          <el-descriptions-item v-if="detail.options.length" label="选项">
            <el-tag v-for="(opt, i) in detail.options" :key="i" style="margin: 2px">{{ opt }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="答案">{{ detail.answer || '-' }}</el-descriptions-item>
          <el-descriptions-item label="解析">{{ detail.explanation || '-' }}</el-descriptions-item>
          <el-descriptions-item label="题库">{{ detail.question_bank_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="课程">{{ detail.course_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="来源文件">{{ detail.source_file || '-' }}</el-descriptions-item>
        </el-descriptions>
      </template>
    </el-drawer>

    <!-- Create dialog -->
    <el-dialog v-model="createDialog" title="新增题目" width="560px">
      <el-form :model="createForm" label-width="80px">
        <el-form-item label="内容" required>
          <el-input v-model="createForm.content" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="题型" required>
          <el-select v-model="createForm.question_type" style="width: 100%">
            <el-option label="单选题" value="single_choice" />
            <el-option label="多选题" value="multi_choice" />
            <el-option label="判断题" value="true_false" />
            <el-option label="填空题" value="fill_blank" />
            <el-option label="简答题" value="short_answer" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="hasOptions" label="选项">
          <div v-for="(_, i) in createForm.options" :key="i" style="display: flex; gap: 8px; margin-bottom: 4px">
            <el-input v-model="createForm.options[i]" :placeholder="`选项 ${String.fromCharCode(65 + i)}`" />
            <el-button type="danger" :icon="'Delete'" circle size="small" @click="createForm.options.splice(i, 1)" />
          </div>
          <el-button size="small" @click="createForm.options.push('')">+ 添加选项</el-button>
        </el-form-item>
        <el-form-item label="答案">
          <el-input v-model="createForm.answer" />
        </el-form-item>
        <el-form-item label="解析">
          <el-input v-model="createForm.explanation" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="题库名">
          <el-input v-model="createForm.question_bank_name" />
        </el-form-item>
        <el-form-item label="课程名">
          <el-input v-model="createForm.course_name" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialog = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="doCreate">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { listQuestions, getQuestion, createQuestion } from '@/api/questions'
import type { QuestionListItem, Question } from '@/types'

const questions = ref<QuestionListItem[]>([])
const page = ref(1)
const pageSize = 20
const filters = reactive({
  keyword: '',
  course_name: '',
  question_type: '',
  question_bank_name: '',
})

const drawerVisible = ref(false)
const detail = ref<Question | null>(null)

const createDialog = ref(false)
const creating = ref(false)
const createForm = reactive({
  content: '',
  question_type: 'single_choice',
  options: [] as string[],
  answer: '',
  explanation: '',
  question_bank_name: '',
  course_name: '',
})

const hasOptions = computed(() =>
  ['single_choice', 'multi_choice'].includes(createForm.question_type),
)

function typeLabel(type: string) {
  const map: Record<string, string> = {
    single_choice: '单选题', multi_choice: '多选题', true_false: '判断题',
    fill_blank: '填空题', short_answer: '简答题',
  }
  return map[type] || type
}

async function fetchQuestions() {
  try {
    questions.value = await listQuestions({
      keyword: filters.keyword || undefined,
      course_name: filters.course_name || undefined,
      question_type: filters.question_type || undefined,
      question_bank_name: filters.question_bank_name || undefined,
      offset: (page.value - 1) * pageSize,
      limit: pageSize,
    })
  } catch { /* handled */ }
}

async function openDetail(id: number) {
  try {
    detail.value = await getQuestion(id)
    drawerVisible.value = true
  } catch { /* handled */ }
}

function openCreate() {
  createForm.content = ''
  createForm.question_type = 'single_choice'
  createForm.options = []
  createForm.answer = ''
  createForm.explanation = ''
  createForm.question_bank_name = ''
  createForm.course_name = ''
  createDialog.value = true
}

async function doCreate() {
  creating.value = true
  try {
    await createQuestion({
      content: createForm.content,
      question_type: createForm.question_type,
      options: createForm.options.filter(Boolean),
      answer: createForm.answer,
      explanation: createForm.explanation,
      question_bank_name: createForm.question_bank_name,
      course_name: createForm.course_name,
    })
    ElMessage.success('题目已创建')
    createDialog.value = false
    fetchQuestions()
  } catch { /* handled */ } finally {
    creating.value = false
  }
}

onMounted(fetchQuestions)
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
```

- [ ] **Step 2: Commit**

```bash
cd /home/xilin/project/RAG_self
git add frontend/src/views/QuestionListView.vue
git commit -m "feat: add QuestionListView with filters, detail drawer, and create dialog"
```

---

### Task 12: QAView + StreamOutput + CitationPanel — 流式问答页面

**Files:**
- Create: `frontend/src/components/StreamOutput.vue`
- Create: `frontend/src/components/CitationPanel.vue`
- Create: `frontend/src/views/QAView.vue`

- [ ] **Step 1: 创建 StreamOutput 组件**

写入 `frontend/src/components/StreamOutput.vue`:

```vue
<template>
  <div class="stream-output" ref="containerRef">
    <div class="stream-content">{{ text }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'

const props = defineProps<{ text: string }>()
const containerRef = ref<HTMLElement>()

watch(() => props.text, async () => {
  await nextTick()
  if (containerRef.value) {
    containerRef.value.scrollTop = containerRef.value.scrollHeight
  }
})
</script>

<style scoped>
.stream-output {
  min-height: 200px;
  max-height: 400px;
  overflow-y: auto;
  background: #f9fafb;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 14px;
}
.stream-content {
  white-space: pre-wrap;
  line-height: 1.7;
  font-size: 15px;
}
</style>
```

- [ ] **Step 2: 创建 CitationPanel 组件**

写入 `frontend/src/components/CitationPanel.vue`:

```vue
<template>
  <div class="citation-panel">
    <el-collapse v-if="citations.length > 0">
      <el-collapse-item v-for="(item, idx) in citations" :key="idx" :title="`引用 #${item.index}`">
        <div class="citation-content">{{ item.content }}</div>
        <div class="citation-meta">
          <el-tag v-if="item.course_name" size="small">课程: {{ item.course_name }}</el-tag>
          <el-tag v-if="item.chapter_name" size="small" type="info">章节: {{ item.chapter_name }}</el-tag>
          <el-tag v-if="item.source_file" size="small" type="warning">来源: {{ item.source_file }}</el-tag>
        </div>
      </el-collapse-item>
    </el-collapse>
    <el-empty v-else description="暂无引用" :image-size="60" />
  </div>
</template>

<script setup lang="ts">
import type { Citation } from '@/types'

defineProps<{ citations: Citation[] }>()
</script>

<style scoped>
.citation-content {
  background: #f9fafb;
  padding: 10px;
  border-radius: 6px;
  margin-bottom: 8px;
  line-height: 1.6;
  font-size: 14px;
}
.citation-meta {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
</style>
```

- [ ] **Step 3: 创建 QAView**

写入 `frontend/src/views/QAView.vue`:

```vue
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
import { getBaseUrl } from '@/api/client'

const query = ref('')
const answer = ref('')
const citations = ref<Citation[]>([])
const streaming = ref(false)
const streamState = ref<'idle' | 'streaming' | 'done' | 'error'>('idle')
const conversationId = ref<number | undefined>()
const conversations = ref<Conversation[]>([])

let abortController: AbortController | null = null

const streamStateType = {
  idle: 'info', streaming: 'warning', done: 'success', error: 'danger',
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
```

- [ ] **Step 4: Commit**

```bash
cd /home/xilin/project/RAG_self
git add frontend/src/components/StreamOutput.vue frontend/src/components/CitationPanel.vue frontend/src/views/QAView.vue
git commit -m "feat: add QAView with SSE streaming, citation panel, and conversation selector"
```

---

### Task 13: ConversationListView — 对话管理页面

**Files:**
- Create: `frontend/src/views/ConversationListView.vue`

- [ ] **Step 1: 写入 ConversationListView**

写入 `frontend/src/views/ConversationListView.vue`:

```vue
<template>
  <div class="conversation-list">
    <el-card>
      <template #header>对话管理</template>

      <el-table :data="conversations" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button size="small" @click="viewConversation(row.id)">查看</el-button>
            <el-popconfirm title="确定删除此对话?" @confirm="doDelete(row.id)">
              <template #reference>
                <el-button size="small" type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="100"
        layout="prev, pager, next"
        style="margin-top: 16px; justify-content: center"
        @current-change="fetchConversations"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { listConversations, deleteConversation } from '@/api/conversations'
import type { Conversation } from '@/types'

const router = useRouter()
const conversations = ref<Conversation[]>([])
const page = ref(1)
const pageSize = 20

async function fetchConversations() {
  try {
    conversations.value = await listConversations({
      offset: (page.value - 1) * pageSize,
      limit: pageSize,
    })
  } catch { /* handled */ }
}

function viewConversation(id: number) {
  router.push({ path: '/qa', query: { conversation_id: String(id) } })
}

async function doDelete(id: number) {
  try {
    await deleteConversation(id)
    ElMessage.success('对话已删除')
    fetchConversations()
  } catch { /* handled */ }
}

onMounted(fetchConversations)
</script>
```

- [ ] **Step 2: Commit**

```bash
cd /home/xilin/project/RAG_self
git add frontend/src/views/ConversationListView.vue
git commit -m "feat: add ConversationListView with delete and navigation to QA"
```

---

### Task 14: 构建验证与集成

**Files:**
- Create: `frontend/src/components/TaskProgress.vue`

- [ ] **Step 1: 创建 TaskProgress 组件**

写入 `frontend/src/components/TaskProgress.vue`:

```vue
<template>
  <el-progress
    :percentage="percent"
    :status="status"
    :stroke-width="16"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  completedChunks: number
  totalChunks: number
  taskStatus: string
}>()

const percent = computed(() => {
  if (props.totalChunks === 0) return 0
  return Math.round((props.completedChunks / props.totalChunks) * 100)
})

const status = computed(() => {
  if (props.taskStatus === 'failed') return 'exception'
  if (props.taskStatus === 'completed') return 'success'
  return undefined
})
</script>
```

- [ ] **Step 2: 运行 TypeScript 类型检查**

```bash
cd /home/xilin/project/RAG_self/frontend && pnpm vue-tsc -b --noEmit 2>&1 || true
```

Expected: 无类型错误。

- [ ] **Step 3: 构建生产版本**

```bash
cd /home/xilin/project/RAG_self/frontend && pnpm build
```

Expected: 构建成功，`app/web/static/` 下生成产物。

- [ ] **Step 4: 启动后端验证 Web 控制台可访问**

```bash
cd /home/xilin/project/RAG_self && timeout 5 python -c "
import uvicorn
uvicorn.run('app.main:app', host='127.0.0.1', port=8000)
" 2>&1 || true
```

验证 `app/web/static/` 中的构建产物存在且可被 FastAPI 的 StaticFiles 挂载。

- [ ] **Step 5: 验证 SPA 回退路由**

确认 `main.py` 中 `/web/{rest:path}` catch-all 路由可正确返回 `index.html`：

```bash
cd /home/xilin/project/RAG_self && python -c "
from app.main import app
from fastapi.testclient import TestClient
client = TestClient(app)
r = client.get('/web/courses')
assert r.status_code == 200
assert 'html' in r.headers.get('content-type', '')
print('SPA fallback OK')
"
```

- [ ] **Step 6: Commit**

```bash
cd /home/xilin/project/RAG_self
git add frontend/src/components/TaskProgress.vue
git add app/web/static/
git commit -m "feat: add TaskProgress component and verify full build"
```

---

### Task 15: 运行后端测试验证无回归

- [ ] **Step 1: 运行全量后端测试**

```bash
cd /home/xilin/project/RAG_self && python -m pytest tests/ -v
```

Expected: 所有已有测试通过。

- [ ] **Step 2: 检查构建产物完整性**

```bash
ls -la /home/xilin/project/RAG_self/app/web/static/
```

Expected: 包含 `index.html` 和 `assets/` 目录（含 JS/CSS 文件）。

- [ ] **Step 3: 如测试失败，修复后重新运行；通过则最终 Commit**

```bash
cd /home/xilin/project/RAG_self
git add -A
git commit -m "chore: final integration verification"
```
