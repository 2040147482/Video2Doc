'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'

export function VideoUpload() {
    const [uploadMode, setUploadMode] = useState<'file' | 'url'>('file')
    const [videoUrl, setVideoUrl] = useState('')
    const [isUploading, setIsUploading] = useState(false)

    const onDrop = useCallback((acceptedFiles: File[]) => {
        const file = acceptedFiles[0]
        if (file) {
            setIsUploading(true)
            // 这里会调用后端API上传文件
            console.log('上传文件:', file.name)

            // 模拟上传过程
            setTimeout(() => {
                setIsUploading(false)
                alert('文件上传成功！')
            }, 2000)
        }
    }, [])

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'video/*': ['.mp4', '.mov', '.avi', '.mkv', '.webm']
        },
        maxSize: 2 * 1024 * 1024 * 1024, // 2GB
        multiple: false
    })

    const handleUrlSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        if (videoUrl.trim()) {
            setIsUploading(true)
            console.log('处理视频链接:', videoUrl)

            // 模拟处理过程
            setTimeout(() => {
                setIsUploading(false)
                alert('视频链接处理成功！')
            }, 2000)
        }
    }

    return (
        <div className="w-full max-w-2xl mx-auto">
            {/* 上传模式切换 */}
            <div className="flex mb-6 bg-gray-100 rounded-lg p-1">
                <button
                    onClick={() => setUploadMode('file')}
                    className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${uploadMode === 'file'
                        ? 'bg-white text-gray-900 shadow-sm'
                        : 'text-gray-600 hover:text-gray-900'
                        }`}
                >
                    本地上传
                </button>
                <button
                    onClick={() => setUploadMode('url')}
                    className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${uploadMode === 'url'
                        ? 'bg-white text-gray-900 shadow-sm'
                        : 'text-gray-600 hover:text-gray-900'
                        }`}
                >
                    在线链接
                </button>
            </div>

            {uploadMode === 'file' ? (
                /* 文件上传区域 */
                <div
                    {...getRootProps()}
                    className={`upload-area border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${isDragActive
                        ? 'border-blue-400 bg-blue-50'
                        : 'border-gray-300 hover:border-gray-400'
                        } ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                    <input {...getInputProps()} disabled={isUploading} />

                    <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                        </svg>
                    </div>

                    {isUploading ? (
                        <div>
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                            <p className="text-blue-600 font-medium">正在上传...</p>
                        </div>
                    ) : (
                        <div>
                            <p className="text-lg font-medium text-gray-900 mb-2">
                                {isDragActive ? '放开文件开始上传' : '拖拽视频文件到这里'}
                            </p>
                            <p className="text-gray-500 mb-4">
                                或者 <span className="text-blue-600 font-medium">点击选择文件</span>
                            </p>
                            <p className="text-sm text-gray-400">
                                支持 MP4、MOV、AVI、MKV、WEBM 格式，最大 2GB
                            </p>
                        </div>
                    )}
                </div>
            ) : (
                /* URL输入区域 */
                <form onSubmit={handleUrlSubmit} className="space-y-4">
                    <div>
                        <label htmlFor="video-url" className="block text-sm font-medium text-gray-700 mb-2">
                            视频链接
                        </label>
                        <input
                            id="video-url"
                            type="url"
                            value={videoUrl}
                            onChange={(e) => setVideoUrl(e.target.value)}
                            placeholder="请输入YouTube、B站等视频链接"
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            disabled={isUploading}
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={!videoUrl.trim() || isUploading}
                        className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        {isUploading ? (
                            <div className="flex items-center justify-center">
                                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                                处理中...
                            </div>
                        ) : (
                            '开始分析'
                        )}
                    </button>
                </form>
            )}

            {/* 提示信息 */}
            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                <div className="flex">
                    <svg className="w-5 h-5 text-blue-600 mr-2 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div className="text-sm text-blue-800">
                        <p className="font-medium mb-1">处理时间说明：</p>
                        <p>• 5分钟视频约需 2-3 分钟处理</p>
                        <p>• 处理时间与视频长度和内容复杂度相关</p>
                        <p>• 我们会实时显示处理进度</p>
                    </div>
                </div>
            </div>
        </div>
    )
} 