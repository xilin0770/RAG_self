# 知识问答对话历史展示 — 设计文档

## 目标

在 Vue 前端知识问答页面中，支持加载并展示完整对话历史（问题 + AI 回答），
从对话管理页面选择会话时展示全部消息，并允许继续提问。

## 核心决策

- **布局**：聊天式消息气泡（用户右蓝，AI 左灰）
- **引用**：右侧独立引用面板（320px），随选中消息切换
- **操作**：仅查看 + 继续提问，不涉及消息编辑/删除
- **重组方式**：改造现有 QAView，不新建页面

## 数据流

```
对话管理点击"查看"
  → 路由 /qa?conversation_id=42
    → QAView 读取 query 参数
      → GET /conversations/42 → messages[] + citations[]
        → 渲染聊天气泡
          → 底部输入框提问
            → POST /qa/stream {query, conversation_id}
              → SSE 逐字推送到当前气泡
                → [CITATIONS] 送右侧面板
                  → 完成后 citations 写入 DB
```

## 涉及改动的文件

| 层 | 文件 | 改动 |
|---|---|---|
| DB | `app/models/conversation.py` | Message 增加 `citations` 列（JSON） |
| 后端 | `app/services/qa_service.py` | `add_message` 支持 citations 参数 |
| 后端 | `app/services/conversation_service.py` | `add_message` 签名增加 citations |
| 后端 | `app/api/conversations.py` | GET 消息时返回 citations |
| 前端 | `frontend/src/types/index.ts` | Message 类型增加 citations |
| 前端 | `frontend/src/views/QAView.vue` | 核心重构：聊天布局 + 历史加载 + 引用面板 |

## UI 结构

```
QAView
├── 顶部工具栏
│   ├── 对话选择器下拉框
│   └── 新建对话按钮
│
├── 中间区域（flex 横向）
│   ├── 左侧：聊天区（flex-grow）
│   │   ├── 消息列表（overflow-y:auto, scrollable）
│   │   │   ├── 用户消息气泡（蓝色右对齐）
│   │   │   │   └── 时间戳 + 文本
│   │   │   └── AI 消息气泡（灰色左对齐）
│   │   │       ├── 时间戳 + 文本
│   │   │       └── 流式输出中：光标闪烁
│   │   └── 输入区
│   │       ├── textarea
│   │       ├── 发送按钮
│   │       └── 停止按钮
│   │
│   └── 右侧：引用面板（width: 320px）
│       ├── "引用来源" 标题
│       ├── 当前选中消息的引用列表
│       └── 流式输出时实时更新
│
└── 空状态提示（无对话时）
```

## 关键交互

1. 加载历史：watch conversationId → GET /conversations/{id} → 填充 messages
2. 新问题：用户输入 → messages 末尾追加临时 AI 消息 → SSE 流式更新该消息 → citations 写入右侧面板
3. 切换对话：下拉框选择 → 清空当前 → 重新加载历史
4. URL 同步：route query 有 conversation_id 时，优先使用它初始化 conversationId
5. 点击消息气泡：切换右侧引用面板内容到该消息的 citations

## 状态变量

```ts
const messages = ref<Message[]>([])           // 历史消息列表
const selectedCitations = ref<Citation[]>([]) // 右侧引用面板
const streamingContent = ref('')              // 流式输出临时内容
const conversationId = ref<number | undefined>()
const conversationTitle = ref('')
```

## 后端改动细节

### Message 模型
```python
citations = Column(JSON, nullable=True)
# [{index, content, course_name, chapter_name, source_file}]
```

### add_message 签名
```python
def add_message(db, conversation_id, role, content, citations=None)
```

### API 响应
```python
"messages": [
    {"id": m.id, "role": m.role, "content": m.content,
     "created_at": m.created_at.isoformat() if m.created_at else None,
     "citations": m.citations or []}
    for m in conv.messages
]
```
