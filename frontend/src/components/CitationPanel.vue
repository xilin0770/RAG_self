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
