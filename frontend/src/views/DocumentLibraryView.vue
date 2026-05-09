<template>
  <div class="document-library-view">
    <div class="page-header">
      <div class="header-left">
        <h2>文档库</h2>
        <span class="doc-count" v-if="!loading">共 {{ total }} 份文档</span>
      </div>
      <el-button @click="refresh" :loading="loading">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <el-card class="filter-card" shadow="never">
      <el-row :gutter="16" align="middle">
        <el-col :span="6">
          <el-select
            v-model="filters.content_type"
            placeholder="文档类型"
            clearable
            style="width: 100%"
            @change="onFilterChange"
          >
            <el-option
              v-for="opt in typeOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-input
            v-model="filters.course_name"
            placeholder="课程名称"
            clearable
            @clear="onFilterChange"
            @keyup.enter="onFilterChange"
          />
        </el-col>
        <el-col :span="6">
          <el-input
            v-model="filters.search"
            placeholder="搜索文档名"
            clearable
            @clear="onFilterChange"
            @keyup.enter="onFilterChange"
          />
        </el-col>
        <el-col :span="6">
          <el-button type="primary" @click="onFilterChange" :loading="loading">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="table-card" shadow="never">
      <el-table
        :data="documents"
        stripe
        v-loading="loading"
        empty-text="暂无导入的文档"
        highlight-current-row
        style="width: 100%"
      >
        <el-table-column label="#" width="60" align="center">
          <template #default="{ $index }">
            {{ (page - 1) * pageSize + $index + 1 }}
          </template>
        </el-table-column>

        <el-table-column label="文档名称" min-width="240">
          <template #default="{ row }">
            <div class="doc-name-cell">
              <el-icon class="doc-icon" :size="18">
                <Document />
              </el-icon>
              <div class="doc-name-info">
                <span class="doc-filename">{{ row.source_file || '未知文件' }}</span>
                <span class="doc-chapters" v-if="row.chapter_name">{{ row.chapter_name }}</span>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="类型" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="typeTagType(row.content_type)" size="small" effect="light">
              {{ contentTypeLabel(row.content_type) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="课程" width="140">
          <template #default="{ row }">
            <span v-if="row.course_name" class="meta-text">{{ row.course_name }}</span>
            <span v-else class="meta-empty">—</span>
          </template>
        </el-table-column>

        <el-table-column label="项目" width="140">
          <template #default="{ row }">
            <span v-if="row.project_name" class="meta-text">{{ row.project_name }}</span>
            <span v-else class="meta-empty">—</span>
          </template>
        </el-table-column>

        <el-table-column label="片段数" width="90" align="center">
          <template #default="{ row }">
            <el-tag round size="small">{{ row.fragment_count }} 段</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="内容预览" min-width="260">
          <template #default="{ row }">
            <div class="preview-cell">
              {{ row.preview || '(空)' }}
              <span v-if="row.preview?.length >= 200">...</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="120" fixed="right" align="center">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button
                type="primary"
                size="small"
                link
                @click="handlePreview(row)"
              >
                查看
              </el-button>
              <el-popconfirm
                :title="`确定删除「${row.source_file}」及其全部 ${row.fragment_count} 个片段吗？`"
                width="300"
                confirm-button-text="确认删除"
                cancel-button-text="取消"
                @confirm="handleDeleteSource(row)"
              >
                <template #reference>
                  <el-button type="danger" size="small" link>删除</el-button>
                </template>
              </el-popconfirm>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          v-model:page-size="pageSize"
          v-model:current-page="page"
          :page-sizes="[10, 20, 50, 100]"
          @size-change="onPageSizeChange"
          @current-change="onPageChange"
        />
      </div>
    </el-card>

    <el-dialog v-model="previewVisible" title="文档预览" width="700px" destroy-on-close>
      <div class="preview-dialog-body">
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="文件名">{{ previewDoc?.source_file }}</el-descriptions-item>
          <el-descriptions-item label="类型">
            <el-tag :type="typeTagType(previewDoc?.content_type || '')" size="small">
              {{ contentTypeLabel(previewDoc?.content_type || '') }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="课程">{{ previewDoc?.course_name || '—' }}</el-descriptions-item>
          <el-descriptions-item label="项目">{{ previewDoc?.project_name || '—' }}</el-descriptions-item>
          <el-descriptions-item label="章节">{{ previewDoc?.chapter_name || '—' }}</el-descriptions-item>
          <el-descriptions-item label="片段数">{{ previewDoc?.fragment_count }} 段</el-descriptions-item>
        </el-descriptions>
        <div class="preview-content">
          <div class="preview-content-label">内容摘要</div>
          <div class="preview-content-text">{{ previewDoc?.preview || '(无内容)' }}</div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Document } from '@element-plus/icons-vue'
import { listDocumentSources, deleteDocumentSource } from '@/api/documents'
import type { DocumentSource } from '@/types'

const documents = ref<DocumentSource[]>([])
const loading = ref(false)
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

const previewVisible = ref(false)
const previewDoc = ref<DocumentSource | null>(null)

const filters = reactive({
  content_type: '',
  course_name: '',
  search: '',
})

const typeOptions = [
  { label: '知识文档', value: 'doc_fragment' },
  { label: '课程介绍', value: 'course_intro' },
  { label: '题目', value: 'question' },
  { label: '项目资料', value: 'project_material' },
]

function contentTypeLabel(type: string) {
  const map: Record<string, string> = {
    doc_fragment: '知识文档',
    course_intro: '课程介绍',
    question: '题目',
    project_material: '项目资料',
  }
  return map[type] || type
}

function typeTagType(type: string): 'success' | 'warning' | 'info' | 'danger' | '' {
  const map: Record<string, string> = {
    doc_fragment: 'success',
    course_intro: 'warning',
    question: 'danger',
    project_material: 'info',
  }
  return (map[type] || 'info') as 'success' | 'warning' | 'info' | 'danger' | ''
}

async function fetchDocuments() {
  loading.value = true
  try {
    const data = await listDocumentSources({
      page: page.value,
      page_size: pageSize.value,
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

function onFilterChange() {
  page.value = 1
  fetchDocuments()
}

function onPageChange(p: number) {
  page.value = p
  fetchDocuments()
}

function onPageSizeChange() {
  page.value = 1
  fetchDocuments()
}

function handlePreview(row: DocumentSource) {
  previewDoc.value = row
  previewVisible.value = true
}

async function handleDeleteSource(row: DocumentSource) {
  try {
    const result = await deleteDocumentSource(
      row.source_file,
      row.course_name || '',
      row.project_name || '',
    )
    ElMessage.success(`已删除「${row.source_file}」及 ${result.fragments_removed} 个片段`)
    await fetchDocuments()
  } catch {
    // handled by interceptor
  }
}

function refresh() {
  fetchDocuments()
}

onMounted(fetchDocuments)
</script>

<style scoped>
.document-library-view {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.header-left h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.doc-count {
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.filter-card {
  margin-bottom: 16px;
}

.filter-card :deep(.el-card__body) {
  padding: 16px 20px;
}

.table-card {
  overflow: visible;
}

.table-card :deep(.el-card__body) {
  padding: 0 20px 20px;
}

.doc-name-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.doc-icon {
  color: var(--el-color-primary);
  flex-shrink: 0;
}

.doc-name-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow: hidden;
}

.doc-filename {
  font-weight: 500;
  color: var(--el-text-color-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.doc-chapters {
  font-size: 12px;
  color: var(--el-text-color-placeholder);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.meta-text {
  color: var(--el-text-color-regular);
}

.meta-empty {
  color: var(--el-text-color-placeholder);
}

.preview-cell {
  color: var(--el-text-color-secondary);
  font-size: 13px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.5;
}

.action-buttons {
  display: flex;
  gap: 4px;
  justify-content: center;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.preview-dialog-body {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.preview-content-label {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
  color: var(--el-text-color-primary);
}

.preview-content-text {
  background: var(--el-fill-color-light);
  border-radius: 6px;
  padding: 16px;
  font-size: 14px;
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-word;
  color: var(--el-text-color-regular);
  max-height: 400px;
  overflow-y: auto;
}
</style>
