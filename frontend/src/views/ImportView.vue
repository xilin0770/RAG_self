<template>
  <div class="import-view">
    <el-card class="upload-card">
      <template #header>内容导入</template>

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

      <el-form :model="metadata" label-width="80px" :inline="true">
        <el-form-item label="内容类型">
          <el-select v-model="metadata.content_type" style="width: 200px">
            <el-option label="知识文档" value="doc_fragment" />
            <el-option label="课程" value="course_intro" />
            <el-option label="题目" value="question" />
          </el-select>
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
        <el-table-column label="提取结果" width="160">
          <template #default="{ row }">
            <template v-if="row.status === 'completed'">
              <span v-if="(row.questions_extracted || 0) + (row.courses_extracted || 0) > 0">
                <span v-if="row.questions_extracted">题目 {{ row.questions_extracted }} 道</span>
                <span v-if="row.questions_extracted && row.courses_extracted">，</span>
                <span v-if="row.courses_extracted">课程 {{ row.courses_extracted }} 门</span>
              </span>
              <span v-else style="color: #909399">-</span>
            </template>
            <template v-else>
              <span style="color: #909399">-</span>
            </template>
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
        content_type: metadata.content_type,
        status: 'pending',
        progress: 0,
        total_chunks: 0,
        completed_chunks: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
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
