'use client'

import React, { useState, useCallback, useEffect } from 'react'
import { useDropzone } from 'react-dropzone'
import {
    CloudArrowUpIcon,
    LinkIcon,
    DocumentTextIcon,
    ExclamationTriangleIcon,
    CheckCircleIcon,
    XMarkIcon,
    ClockIcon
} from '@heroicons/react/24/outline'
import { api, VideoProcessResponse, TaskStatusResponse, SupportedFormatsResponse } from '@/lib/api'

export default function VideoUpload() {
    // 状态管理
    const [uploadMode, setUploadMode] = useState<'file' | 'url'>('file')
    const [videoUrl, setVideoUrl] = useState('')
    const [videoName, setVideoName] = useState('')
    const [language, setLanguage] = useState('auto')
    const [outputFormats, setOutputFormats] = useState(['markdown'])
    const [isUploading, setIsUploading] = useState(false)
    const [uploadProgress, setUploadProgress] = useState<UploadProgress | null>(null)
    const [currentTask, setCurrentTask] = useState<VideoProcessResponse | null>(null)
    const [supportedFormats, setSupportedFormats] = useState<SupportedFormatsResponse | null>(null)
    const [error, setError] = useState<string | null>(null)

    // 获取支持的格式信息
    useEffect(() => {
        const fetchSupportedFormats = async () => {
            try {
                const formats = await api.getSupportedFormats()
                setSupportedFormats(formats)
            } catch (err) {
                console.error('获取支持格式失败:', err)
            }
        }
        fetchSupportedFormats()
    }, [])

    // 文件验证
    const validateFile = (file: File): string | null => {
        if (!supportedFormats) return null

        // 检查文件大小
        if (file.size > supportedFormats.max_file_size) {
            return `文件大小超过限制（最大 ${supportedFormats.max_file_size_mb}MB）`
        }

        // 检查文件格式
        const fileExt = '.' + file.name.split('.').pop()?.toLowerCase()
        if (!supportedFormats.video_formats.includes(fileExt)) {
            return `不支持的文件格式。支持格式：${supportedFormats.video_formats.join(', ')}`
        }

        return null
    }

    // 处理文件上传
    const handleFileUpload = async (files: File[]) => {
        const file = files[0]
        if (!file) return

        // 验证文件
        const validationError = validateFile(file)
        if (validationError) {
            setError(validationError)
            return
        }

        setError(null)
        setIsUploading(true)
        setUploadProgress({
            percent: 0,
            stage: 'uploading',
            message: '开始上传文件...'
        })

        try {
            // 上传文件
            const response = await api.uploadFile(
                file,
                language,
                outputFormats.join(',')
            )

            setCurrentTask(response)
            setUploadProgress({
                percent: 100,
                stage: 'processing',
                message: response.message
            })

            // 开始轮询任务状态
            startTaskPolling(response.task_id)

        } catch (err) {
            console.error('文件上传失败:', err)
            setError(err instanceof Error ? err.message : '文件上传失败')
            setUploadProgress({
                percent: 0,
                stage: 'error',
                message: '上传失败'
            })
        } finally {
            setIsUploading(false)
        }
    }

    // 处理URL上传
    const handleUrlUpload = async () => {
        if (!videoUrl.trim()) {
            setError('请输入视频链接')
            return
        }

        setError(null)
        setIsUploading(true)
        setUploadProgress({
            percent: 0,
            stage: 'processing',
            message: '解析视频链接...'
        })

        try {
            const response = await api.uploadUrl({
                video_url: videoUrl.trim(),
                video_name: videoName.trim() || undefined,
                language,
                output_formats: outputFormats
            })

            setCurrentTask(response)
            setUploadProgress({
                percent: 50,
                stage: 'processing',
                message: response.message
            })

            // 开始轮询任务状态
            startTaskPolling(response.task_id)

        } catch (err) {
            console.error('视频链接处理失败:', err)
            setError(err instanceof Error ? err.message : '视频链接处理失败')
            setUploadProgress({
                percent: 0,
                stage: 'error',
                message: '处理失败'
            })
        } finally {
            setIsUploading(false)
        }
    }

    // 轮询任务状态
    const startTaskPolling = (taskId: string) => {
        const pollInterval = setInterval(async () => {
            try {
                const taskStatus = await api.getTaskStatus(taskId)

                setUploadProgress({
                    percent: taskStatus.progress,
                    stage: taskStatus.status === 'completed' ? 'completed' :
                        taskStatus.status === 'failed' ? 'error' : 'processing',
                    message: taskStatus.message
                })

                // 任务完成或失败时停止轮询
                if (taskStatus.status === 'completed' || taskStatus.status === 'failed') {
                    clearInterval(pollInterval)

                    if (taskStatus.status === 'failed') {
                        setError(taskStatus.error_details || '处理失败')
                    }
                }

            } catch (err) {
                console.error('获取任务状态失败:', err)
                clearInterval(pollInterval)
            }
        }, 2000) // 每2秒查询一次

        // 5分钟后自动停止轮询
        setTimeout(() => {
            clearInterval(pollInterval)
        }, 5 * 60 * 1000)
    }

    // 重置状态
    const resetUpload = () => {
        setCurrentTask(null)
        setUploadProgress(null)
        setError(null)
        setVideoUrl('')
        setVideoName('')
        setIsUploading(false)
    }

    // 配置react-dropzone
    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop: handleFileUpload,
        accept: supportedFormats?.video_formats.reduce((acc, format) => {
            acc[`video/${format.slice(1)}`] = [format]
            return acc
        }, {} as Record<string, string[]>) || {},
        maxFiles: 1,
        disabled: isUploading
    })

    // 进度条颜色
    const getProgressColor = (stage: string) => {
        switch (stage) {
            case 'uploading': return 'bg-blue-500'
            case 'processing': return 'bg-yellow-500'
            case 'completed': return 'bg-green-500'
            case 'error': return 'bg-red-500'
            default: return 'bg-gray-300'
        }
    }

    return (
        <div className="w-full max-w-4xl mx-auto bg-white rounded-xl shadow-lg overflow-hidden">
            {/* 标签切换 */}
            <div className="flex border-b">
                <button
                    onClick={() => setUploadMode('file')}
                    className={`flex-1 py-4 px-6 text-center font-medium transition-colors ${uploadMode === 'file'
                        ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-600'
                        : 'text-gray-600 hover:text-gray-800'
                        }`}
                >
                    <CloudArrowUpIcon className="w-5 h-5 inline-block mr-2" />
                    上传本地视频
                </button>
                <button
                    onClick={() => setUploadMode('url')}
                    className={`flex-1 py-4 px-6 text-center font-medium transition-colors ${uploadMode === 'url'
                        ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-600'
                        : 'text-gray-600 hover:text-gray-800'
                        }`}
                >
                    <LinkIcon className="w-5 h-5 inline-block mr-2" />
                    视频链接处理
                </button>
            </div>

            <div className="p-6">
                {/* 错误提示 */}
                {error && (
                    <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start">
                        <ExclamationTriangleIcon className="w-5 h-5 text-red-500 mr-2 mt-0.5 flex-shrink-0" />
                        <div>
                            <p className="text-red-800 font-medium">处理失败</p>
                            <p className="text-red-600 text-sm mt-1">{error}</p>
                            <button
                                onClick={resetUpload}
                                className="text-red-600 hover:text-red-800 text-sm underline mt-2"
                            >
                                重新开始
                            </button>
                        </div>
                    </div>
                )}

                {/* 进度显示 */}
                {uploadProgress && (
                    <div className="mb-6">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium text-gray-700">
                                {uploadProgress.message}
                            </span>
                            <span className="text-sm text-gray-500">
                                {uploadProgress.percent}%
                            </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                                className={`h-2 rounded-full transition-all duration-300 ${getProgressColor(uploadProgress.stage)}`}
                                style={{ width: `${uploadProgress.percent}%` }}
                            />
                        </div>
                        {uploadProgress.stage === 'completed' && (
                            <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                                <div className="flex items-center">
                                    <CheckCircleIcon className="w-5 h-5 text-green-500 mr-2" />
                                    <span className="text-green-800 font-medium">处理完成！</span>
                                </div>
                                <p className="text-green-600 text-sm mt-1">
                                    您的视频已成功转换为文档格式
                                </p>
                                <button
                                    onClick={resetUpload}
                                    className="mt-3 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
                                >
                                    处理新视频
                                </button>
                            </div>
                        )}
                    </div>
                )}

                {/* 文件上传区域 */}
                {uploadMode === 'file' && !uploadProgress && (
                    <div
                        {...getRootProps()}
                        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${isDragActive
                            ? 'border-blue-400 bg-blue-50'
                            : 'border-gray-300 hover:border-gray-400'
                            } ${isUploading ? 'pointer-events-none opacity-50' : ''}`}
                    >
                        <input {...getInputProps()} />
                        <CloudArrowUpIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-gray-900 mb-2">
                            {isDragActive ? '松开鼠标上传文件' : '拖拽视频文件到这里'}
                        </h3>
                        <p className="text-gray-600 mb-4">
                            或者 <span className="text-blue-600 underline">点击选择文件</span>
                        </p>
                        {supportedFormats && (
                            <div className="text-sm text-gray-500">
                                <p>支持格式：{supportedFormats.video_formats.join(', ')}</p>
                                <p>最大文件大小：{supportedFormats.max_file_size_mb}MB</p>
                            </div>
                        )}
                    </div>
                )}

                {/* URL输入区域 */}
                {uploadMode === 'url' && !uploadProgress && (
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                视频链接 <span className="text-red-500">*</span>
                            </label>
                            <input
                                type="url"
                                value={videoUrl}
                                onChange={(e) => setVideoUrl(e.target.value)}
                                placeholder="粘贴 YouTube、B站、Vimeo 等平台的视频链接"
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                disabled={isUploading}
                            />
                            {supportedFormats && (
                                <p className="text-sm text-gray-500 mt-1">
                                    支持平台：{supportedFormats.video_platforms.join(', ')}
                                </p>
                            )}
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                视频名称（可选）
                            </label>
                            <input
                                type="text"
                                value={videoName}
                                onChange={(e) => setVideoName(e.target.value)}
                                placeholder="为视频起一个名称"
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                disabled={isUploading}
                            />
                        </div>

                        <button
                            onClick={handleUrlUpload}
                            disabled={isUploading || !videoUrl.trim()}
                            className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                        >
                            开始处理
                        </button>
                    </div>
                )}

                {/* 高级选项 */}
                {!uploadProgress && (
                    <div className="mt-6 pt-6 border-t border-gray-200">
                        <h4 className="text-sm font-medium text-gray-900 mb-4">高级选项</h4>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {/* 语言选择 */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    视频语言
                                </label>
                                <select
                                    value={language}
                                    onChange={(e) => setLanguage(e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    disabled={isUploading}
                                >
                                    <option value="auto">自动检测</option>
                                    <option value="zh">中文</option>
                                    <option value="en">英文</option>
                                    <option value="ja">日文</option>
                                    <option value="ko">韩文</option>
                                </select>
                            </div>

                            {/* 输出格式 */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    输出格式
                                </label>
                                <div className="space-y-2">
                                    {[
                                        { value: 'markdown', label: 'Markdown' },
                                        { value: 'pdf', label: 'PDF' },
                                        { value: 'html', label: 'HTML' },
                                        { value: 'txt', label: '纯文本' }
                                    ].map((format) => (
                                        <label key={format.value} className="flex items-center">
                                            <input
                                                type="checkbox"
                                                checked={outputFormats.includes(format.value)}
                                                onChange={(e) => {
                                                    if (e.target.checked) {
                                                        setOutputFormats([...outputFormats, format.value])
                                                    } else {
                                                        setOutputFormats(outputFormats.filter(f => f !== format.value))
                                                    }
                                                }}
                                                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                                                disabled={isUploading}
                                            />
                                            <span className="ml-2 text-sm text-gray-700">{format.label}</span>
                                        </label>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}

// 类型定义
interface UploadProgress {
    percent: number
    stage: 'uploading' | 'processing' | 'completed' | 'error'
    message: string
} 