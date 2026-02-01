/**
 * API 服务层 - 处理与后端的所有通信
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// 类型定义
export interface StepItem {
  title: string;
  description: string;
}

export interface VisualPreferences {
  character?: string;
  color_scheme?: string;
  custom_tags?: string[];
}

export interface GenerateRequest {
  title: string;
  steps: StepItem[];
  visual_preferences?: VisualPreferences;
  seed?: number | null;
}

export interface VSScenario {
  title: string;
  description: string;
}

export interface GenerateVSRequest {
  title: string;
  left_scenario: VSScenario;
  right_scenario: VSScenario;
  actions: string[];
  visual_preferences?: VisualPreferences;
  seed?: number | null;
}

export interface GenerateResponse {
  task_id: string;
  status: string;
  message: string;
}

export interface ImageMetadata {
  resolution: string;
  seed: number;
  model_version: string;
  cfg_scale: number;
  sampling_steps: number;
}

export interface GenerationResult {
  image_url: string;
  thumbnail_url: string;
  enhanced_prompt: string;
  metadata: ImageMetadata;
}

export interface ErrorDetail {
  code: string;
  message: string;
}

export type TaskStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface TaskResponse {
  task_id: string;
  status: TaskStatus;
  progress: number | null;
  message: string;
  result: GenerationResult | null;
  error: ErrorDetail | null;
  estimated_time: number | null;
}

export interface GenerateStepsRequest {
  title: string;
}

export interface GenerateStepsResponse {
  steps: StepItem[];
}

/**
 * 创建图像生成任务
 */
export async function createGenerationTask(
  request: GenerateRequest
): Promise<GenerateResponse> {
  const response = await fetch(`${API_BASE_URL}/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '创建任务失败');
  }

  return response.json();
}

/**
 * 查询任务状态
 */
export async function getTaskStatus(taskId: string): Promise<TaskResponse> {
  const response = await fetch(`${API_BASE_URL}/generate/${taskId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '查询任务状态失败');
  }

  return response.json();
}

/**
 * 轮询任务状态直到完成或失败
 * @param taskId 任务ID
 * @param onProgress 进度更新回调
 * @param pollInterval 轮询间隔（毫秒）
 */
export async function pollTaskUntilComplete(
  taskId: string,
  onProgress: (task: TaskResponse) => void,
  pollInterval: number = 2000
): Promise<TaskResponse> {
  return new Promise((resolve, reject) => {
    const poll = async () => {
      try {
        const task = await getTaskStatus(taskId);
        onProgress(task);

        if (task.status === 'completed') {
          resolve(task);
        } else if (task.status === 'failed') {
          reject(new Error(task.error?.message || '任务失败'));
        } else {
          // 继续轮询
          setTimeout(poll, pollInterval);
        }
      } catch (error) {
        reject(error);
      }
    };

    poll();
  });
}

/**
 * 根据标题自动生成步骤列表
 */
export async function generateSteps(
  title: string
): Promise<GenerateStepsResponse> {
  const response = await fetch(`${API_BASE_URL}/generate/generate-steps`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ title }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '生成步骤失败');
  }

  return response.json();
}

/**
 * 创建VS模式图像生成任务
 */
export async function createVSGenerationTask(
  request: GenerateVSRequest
): Promise<GenerateResponse> {
  const response = await fetch(`${API_BASE_URL}/generate-vs`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '创建VS任务失败');
  }

  return response.json();
}
