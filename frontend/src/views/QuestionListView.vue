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
