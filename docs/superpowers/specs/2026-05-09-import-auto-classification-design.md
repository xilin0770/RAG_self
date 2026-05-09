# 导入自动分类提取 - 设计文档

日期: 2026-05-09

## 目标

导入文档后，根据内容自动进行结构化提取：
- 识别到的题目 → 自动写入 `questions` 表，前端题库管理页面直接可见
- 识别到的课程信息 → 自动写入 `courses` 表，前端课程管理页面直接可见

## 方案

并行处理：解析得到全文后，分块嵌入和 LLM 提取同时进行。

```
解析文档 → 全文
              ├─ 分块 → 嵌入 → 向量库 + 文档片段（现有逻辑，不动）
              └─ LLM 结构化提取（新增）
                   ├─ 合并跨 chunk 的 JSON 结果
                   ├─ 题目 → 批量 create_question
                   └─ 课程 → create_course（已存在则跳过）
```

## LLM 提取策略

- 分块提取：长文本分多个 chunk，每个 chunk 独立调用 LLM
- 每个 chunk 返回 JSON，合并去重
- Prompt 为中文，要求输出以下 JSON 结构：

```json
{
  "questions": [
    {
      "content": "...",
      "question_type": "single_choice|multi_choice|true_false|fill_blank|short_answer",
      "options": ["A", "B", "C", "D"],
      "answer": "...",
      "explanation": "..."
    }
  ],
  "courses": [
    {
      "name": "...",
      "description": "...",
      "prerequisites": "...",
      "target_audience": "...",
      "learning_goals": "..."
    }
  ]
}
```

- LLM 自动识别混合内容（一个文档可同时提取题目和课程）
- 提取失败不影响主任务（标记 completed + 提取警告）

## 文件变更

| 文件 | 操作 | 说明 |
|---|---|---|
| `app/services/extractor.py` | 新增 | LLM 结构化提取服务 |
| `app/services/importer.py` | 修改 | 并行启动提取线程 |
| `app/api/importer.py` | 修改 | 状态 API 返回提取统计 |
| `app/models/import_task.py` | 修改 | 新增 questions_extracted, courses_extracted 字段 |
| `frontend/src/types/index.ts` | 修改 | ImportTask 加提取统计字段 |
| `frontend/src/views/ImportView.vue` | 修改 | 表格显示提取结果列 |

## 不涉及

- 前端题库管理页面（QuestionListView.vue）：零改动
- 前端课程管理页面（CourseListView.vue）：零改动
- 现有向量存储逻辑：零改动
