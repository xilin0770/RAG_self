# Vue 3 + Element Plus 前端重构设计

## 概述

将现有的纯 HTML + 原生 JS 单页控制台重构为企业级 Vue 3 + TypeScript + Element Plus 前端应用，完整覆盖后端全部 6 个 API 模块，新增切分配置、多文件上传、文档搜索高亮等功能。

## 技术栈

| 层 | 技术 | 说明 |
|---|------|------|
| 框架 | Vue 3 (Composition API) | `<script setup lang="ts">` |
| 语言 | TypeScript | 严格模式 |
| UI 库 | Element Plus | 企业级组件库 |
| 构建 | Vite 7 | 快速 HMR |
| 路由 | Vue Router 4 | 嵌套路由 |
| 状态 | Pinia | 模块化 store |
| HTTP | Axios | 请求拦截 + 错误处理 |
| 包管理 | pnpm | 快速、节省空间 |

## 项目结构

```
frontend/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── src/
│   ├── main.ts                    # createApp + router + pinia + element-plus
│   ├── App.vue                    # <router-view> 壳
│   ├── router/index.ts            # 路由表
│   ├── api/                       # Axios 请求封装
│   │   ├── client.ts              # 实例 + baseURL + 拦截器
│   │   ├── import.ts
│   │   ├── courses.ts
│   │   ├── search.ts
│   │   ├── questions.ts
│   │   ├── qa.ts
│   │   └── conversations.ts
│   ├── stores/                    # Pinia stores
│   │   ├── import.ts
│   │   └── qa.ts
│   ├── views/                     # 页面组件
│   │   ├── ImportView.vue
│   │   ├── CourseListView.vue
│   │   ├── CourseDetailView.vue
│   │   ├── QuestionListView.vue
│   │   ├── SearchView.vue
│   │   ├── QAView.vue
│   │   └── ConversationListView.vue
│   ├── components/                # 可复用组件
│   │   ├── AppLayout.vue          # 侧边栏 + 顶栏 + <router-view>
│   │   ├── SearchHighlight.vue    # 前端关键词高亮
│   │   ├── CitationPanel.vue      # 引用来源折叠面板
│   │   ├── StreamOutput.vue       # SSE 流式输出渲染
│   │   └── TaskProgress.vue       # 导入任务进度条
│   ├── types/                     # TS 类型定义
│   │   └── index.ts
│   └── utils/                     # 工具函数
│       └── highlight.ts
```

构建输出到 `app/web/static/`，FastAPI 已有对应的 `StaticFiles` 挂载。

## 路由设计

| 路径 | 视图 | 说明 |
|------|------|------|
| `/web` | AppLayout + 默认重定向到 /web/import | 入口 |
| `/web/import` | ImportView | 内容导入 |
| `/web/courses` | CourseListView | 课程列表 |
| `/web/courses/:id` | CourseDetailView | 课程详情 + 章节/项目管理 |
| `/web/questions` | QuestionListView | 题库管理 |
| `/web/search` | SearchView | 文档检索 |
| `/web/qa` | QAView | 知识问答 |
| `/web/conversations` | ConversationListView | 对话管理 |

所有页面在 AppLayout 的 `<router-view>` 中渲染。路由 mode 为 `createWebHistory`，FastAPI 侧需在 `/web` 及 `/web/*` 下回退到 `index.html`。

## 布局

Element Plus 经典企业后台布局：

- **左侧**：`el-menu` 导航，支持折叠，6 个菜单项对应 6 个模块
- **顶部**：面包屑导航 + API 连接状态指示器
- **底部**：Footer 显示版本号
- **内容区**：`<router-view>` 渲染各页面

## 模块设计

### 1. 内容导入 (ImportView)

**上传区**：`el-upload` 组件的 drag 模式，`multiple`，accept `.pdf,.md,.docx,.txt`。
**切分配置**：`el-input-number` 调节 `chunk_size`（默认 500，范围 100-2000）和 `chunk_overlap`（默认 50，范围 0-500）。
**元数据**：`el-form` 包含 content_type、course_name、project_name、chapter_name、source_path。
**任务列表**：`el-table` 展示所有导入任务，列：task_id、file_name、status（`el-tag` 着色）、progress（`el-progress`）、时间、操作（查看详情）。支持自动轮询刷新（2 秒间隔）。

后端需配合：`POST /import` 接受 `chunk_size`（Form[int], default=500）、`chunk_overlap`（Form[int], default=50），支持多文件 `List[UploadFile]`。

### 2. 文档检索 (SearchView)

**搜索栏**：`el-input` + `el-button`，下方筛选：课程（`el-select`，从 `/courses` 加载）、内容类型（`el-select`）、Top-K（`el-input-number`，默认 5）。
**结果列表**：`el-card` 列表，每条显示相似度分数（`el-tag`）、课程名、章节名、来源文件、文本片段。命中关键词用 `<mark>` 高亮。
**高亮策略**：纯前端，对返回文本做关键词匹配，用 `<mark>` 标签包裹命中词。

### 3. 课程管理 (CourseListView / CourseDetailView)

**列表页**：`el-table` + 搜索 + 分页 + 新增按钮。点击行进入详情。
**详情页**：课程基本信息展示，章节表格（`el-table` + 排序 + 删除），项目表格。新增章节/项目用 `el-dialog` 内嵌表单。
**新增课程**：`el-dialog` 内嵌 `el-form`，字段：name、description、prerequisites、target_audience、learning_goals。

### 4. 题库管理 (QuestionListView)

**筛选栏**：课程（`el-select`）、题型（`el-select`）、题库名称（`el-input`）、关键词搜索。
**列表**：`el-table` + 分页，列：id、content（截断）、question_type（`el-tag`）、question_bank_name、course_name、操作（详情）。
**题目详情**：`el-drawer` 展示完整内容、题型、选项（列表）、答案、解析。
**新增题目**：`el-dialog` 表单，根据选择的题型动态显示选项输入区域。

### 5. 知识问答 (QAView)

**对话选择**：`el-select` 加载已有对话列表 + 新建按钮。
**问题输入**：`el-input` type=textarea + 发送按钮 + 停止按钮。
**流式输出**：`StreamOutput` 组件，fetch + ReadableStream 消费 SSE，实时追加文本。状态指示器（`el-tag`）显示空闲/流式输出中/已完成/错误。
**引用来源**：`CitationPanel` 组件，`el-collapse` 折叠面板展示每条引用的元数据和内容。

### 6. 对话管理 (ConversationListView)

**列表**：`el-table` + 分页，列：id、title、created_at、操作（查看/删除）。
**查看**：跳转到问答页并选中该对话。
**删除**：`el-popconfirm` 确认后调用 API。

## 后端改动

仅在 `app/api/importer.py` 和 `app/services/importer.py`：

- `POST /import`：新增 `chunk_size: int = Form(default=500)`、`chunk_overlap: int = Form(default=50)`，文件改为 `List[UploadFile]`
- `run_import`：接收 `chunk_size`、`chunk_overlap` 参数，动态构造 `RecursiveCharacterTextSplitter`，替代使用全局 settings 值
- FastAPI `/web` 路由：回退到 `index.html`，支持 Vue Router history 模式

改动量不超过 30 行，不影响现有 API 契约。

## 错误处理

- Axios 响应拦截器统一处理 HTTP 错误，`ElMessage.error` 提示
- SSE 流中断时显示错误状态并提示重试
- 导入任务失败时，状态列显示红色标签并展示 error_message
- 网络异常时在顶栏显示连接状态指示器

## 测试策略

- 组件单元测试：Vitest + @vue/test-utils，覆盖关键交互逻辑
- API mock：MSW 拦截请求，验证各模块的数据流
- E2E 测试（可选）：Playwright，覆盖导入→搜索→问答的完整流程
