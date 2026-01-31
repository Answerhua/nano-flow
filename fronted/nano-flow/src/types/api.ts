/**
 * API 相关的 TypeScript 类型定义
 */

// 步骤项
export interface StepItem {
  title: string;
  description: string;
}

// 视觉偏好
export interface VisualPreferences {
  character?: string;
  color_scheme?: string;
  custom_tags?: string[];
}

// 生成请求
export interface GenerateRequest {
  title: string;
  steps: StepItem[];
  visual_preferences?: VisualPreferences;
  seed?: number | null;
}

// 生成响应
export interface GenerateResponse {
  task_id: string;
  status: string;
  message: string;
}

// 图片元数据
export interface ImageMetadata {
  resolution: string;
  seed: number;
  model_version: string;
  cfg_scale: number;
  sampling_steps: number;
}

// 生成结果
export interface GenerationResult {
  image_url: string;
  thumbnail_url: string;
  enhanced_prompt: string;
  metadata: ImageMetadata;
}

// 错误详情
export interface ErrorDetail {
  code: string;
  message: string;
}

// 任务状态
export type TaskStatus = 'pending' | 'processing' | 'completed' | 'failed';

// 任务响应
export interface TaskResponse {
  task_id: string;
  status: TaskStatus;
  progress: number | null;
  message: string;
  result: GenerationResult | null;
  error: ErrorDetail | null;
  estimated_time: number | null;
}
