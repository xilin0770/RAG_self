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
