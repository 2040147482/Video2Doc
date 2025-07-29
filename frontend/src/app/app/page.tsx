'use client'

import React, { useState } from 'react'
import Header from '@/components/Header'
import Footer from '@/components/Footer'
import VideoUpload from '@/components/VideoUpload'
import TaskStatusTracker from '@/components/TaskStatusTracker'
import ResultPreview from '@/components/ResultPreview'
import ExportOptions from '@/components/ExportOptions'
import {
    DocumentTextIcon,
    PhotoIcon,
    ClockIcon,
    ArrowLeftIcon,
    ArrowDownTrayIcon,
    CheckCircleIcon
} from '@heroicons/react/24/outline'

// 模拟数据类型
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

type AppState = 'upload' | 'processing' | 'result' | 'export'

export default function AppPage() {
    const [currentState, setCurrentState] = useState<AppState>('upload')
    const [currentTaskId, setCurrentTaskId] = useState<string | null>(null)
    const [processingStep, setProcessingStep] = useState<string>('upload')
    const [processingProgress, setProcessingProgress] = useState<number>(0)
    const [analysisResult, setAnalysisResult] = useState<VideoAnalysisResult | null>(null)

    // 模拟分析结果数据
    const mockAnalysisResult: VideoAnalysisResult = {
        videoInfo: {
            filename: "AI技术发展趋势讲座.mp4",
            duration: 1800, // 30分钟
            size: 524288000, // 500MB
            format: "mp4",
            language: "中文"
        },
        transcript: {
            segments: [
                {
                    start: 0,
                    end: 30,
                    text: "大家好，欢迎来到今天的AI技术发展趋势讲座。在过去的几年里，人工智能技术发生了翻天覆地的变化。",
                    speaker: "讲师"
                },
                {
                    start: 30,
                    end: 65,
                    text: "从最初的机器学习算法到现在的大语言模型，我们见证了AI能力的指数级增长。",
                    speaker: "讲师"
                },
                {
                    start: 65,
                    end: 120,
                    text: "特别是ChatGPT的发布，标志着AI技术进入了一个全新的时代。让我们来看看这些技术是如何改变我们的生活和工作方式的。",
                    speaker: "讲师"
                }
            ],
            fullText: "大家好，欢迎来到今天的AI技术发展趋势讲座...",
            language: "中文",
            confidence: 0.95
        },
        images: [
            {
                timestamp: 45,
                url: "https://via.placeholder.com/640x360/1f2937/ffffff?text=AI+Timeline",
                description: "AI技术发展时间线图表",
                ocrText: "2010: 深度学习兴起\n2015: 图像识别突破\n2020: GPT-3发布\n2023: ChatGPT爆发",
                tags: ["时间线", "技术发展", "里程碑"]
            },
            {
                timestamp: 180,
                url: "https://via.placeholder.com/640x360/3b82f6/ffffff?text=Market+Growth",
                description: "AI市场增长预测图",
                ocrText: "AI市场规模\n2023: $150B\n2028: $1.3T",
                tags: ["市场", "增长", "预测"]
            },
            {
                timestamp: 320,
                url: "https://via.placeholder.com/640x360/10b981/ffffff?text=Applications",
                description: "AI应用领域分布",
                tags: ["应用", "领域", "分布"]
            }
        ],
        summary: {
            title: "AI技术发展趋势与未来展望",
            brief: "本讲座深入探讨了人工智能技术的发展历程，从早期机器学习到现代大语言模型的演进过程，分析了AI技术对各行业的影响，并展望了未来发展趋势。",
            detailed: "讲座首先回顾了AI技术的发展历程，重点介绍了深度学习、自然语言处理、计算机视觉等关键技术的突破。\n\n随后分析了ChatGPT等大语言模型对AI领域带来的革命性变化，以及这些技术在教育、医疗、金融、制造业等各个领域的实际应用案例。\n\n最后展望了AI技术的未来发展方向，包括多模态AI、AGI（通用人工智能）的发展路径，以及可能面临的挑战和机遇。",
            keyPoints: [
                "AI技术在过去十年经历了跨越式发展",
                "大语言模型标志着AI进入新时代",
                "AI正在重塑传统行业的工作模式",
                "多模态AI将是下一个重要发展方向",
                "AI安全和伦理问题需要重点关注"
            ],
            tags: ["人工智能", "技术趋势", "大语言模型", "行业应用", "未来展望"],
            chapters: [
                {
                    start: 0,
                    end: 300,
                    title: "AI技术发展回顾",
                    summary: "回顾了从传统机器学习到深度学习的技术演进历程"
                },
                {
                    start: 300,
                    end: 900,
                    title: "大语言模型革命",
                    summary: "深入分析了GPT系列模型的技术突破和应用影响"
                },
                {
                    start: 900,
                    end: 1500,
                    title: "行业应用案例",
                    summary: "展示了AI技术在各个行业的具体应用和成功案例"
                },
                {
                    start: 1500,
                    end: 1800,
                    title: "未来发展趋势",
                    summary: "展望了AI技术的未来发展方向和潜在挑战"
                }
            ]
        },
        metadata: {
            processedAt: new Date().toISOString(),
            processingTime: 180,
            aiModel: "GPT-4 + Whisper + Vision"
        }
    }

    const handleVideoUploadSuccess = (taskId: string) => {
        setCurrentTaskId(taskId)
        setCurrentState('processing')
        setProcessingStep('upload')
        setProcessingProgress(10)

        // 模拟处理过程
        simulateProcessing()
    }

    const simulateProcessing = () => {
        const steps = ['upload', 'processing', 'speech', 'image', 'summary']
        let currentIndex = 0

        const interval = setInterval(() => {
            currentIndex++
            if (currentIndex < steps.length) {
                setProcessingStep(steps[currentIndex])
                setProcessingProgress((currentIndex + 1) * 20)
            } else {
                setProcessingProgress(100)
                setCurrentState('result')
                setAnalysisResult(mockAnalysisResult)
                clearInterval(interval)
            }
        }, 3000) // 每3秒切换一个步骤
    }

    const handleExportSuccess = (exportId: string) => {
        setCurrentState('export')
        // 这里可以添加导出状态跟踪逻辑
    }

    const handleBackToUpload = () => {
        setCurrentState('upload')
        setCurrentTaskId(null)
        setProcessingStep('upload')
        setProcessingProgress(0)
        setAnalysisResult(null)
    }

    const renderStateContent = () => {
        switch (currentState) {
            case 'upload':
                return (
                    <div className="space-y-8">
                        <VideoUpload />

                        {/* 演示按钮 */}
                        <div className="text-center">
                            <button
                                onClick={() => handleVideoUploadSuccess('demo-task-id')}
                                className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-6 py-3 rounded-lg font-medium hover:from-purple-600 hover:to-pink-600 transition-all shadow-lg"
                            >
                                🎬 查看演示效果
                            </button>
                            <p className="text-gray-500 text-sm mt-2">
                                点击查看完整的视频分析流程演示
                            </p>
                        </div>
                    </div>
                )

            case 'processing':
                return (
                    <div className="space-y-8">
                        <div className="flex items-center justify-between">
                            <h1 className="text-2xl font-bold text-gray-900">处理中...</h1>
                            <button
                                onClick={handleBackToUpload}
                                className="flex items-center text-gray-600 hover:text-gray-800"
                            >
                                <ArrowLeftIcon className="w-4 h-4 mr-1" />
                                返回上传
                            </button>
                        </div>

                        <TaskStatusTracker
                            currentStep={processingStep}
                            overallProgress={processingProgress}
                        />

                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                            <div className="flex items-center">
                                <ClockIcon className="w-5 h-5 text-blue-500 mr-3" />
                                <div>
                                    <p className="text-blue-800 font-medium">正在处理您的视频</p>
                                    <p className="text-blue-600 text-sm">
                                        预计还需 {Math.max(0, Math.round((100 - processingProgress) / 10))} 分钟完成
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                )

            case 'result':
                return (
                    <div className="space-y-8">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center">
                                <CheckCircleIcon className="w-8 h-8 text-green-500 mr-3" />
                                <div>
                                    <h1 className="text-2xl font-bold text-gray-900">分析完成</h1>
                                    <p className="text-gray-600">视频内容已成功分析并结构化</p>
                                </div>
                            </div>
                            <div className="flex space-x-3">
                                <button
                                    onClick={() => setCurrentState('export')}
                                    className="bg-gradient-to-r from-green-500 to-blue-500 text-white px-4 py-2 rounded-lg font-medium hover:from-green-600 hover:to-blue-600 transition-all flex items-center"
                                >
                                    <ArrowDownTrayIcon className="w-4 h-4 mr-2" />
                                    导出文档
                                </button>
                                <button
                                    onClick={handleBackToUpload}
                                    className="text-gray-600 hover:text-gray-800 px-4 py-2 rounded-lg border border-gray-300 hover:bg-gray-50"
                                >
                                    分析新视频
                                </button>
                            </div>
                        </div>

                        {analysisResult && (
                            <ResultPreview result={analysisResult} />
                        )}
                    </div>
                )

            case 'export':
                return (
                    <div className="space-y-8">
                        <div className="flex items-center justify-between">
                            <h1 className="text-2xl font-bold text-gray-900">导出文档</h1>
                            <div className="flex space-x-3">
                                <button
                                    onClick={() => setCurrentState('result')}
                                    className="text-gray-600 hover:text-gray-800 px-4 py-2 rounded-lg border border-gray-300 hover:bg-gray-50"
                                >
                                    <ArrowLeftIcon className="w-4 h-4 mr-2 inline" />
                                    返回结果
                                </button>
                                <button
                                    onClick={handleBackToUpload}
                                    className="text-gray-600 hover:text-gray-800 px-4 py-2 rounded-lg border border-gray-300 hover:bg-gray-50"
                                >
                                    分析新视频
                                </button>
                            </div>
                        </div>

                        {currentTaskId && (
                            <ExportOptions
                                taskId={currentTaskId}
                                onExportSuccess={handleExportSuccess}
                                onExportError={(error) => console.error('Export error:', error)}
                            />
                        )}
                    </div>
                )

            default:
                return null
        }
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
            <Header />

            <main className="container mx-auto px-4 py-8">
                {/* 进度指示器 */}
                <div className="mb-8 max-w-4xl mx-auto">
                    <div className="flex items-center justify-center space-x-8">
                        {[
                            { id: 'upload', label: '上传视频', icon: DocumentTextIcon },
                            { id: 'processing', label: 'AI分析', icon: ClockIcon },
                            { id: 'result', label: '查看结果', icon: PhotoIcon },
                            { id: 'export', label: '导出文档', icon: ArrowDownTrayIcon }
                        ].map((step, index) => {
                            const Icon = step.icon
                            const isActive = currentState === step.id
                            const isCompleted = ['upload', 'processing', 'result'].indexOf(currentState) > ['upload', 'processing', 'result'].indexOf(step.id)

                            return (
                                <div key={step.id} className="flex items-center">
                                    <div className={`
                                        flex items-center justify-center w-10 h-10 rounded-full border-2 transition-all
                                        ${isActive ? 'border-blue-500 bg-blue-500 text-white' :
                                            isCompleted ? 'border-green-500 bg-green-500 text-white' :
                                                'border-gray-300 bg-white text-gray-400'}
                                    `}>
                                        <Icon className="w-5 h-5" />
                                    </div>
                                    <span className={`ml-2 text-sm font-medium ${isActive ? 'text-blue-600' :
                                            isCompleted ? 'text-green-600' : 'text-gray-500'
                                        }`}>
                                        {step.label}
                                    </span>
                                    {index < 3 && (
                                        <div className={`ml-4 w-8 h-0.5 ${isCompleted ? 'bg-green-500' : 'bg-gray-300'
                                            }`} />
                                    )}
                                </div>
                            )
                        })}
                    </div>
                </div>

                {/* 主内容区域 */}
                <div className="max-w-6xl mx-auto">
                    {renderStateContent()}
                </div>
            </main>

            <Footer />
        </div>
    )
} 