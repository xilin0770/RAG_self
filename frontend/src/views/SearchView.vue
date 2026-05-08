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
