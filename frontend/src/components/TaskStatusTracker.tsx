'use client'

import React from 'react'
import {
    CheckCircleIcon,
    ClockIcon,
    ExclamationTriangleIcon,
    PlayIcon,
    DocumentTextIcon,
    PhotoIcon,
    MicrophoneIcon,
    ArrowPathIcon
} from '@heroicons/react/24/outline'
import {
    CheckCircleIcon as CheckCircleIconSolid,
    ClockIcon as ClockIconSolid,
    ExclamationTriangleIcon as ExclamationTriangleIconSolid,
    PlayIcon as PlayIconSolid
} from '@heroicons/react/24/solid'

interface TaskStep {
    id: string
    title: string
    description: string
    status: 'pending' | 'in-progress' | 'completed' | 'error'
    progress?: number
    icon: React.ComponentType<any>
    solidIcon: React.ComponentType<any>
}

interface TaskStatusTrackerProps {
    currentStep?: string
    steps?: TaskStep[]
    overallProgress?: number
    className?: string
}

const defaultSteps: TaskStep[] = [
    {
        id: 'upload',
        title: '文件上传',
        description: '上传视频文件或解析视频链接',
        status: 'pending',
        icon: PlayIcon,
        solidIcon: PlayIconSolid
    },
    {
        id: 'processing',
        title: '视频处理',
        description: '提取音频和关键帧',
        status: 'pending',
        icon: ArrowPathIcon,
        solidIcon: ArrowPathIcon
    },
    {
        id: 'speech',
        title: '语音识别',
        description: 'AI语音转文字，添加时间戳',
        status: 'pending',
        icon: MicrophoneIcon,
        solidIcon: MicrophoneIcon
    },
    {
        id: 'image',
        title: '图像分析',
        description: 'OCR识别和场景描述',
        status: 'pending',
        icon: PhotoIcon,
        solidIcon: PhotoIcon
    },
    {
        id: 'summary',
        title: 'AI摘要',
        description: '生成智能摘要和结构化内容',
        status: 'pending',
        icon: DocumentTextIcon,
        solidIcon: DocumentTextIcon
    }
]

export default function TaskStatusTracker({
    currentStep,
    steps = defaultSteps,
    overallProgress = 0,
    className = ''
}: TaskStatusTrackerProps) {

    const getStepStatus = (step: TaskStep, index: number): 'pending' | 'in-progress' | 'completed' | 'error' => {
        if (step.status !== 'pending') {
            return step.status
        }

        if (currentStep === step.id) {
            return 'in-progress'
        }

        // 基于当前步骤推断状态
        const currentIndex = steps.findIndex(s => s.id === currentStep)
        if (currentIndex > index) {
            return 'completed'
        }

        return 'pending'
    }

    const getStepIcon = (step: TaskStep, status: string) => {
        const IconComponent = status === 'completed' ? step.solidIcon : step.icon

        switch (status) {
            case 'completed':
                return <CheckCircleIconSolid className="w-6 h-6 text-green-500" />
            case 'in-progress':
                return <IconComponent className="w-6 h-6 text-blue-500 animate-pulse" />
            case 'error':
                return <ExclamationTriangleIconSolid className="w-6 h-6 text-red-500" />
            default:
                return <IconComponent className="w-6 h-6 text-gray-400" />
        }
    }

    const getStepColor = (status: string) => {
        switch (status) {
            case 'completed':
                return 'text-green-600 border-green-200 bg-green-50'
            case 'in-progress':
                return 'text-blue-600 border-blue-200 bg-blue-50'
            case 'error':
                return 'text-red-600 border-red-200 bg-red-50'
            default:
                return 'text-gray-500 border-gray-200 bg-gray-50'
        }
    }

    return (
        <div className={`w-full ${className}`}>
            {/* 整体进度条 */}
            <div className="mb-6">
                <div className="flex justify-between items-center mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">处理进度</h3>
                    <span className="text-sm font-medium text-gray-600">
                        {Math.round(overallProgress)}%
                    </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                        className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-500 ease-out"
                        style={{ width: `${overallProgress}%` }}
                    />
                </div>
            </div>

            {/* 步骤列表 */}
            <div className="space-y-4">
                {steps.map((step, index) => {
                    const status = getStepStatus(step, index)
                    const isLast = index === steps.length - 1

                    return (
                        <div key={step.id} className="relative">
                            {/* 连接线 */}
                            {!isLast && (
                                <div className="absolute left-6 top-12 w-0.5 h-8 bg-gray-200" />
                            )}

                            {/* 步骤内容 */}
                            <div className={`
                                flex items-start space-x-4 p-4 rounded-lg border-2 transition-all duration-300
                                ${getStepColor(status)}
                                ${status === 'in-progress' ? 'shadow-md scale-105' : ''}
                            `}>
                                {/* 图标 */}
                                <div className="flex-shrink-0 mt-1">
                                    {getStepIcon(step, status)}
                                </div>

                                {/* 文本内容 */}
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center justify-between">
                                        <h4 className="text-sm font-semibold truncate">
                                            {step.title}
                                        </h4>
                                        {status === 'in-progress' && step.progress !== undefined && (
                                            <span className="text-xs font-medium ml-2">
                                                {step.progress}%
                                            </span>
                                        )}
                                    </div>
                                    <p className="text-xs mt-1 opacity-75">
                                        {step.description}
                                    </p>

                                    {/* 步骤特定的进度条 */}
                                    {status === 'in-progress' && step.progress !== undefined && (
                                        <div className="w-full bg-white/30 rounded-full h-1.5 mt-2">
                                            <div
                                                className="bg-current h-1.5 rounded-full transition-all duration-300"
                                                style={{ width: `${step.progress}%` }}
                                            />
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    )
                })}
            </div>

            {/* 状态说明 */}
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-6 text-xs">
                    <div className="flex items-center space-x-1">
                        <ClockIcon className="w-4 h-4 text-gray-400" />
                        <span className="text-gray-600">等待中</span>
                    </div>
                    <div className="flex items-center space-x-1">
                        <ArrowPathIcon className="w-4 h-4 text-blue-500 animate-spin" />
                        <span className="text-blue-600">处理中</span>
                    </div>
                    <div className="flex items-center space-x-1">
                        <CheckCircleIconSolid className="w-4 h-4 text-green-500" />
                        <span className="text-green-600">已完成</span>
                    </div>
                    <div className="flex items-center space-x-1">
                        <ExclamationTriangleIconSolid className="w-4 h-4 text-red-500" />
                        <span className="text-red-600">出错</span>
                    </div>
                </div>
            </div>
        </div>
    )
} 