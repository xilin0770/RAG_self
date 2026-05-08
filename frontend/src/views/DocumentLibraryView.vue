<template>
  <div class="document-library-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>文档库</span>
          <el-button @click="refresh">刷新</el-button>
        </div>
      </template>

      <el-row :gutter="12" style="margin-bottom: 12px">
        <el-col :span="6">
          <el-select v-model="filters.content_type" placeholder="类型筛选" clearable @change="refresh">
            <el-option label="知识文档" value="doc_fragment" />
            <el-option label="课程" value="course_intro" />
            <el-option label="题目" value="question" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-input v-model="filters.course_name" placeholder="课程名" clearable @clear="refresh" @keyup.enter="refresh" />
        </el-col>
        <el-col :span="6">
          <el-input v-model="filters.search" placeholder="搜索内容" clearable @clear="refresh" @keyup.enter="refresh" />
        </el-col>
      </el-row>

      <el-table :data="documents" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column label="类型" width="100">
          <template #default="{ row }">{{ contentTypeLabel(row.content_type) }}</template>
        </el-table-column>
        <el-table-column prop="source_file" label="文档名称" min-width="200" />
        <el-table-column prop="course_name" label="课程" width="120" />
        <el-table-column prop="project_name" label="项目" width="120" />
        <el-table-column label="内容预览" min-width="200">
          <template #default="{ row }">{{ row.content?.substring(0, 100) }}{{ row.content?.length > 100 ? '...' : '' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-popconfirm title="删除该文档？同时会移除向量嵌入。" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button type="danger" size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
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
import { ElMessage } from 'element-plus'
import { listDocuments, deleteDocument } from '@/api/documents'
import type { DocumentFragment } from '@/types'

const documents = ref<DocumentFragment[]>([])
const loading = ref(false)
const total = ref(0)
const page = ref(1)
const pageSize = 20

const filters = reactive({
  content_type: '',
  course_name: '',
  search: '',
})

async function refresh() {
  loading.value = true
  try {
    const data = await listDocuments({
      page: page.value,
      page_size: pageSize,
      content_type: filters.content_type || undefined,
      course_name: filters.course_name || undefined,
      search: filters.search || undefined,
    })
    documents.value = data.documents
    total.value = data.total
  } catch {
    // handled by interceptor
  } finally {
    loading.value = false
  }
}

async function handleDelete(id: number) {
  try {
    await deleteDocument(id)
    ElMessage.success('文档已删除')
    await refresh()
  } catch {
    // handled by interceptor
  }
}

function contentTypeLabel(type: string) {
  const map: Record<string, string> = {
    doc_fragment: '知识文档', course_intro: '课程', question: '题目',
  }
  return map[type] || type
}

onMounted(refresh)
</script>
