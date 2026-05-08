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
