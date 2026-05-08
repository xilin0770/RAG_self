<template>
  <el-container class="app-layout">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="app-aside">
      <div class="logo" @click="$router.push('/')">
        <span v-if="!isCollapse">教育知识库</span>
        <span v-else>RAG</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/import">
          <el-icon><Upload /></el-icon>
          <span>内容导入</span>
        </el-menu-item>
        <el-menu-item index="/courses">
          <el-icon><Reading /></el-icon>
          <span>课程管理</span>
        </el-menu-item>
        <el-menu-item index="/questions">
          <el-icon><EditPen /></el-icon>
          <span>题库管理</span>
        </el-menu-item>
        <el-menu-item index="/search">
          <el-icon><Search /></el-icon>
          <span>文档检索</span>
        </el-menu-item>
        <el-menu-item index="/qa">
          <el-icon><ChatDotSquare /></el-icon>
          <span>知识问答</span>
        </el-menu-item>
        <el-menu-item index="/conversations">
          <el-icon><List /></el-icon>
          <span>对话管理</span>
        </el-menu-item>
        <el-menu-item index="/history">
          <el-icon><Clock /></el-icon>
          <span>导入历史</span>
        </el-menu-item>
        <el-menu-item index="/documents">
          <el-icon><Document /></el-icon>
          <span>文档库</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="app-header">
        <div class="header-left">
          <el-button
            :icon="isCollapse ? Expand : Fold"
            text
            @click="isCollapse = !isCollapse"
          />
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentTitle">{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-tag :type="apiConnected ? 'success' : 'danger'" size="small">
            {{ apiConnected ? 'API 已连接' : 'API 断开' }}
          </el-tag>
        </div>
      </el-header>

      <el-main>
        <router-view />
      </el-main>

      <el-footer class="app-footer">
        教育知识库 RAG 系统 v0.2.0
      </el-footer>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  Upload, Reading, EditPen, Search, ChatDotSquare, List, Expand, Fold, Clock, Document,
} from '@element-plus/icons-vue'

const route = useRoute()
const isCollapse = ref(false)
const apiConnected = ref(true)

const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/courses')) return '/courses'
  return path || '/import'
})

const currentTitle = computed(() => route.meta.title as string | undefined)
</script>

<style scoped>
.app-layout {
  height: 100vh;
}
.app-aside {
  background-color: #304156;
  overflow-y: auto;
  transition: width 0.3s;
}
.logo {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  padding: 0 16px;
  height: 56px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.app-footer {
  text-align: center;
  color: #999;
  font-size: 13px;
  line-height: 40px;
  border-top: 1px solid #e6e6e6;
}
</style>
