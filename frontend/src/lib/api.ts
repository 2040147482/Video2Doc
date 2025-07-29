import axios, { AxiosResponse } from 'axios'

// API基础配置
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// 创建axios实例
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000, // 30秒超时
    headers: {
        'Content-Type': 'application/json',
    },
})

// 请求拦截器
apiClient.interceptors.request.use(
    (config) => {
        // 可以在这里添加认证token等
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// 响应拦截器
apiClient.interceptors.response.use(
    (response) => {
        return response
    },
    (error) => {
        // 统一错误处理
        const errorMessage = error.response?.data?.message || error.message || '请求失败'
        return Promise.reject(new Error(errorMessage))
    }
)

// API方法
export const api = {
    // 健康检查
    health: async (): Promise<any> => {
        const response = await apiClient.get('/health')
        return response.data
    },

    // 上传视频文件
    uploadFile: async (
        file: File,
        language: string = 'auto',
        outputFormats: string = 'markdown'
    ): Promise<VideoProcessResponse> => {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('language', language)
        formData.append('output_formats', outputFormats)

        const response = await apiClient.post('/api/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
            // 上传进度回调
            onUploadProgress: (progressEvent) => {
                if (progressEvent.total) {
                    const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
                    console.log(`Upload progress: ${progress}%`)
                }
            },
        })
        return response.data
    },

    // 处理视频链接
    uploadUrl: async (request: VideoUploadRequest): Promise<VideoProcessResponse> => {
        const response = await apiClient.post('/api/upload-url', request)
        return response.data
    },

    // 获取任务状态
    getTaskStatus: async (taskId: string): Promise<TaskStatusResponse> => {
        const response = await apiClient.get(`/api/status/${taskId}`)
        return response.data
    },

    // 获取所有任务
    getAllTasks: async (): Promise<TaskStatusResponse[]> => {
        const response = await apiClient.get('/api/tasks')
        return response.data
    },

    // 删除任务
    deleteTask: async (taskId: string): Promise<{ message: string }> => {
        const response = await apiClient.delete(`/api/tasks/${taskId}`)
        return response.data
    },

    // 获取支持的格式
    getSupportedFormats: async (): Promise<SupportedFormatsResponse> => {
        const response = await apiClient.get('/api/supported-formats')
        return response.data
    },

    // === 导出相关API ===

    // 创建导出任务
    createExport: async (request: ExportRequest): Promise<ExportResponse> => {
        const response = await apiClient.post('/api/export', request)
        return response.data
    },

    // 获取导出状态
    getExportStatus: async (exportId: string): Promise<ExportStatus> => {
        const response = await apiClient.get(`/api/export/status/${exportId}`)
        return response.data
    },

    // 取消导出任务
    cancelExport: async (exportId: string): Promise<{ message: string }> => {
        const response = await apiClient.delete(`/api/export/${exportId}`)
        return response.data
    },

    // 下载导出文件
    downloadExportFile: async (exportId: string, filename: string): Promise<Blob> => {
        const response = await apiClient.get(`/api/export/download/${exportId}/${filename}`, {
            responseType: 'blob'
        })
        return response.data
    },

    // 获取支持的导出格式
    getExportFormats: async (): Promise<string[]> => {
        const response = await apiClient.get('/api/export/formats')
        return response.data
    },

    // 获取可用的导出模板
    getExportTemplates: async (): Promise<string[]> => {
        const response = await apiClient.get('/api/export/templates')
        return response.data
    },
}

// 类型定义
export interface VideoUploadRequest {
    video_url?: string
    video_name?: string
    language?: string
    output_formats?: string[]
}

export interface VideoProcessResponse {
    task_id: string
    status: string
    message: string
    estimated_time?: number
}

export interface TaskStatusResponse {
    task_id: string
    status: string
    progress: number
    message: string
    created_at: string
    updated_at: string
    result_urls?: string[]
    error_details?: string
}

export interface SupportedFormatsResponse {
    video_formats: string[]
    video_platforms: string[]
    max_file_size: number
    max_file_size_mb: number
}

// === 导出相关类型定义 ===

export interface ExportRequest {
    task_id: string
    formats: string[]
    template: string
    include_images: boolean
    include_timestamps: boolean
    include_metadata: boolean
    custom_filename?: string
}

export interface ExportResponse {
    export_id: string
    status: string
    message: string
    download_urls?: Record<string, string>
    expires_at?: string
}

export interface ExportStatus {
    export_id: string
    status: string
    progress: number
    message: string
    formats_completed: string[]
    download_urls?: Record<string, string>
    error_details?: string
    created_at: string
    completed_at?: string
} 