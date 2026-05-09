// ---- Import ----
export interface ImportTask {
  task_id: number
  file_name: string
  content_type: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  total_chunks: number
  completed_chunks: number
  questions_extracted?: number
  courses_extracted?: number
  error_message?: string
  created_at: string
  updated_at: string
}

export interface ImportSubmitResult {
  task_id: number
  status: string
  file_name: string
}

export interface ImportMetadata {
  content_type: string
  course_name: string
  project_name: string
  chapter_name: string
  source_path: string
}

// ---- Course ----
export interface Course {
  id: number
  name: string
  description: string
  prerequisites: string
  target_audience: string
  learning_goals: string
  chapters: Chapter[]
  projects: Project[]
}

export interface CourseListItem {
  id: number
  name: string
  description: string
  target_audience: string
}

export interface Chapter {
  id: number
  name: string
  order: number
}

export interface Project {
  id: number
  name: string
  description: string
}

// ---- Question ----
export interface Question {
  id: number
  content: string
  question_type: 'single_choice' | 'multi_choice' | 'true_false' | 'fill_blank' | 'short_answer'
  options: string[]
  answer: string
  explanation: string
  question_bank_name: string
  question_code: string
  course_name: string
  source_file: string
}

export interface QuestionListItem {
  id: number
  content: string
  question_type: string
  question_bank_name: string
  question_code: string
  course_name: string
}

// ---- Search ----
export interface SearchResult {
  chunk_id: string
  content: string
  score: number
  course_name: string
  project_name: string
  chapter_name: string
  content_type: string
  source_file: string
  source_path: string
}

export interface SearchResponse {
  query: string
  total: number
  results: SearchResult[]
}

export interface DocumentFragment {
  id: number
  content: string
  content_type: string
  course_name: string
  project_name: string
  chapter_name: string
  source_file: string
  source_path: string
  chunk_id: string
}

export interface DocumentListResponse {
  total: number
  page: number
  page_size: number
  documents: DocumentFragment[]
}

export interface ImportTaskListResponse {
  total: number
  page: number
  page_size: number
  tasks: ImportTask[]
}

// ---- QA ----
export interface QARequest {
  query: string
  conversation_id?: number
}

export interface Citation {
  index: number
  content: string
  course_name?: string
  chapter_name?: string
  source_file?: string
}

// ---- Conversation ----
export interface Conversation {
  id: number
  title: string
  created_at: string
}

export interface ConversationDetail {
  id: number
  title: string
  messages: Message[]
}

export interface Message {
  id: number
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

// ---- API ----
export interface ApiError {
  detail: string
}
