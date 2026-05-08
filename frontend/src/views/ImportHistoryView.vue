<template>
  <div class="import-history-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>导入历史</span>
          <el-button @click="refresh">刷新</el-button>
        </div>
      </template>

      <el-row :gutter="12" style="margin-bottom: 12px">
        <el-col :span="6">
          <el-select v-model="filters.status" placeholder="状态筛选" clearable @change="refresh">
            <el-option label="等待中" value="pending" />
            <el-option label="处理中" value="processing" />
            <el-option label="已完成" value="completed" />
            <el-option label="失败" value="failed" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="filters.content_type" placeholder="类型筛选" clearable @change="refresh">
            <el-option label="知识文档" value="doc_fragment" />
            <el-option label="课程" value="course_intro" />
            <el-option label="题目" value="question" />
          </el-select>
        </el-col>
      </el-row>

      <el-table :data="tasks" stripe v-loading="loading">
        <el-table-column prop="task_id" label="任务ID" width="80" />
        <el-table-column prop="file_name" label="文件名" min-width="180" />
        <el-table-column label="内容类型" width="100">
          <template #default="{ row }">{{ contentTypeLabel(row.content_type) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" />
      </el-table>

      <el-pagination
        style="margin-top: 12px; justify-content: flex-end"
        layout="total, prev, pager, next"
        :total="total"
        :page-size="pageSize"
        v-model:current-page="page"
        @current-change="refresh"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { listImportTasks } from '@/api/import'
import type { ImportTask } from '@/types'

const tasks = ref<ImportTask[]>([])
const loading = ref(false)
const total = ref(0)
const page = ref(1)
const pageSize = 20

const filters = reactive({
  status: '',
  content_type: '',
})

async function refresh() {
  loading.value = true
  try {
    const data = await listImportTasks({
      status: filters.status || undefined,
      content_type: filters.content_type || undefined,
      page: page.value,
      page_size: pageSize,
    })
    tasks.value = data.tasks
    total.value = data.total
  } catch {
    // handled by interceptor
  } finally {
    loading.value = false
  }
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

function contentTypeLabel(type: string) {
  const map: Record<string, string> = {
    doc_fragment: '知识文档', course_intro: '课程', question: '题目',
  }
  return map[type] || type
}

onMounted(refresh)
</script>
