import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory('/web'),
  routes: [
    {
      path: '/',
      component: () => import('@/components/AppLayout.vue'),
      redirect: '/import',
      children: [
        {
          path: 'import',
          name: 'import',
          component: () => import('@/views/ImportView.vue'),
          meta: { title: '内容导入' },
        },
        {
          path: 'courses',
          name: 'courses',
          component: () => import('@/views/CourseListView.vue'),
          meta: { title: '课程管理' },
        },
        {
          path: 'courses/:id',
          name: 'course-detail',
          component: () => import('@/views/CourseDetailView.vue'),
          meta: { title: '课程详情' },
        },
        {
          path: 'questions',
          name: 'questions',
          component: () => import('@/views/QuestionListView.vue'),
          meta: { title: '题库管理' },
        },
        {
          path: 'search',
          name: 'search',
          component: () => import('@/views/SearchView.vue'),
          meta: { title: '文档检索' },
        },
        {
          path: 'qa',
          name: 'qa',
          component: () => import('@/views/QAView.vue'),
          meta: { title: '知识问答' },
        },
        {
          path: 'conversations',
          name: 'conversations',
          component: () => import('@/views/ConversationListView.vue'),
          meta: { title: '对话管理' },
        },
        {
          path: 'history',
          name: 'history',
          component: () => import('@/views/ImportHistoryView.vue'),
          meta: { title: '导入历史' },
        },
        {
          path: 'documents',
          name: 'documents',
          component: () => import('@/views/DocumentLibraryView.vue'),
          meta: { title: '文档库' },
        },
      ],
    },
  ],
})

export default router
