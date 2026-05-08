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
