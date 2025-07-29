'use client'

import React, { useState } from 'react'
import {
    DocumentTextIcon,
    PhotoIcon,
    ClockIcon,
    EyeIcon,
    ChevronDownIcon,
    ChevronRightIcon,
    HashtagIcon,
    SpeakerWaveIcon,
    LanguageIcon,
    XMarkIcon
} from '@heroicons/react/24/outline'

interface VideoAnalysisResult {
    videoInfo: {
        filename: string
        duration: number
        size: number
        format: string
        language?: string
    }
    transcript: {
        segments: Array<{
            start: number
            end: number
            text: string
            speaker?: string
        }>
        fullText: string
        language: string
        confidence: number
    }
    images: Array<{
        timestamp: number
        url: string
        description?: string
        ocrText?: string
        tags?: string[]
    }>
    summary: {
        title: string
        brief: string
        detailed: string
        keyPoints: string[]
        tags: string[]
        chapters?: Array<{
            start: number
            end: number
            title: string
            summary: string
        }>
    }
    metadata: {
        processedAt: string
        processingTime: number
        aiModel: string
    }
}

interface ResultPreviewProps {
    result: VideoAnalysisResult
    className?: string
}

const formatTime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = Math.floor(seconds % 60)

    if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`
}

const formatFileSize = (bytes: number): string => {
    const sizes = ['B', 'KB', 'MB', 'GB']
    if (bytes === 0) return '0 B'
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`
}

export default function ResultPreview({ result, className = '' }: ResultPreviewProps) {
    const [activeTab, setActiveTab] = useState<'summary' | 'transcript' | 'images' | 'metadata'>('summary')
    const [expandedChapters, setExpandedChapters] = useState<Set<number>>(new Set())
    const [selectedImage, setSelectedImage] = useState<number | null>(null)

    const toggleChapter = (index: number) => {
        const newExpanded = new Set(expandedChapters)
        if (newExpanded.has(index)) {
            newExpanded.delete(index)
        } else {
            newExpanded.add(index)
        }
        setExpandedChapters(newExpanded)
    }

    const tabs = [
        { id: 'summary', label: '智能摘要', icon: DocumentTextIcon },
        { id: 'transcript', label: '文字转录', icon: SpeakerWaveIcon },
        { id: 'images', label: '关键帧', icon: PhotoIcon },
        { id: 'metadata', label: '元数据', icon: ClockIcon }
    ] as const

    return (
        <div className={`w-full bg-white rounded-xl shadow-lg overflow-hidden ${className}`}>
            {/* 视频信息头部 */}
            <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-6">
                <div className="flex items-start justify-between">
                    <div>
                        <h2 className="text-2xl font-bold mb-2">{result.videoInfo.filename}</h2>
                        <div className="flex items-center space-x-4 text-blue-100">
                            <span className="flex items-center">
                                <ClockIcon className="w-4 h-4 mr-1" />
                                {formatTime(result.videoInfo.duration)}
                            </span>
                            <span>{formatFileSize(result.videoInfo.size)}</span>
                            <span className="uppercase">{result.videoInfo.format}</span>
                            {result.videoInfo.language && (
                                <span className="flex items-center">
                                    <LanguageIcon className="w-4 h-4 mr-1" />
                                    {result.videoInfo.language}
                                </span>
                            )}
                        </div>
                    </div>
                    <div className="text-right">
                        <div className="text-sm opacity-75">处理完成</div>
                        <div className="text-xs opacity-60">
                            {new Date(result.metadata.processedAt).toLocaleString()}
                        </div>
                    </div>
                </div>
            </div>

            {/* 标签导航 */}
            <div className="border-b border-gray-200">
                <div className="flex">
                    {tabs.map((tab) => {
                        const Icon = tab.icon
                        return (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`
                                    flex items-center px-6 py-4 text-sm font-medium transition-colors
                                    ${activeTab === tab.id
                                        ? 'border-b-2 border-blue-500 text-blue-600 bg-blue-50'
                                        : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'
                                    }
                                `}
                            >
                                <Icon className="w-4 h-4 mr-2" />
                                {tab.label}
                            </button>
                        )
                    })}
                </div>
            </div>

            {/* 内容区域 */}
            <div className="p-6">
                {/* 智能摘要 */}
                {activeTab === 'summary' && (
                    <div className="space-y-6">
                        {/* 简要摘要 */}
                        <div>
                            <h3 className="text-lg font-semibold mb-3 text-gray-900">
                                {result.summary.title}
                            </h3>
                            <p className="text-gray-700 leading-relaxed">
                                {result.summary.brief}
                            </p>
                        </div>

                        {/* 关键要点 */}
                        <div>
                            <h4 className="font-semibold mb-3 text-gray-900">关键要点</h4>
                            <ul className="space-y-2">
                                {result.summary.keyPoints.map((point, index) => (
                                    <li key={index} className="flex items-start">
                                        <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0" />
                                        <span className="text-gray-700">{point}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>

                        {/* 标签 */}
                        <div>
                            <h4 className="font-semibold mb-3 text-gray-900">内容标签</h4>
                            <div className="flex flex-wrap gap-2">
                                {result.summary.tags.map((tag, index) => (
                                    <span
                                        key={index}
                                        className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
                                    >
                                        <HashtagIcon className="w-3 h-3 mr-1" />
                                        {tag}
                                    </span>
                                ))}
                            </div>
                        </div>

                        {/* 章节 */}
                        {result.summary.chapters && (
                            <div>
                                <h4 className="font-semibold mb-3 text-gray-900">内容章节</h4>
                                <div className="space-y-2">
                                    {result.summary.chapters.map((chapter, index) => (
                                        <div key={index} className="border border-gray-200 rounded-lg">
                                            <button
                                                onClick={() => toggleChapter(index)}
                                                className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50"
                                            >
                                                <div className="flex items-center">
                                                    {expandedChapters.has(index) ? (
                                                        <ChevronDownIcon className="w-4 h-4 mr-2 text-gray-500" />
                                                    ) : (
                                                        <ChevronRightIcon className="w-4 h-4 mr-2 text-gray-500" />
                                                    )}
                                                    <span className="font-medium">{chapter.title}</span>
                                                </div>
                                                <span className="text-sm text-gray-500">
                                                    {formatTime(chapter.start)} - {formatTime(chapter.end)}
                                                </span>
                                            </button>
                                            {expandedChapters.has(index) && (
                                                <div className="px-4 pb-4 text-gray-700">
                                                    {chapter.summary}
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* 详细摘要 */}
                        <div>
                            <h4 className="font-semibold mb-3 text-gray-900">详细摘要</h4>
                            <div className="prose max-w-none text-gray-700">
                                {result.summary.detailed.split('\n').map((paragraph, index) => (
                                    <p key={index} className="mb-3 leading-relaxed">
                                        {paragraph}
                                    </p>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {/* 文字转录 */}
                {activeTab === 'transcript' && (
                    <div className="space-y-4">
                        <div className="flex items-center justify-between">
                            <h3 className="text-lg font-semibold text-gray-900">语音转录文本</h3>
                            <div className="flex items-center space-x-4 text-sm text-gray-600">
                                <span>语言: {result.transcript.language}</span>
                                <span>准确度: {(result.transcript.confidence * 100).toFixed(1)}%</span>
                            </div>
                        </div>

                        <div className="space-y-3">
                            {result.transcript.segments.map((segment, index) => (
                                <div key={index} className="flex space-x-4 p-3 hover:bg-gray-50 rounded-lg">
                                    <div className="flex-shrink-0 text-xs text-gray-500 font-mono min-w-20">
                                        {formatTime(segment.start)}
                                    </div>
                                    <div className="flex-1">
                                        {segment.speaker && (
                                            <div className="text-xs text-blue-600 font-medium mb-1">
                                                {segment.speaker}
                                            </div>
                                        )}
                                        <p className="text-gray-800 leading-relaxed">
                                            {segment.text}
                                        </p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* 关键帧 */}
                {activeTab === 'images' && (
                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-gray-900">
                            关键帧截图 ({result.images.length} 张)
                        </h3>

                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                            {result.images.map((image, index) => (
                                <div key={index} className="bg-gray-50 rounded-lg overflow-hidden">
                                    <div className="relative">
                                        <img
                                            src={image.url}
                                            alt={`关键帧 ${formatTime(image.timestamp)}`}
                                            className="w-full h-32 object-cover cursor-pointer hover:opacity-75 transition-opacity"
                                            onClick={() => setSelectedImage(index)}
                                        />
                                        <div className="absolute bottom-2 left-2 bg-black/70 text-white text-xs px-2 py-1 rounded">
                                            {formatTime(image.timestamp)}
                                        </div>
                                        <button
                                            onClick={() => setSelectedImage(index)}
                                            className="absolute top-2 right-2 bg-black/70 text-white p-1 rounded hover:bg-black/90"
                                        >
                                            <EyeIcon className="w-4 h-4" />
                                        </button>
                                    </div>

                                    <div className="p-3">
                                        {image.description && (
                                            <p className="text-sm text-gray-700 mb-2">
                                                {image.description}
                                            </p>
                                        )}

                                        {image.ocrText && (
                                            <div className="bg-blue-50 p-2 rounded text-xs">
                                                <div className="font-medium text-blue-800 mb-1">识别文字:</div>
                                                <div className="text-blue-700">{image.ocrText}</div>
                                            </div>
                                        )}

                                        {image.tags && image.tags.length > 0 && (
                                            <div className="mt-2 flex flex-wrap gap-1">
                                                {image.tags.map((tag, tagIndex) => (
                                                    <span
                                                        key={tagIndex}
                                                        className="inline-block px-2 py-1 bg-gray-200 text-gray-700 text-xs rounded"
                                                    >
                                                        {tag}
                                                    </span>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* 元数据 */}
                {activeTab === 'metadata' && (
                    <div className="space-y-6">
                        <h3 className="text-lg font-semibold text-gray-900">处理信息</h3>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-4">
                                <h4 className="font-medium text-gray-900">视频信息</h4>
                                <dl className="space-y-2">
                                    <div className="flex justify-between">
                                        <dt className="text-gray-600">文件名:</dt>
                                        <dd className="font-mono text-sm">{result.videoInfo.filename}</dd>
                                    </div>
                                    <div className="flex justify-between">
                                        <dt className="text-gray-600">时长:</dt>
                                        <dd>{formatTime(result.videoInfo.duration)}</dd>
                                    </div>
                                    <div className="flex justify-between">
                                        <dt className="text-gray-600">大小:</dt>
                                        <dd>{formatFileSize(result.videoInfo.size)}</dd>
                                    </div>
                                    <div className="flex justify-between">
                                        <dt className="text-gray-600">格式:</dt>
                                        <dd className="uppercase">{result.videoInfo.format}</dd>
                                    </div>
                                </dl>
                            </div>

                            <div className="space-y-4">
                                <h4 className="font-medium text-gray-900">处理统计</h4>
                                <dl className="space-y-2">
                                    <div className="flex justify-between">
                                        <dt className="text-gray-600">处理时间:</dt>
                                        <dd>{result.metadata.processingTime}s</dd>
                                    </div>
                                    <div className="flex justify-between">
                                        <dt className="text-gray-600">AI模型:</dt>
                                        <dd>{result.metadata.aiModel}</dd>
                                    </div>
                                    <div className="flex justify-between">
                                        <dt className="text-gray-600">完成时间:</dt>
                                        <dd>{new Date(result.metadata.processedAt).toLocaleString()}</dd>
                                    </div>
                                    <div className="flex justify-between">
                                        <dt className="text-gray-600">转录段数:</dt>
                                        <dd>{result.transcript.segments.length}</dd>
                                    </div>
                                    <div className="flex justify-between">
                                        <dt className="text-gray-600">关键帧数:</dt>
                                        <dd>{result.images.length}</dd>
                                    </div>
                                </dl>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* 图片查看模态框 */}
            {selectedImage !== null && (
                <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-lg max-w-4xl max-h-[90vh] overflow-auto">
                        <div className="p-4 border-b flex justify-between items-center">
                            <h3 className="font-semibold">
                                关键帧 - {formatTime(result.images[selectedImage].timestamp)}
                            </h3>
                            <button
                                onClick={() => setSelectedImage(null)}
                                className="text-gray-500 hover:text-gray-700"
                            >
                                <XMarkIcon className="w-6 h-6" />
                            </button>
                        </div>
                        <div className="p-4">
                            <img
                                src={result.images[selectedImage].url}
                                alt={`关键帧 ${formatTime(result.images[selectedImage].timestamp)}`}
                                className="w-full h-auto max-h-[60vh] object-contain"
                            />
                            {result.images[selectedImage].description && (
                                <p className="mt-4 text-gray-700">
                                    {result.images[selectedImage].description}
                                </p>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
} 