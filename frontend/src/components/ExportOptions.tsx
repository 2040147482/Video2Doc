'use client'

import React, { useState } from 'react'
import {
    DocumentTextIcon,
    DocumentIcon,
    ArchiveBoxIcon,
    ClipboardDocumentListIcon,
    PaintBrushIcon,
    PhotoIcon,
    ClockIcon,
    TagIcon,
    ArrowDownTrayIcon,
    CheckCircleIcon,
    ExclamationTriangleIcon
} from '@heroicons/react/24/outline'
import { api } from '@/lib/api'

interface ExportFormat {
    id: string
    name: string
    description: string
    icon: React.ComponentType<any>
    extension: string
    size?: string
}

interface ExportTemplate {
    id: string
    name: string
    description: string
    icon: React.ComponentType<any>
}

interface ExportOptionsProps {
    taskId: string
    onExportSuccess?: (exportId: string) => void
    onExportError?: (error: string) => void
    className?: string
}

const formats: ExportFormat[] = [
    {
        id: 'markdown',
        name: 'Markdown',
        description: '适用于Obsidian、Notion等笔记软件',
        icon: DocumentTextIcon,
        extension: '.md',
        size: '小'
    },
    {
        id: 'html',
        name: 'HTML',
        description: '包含CSS样式的网页格式，可在浏览器中查看',
        icon: DocumentIcon,
        extension: '.html',
        size: '中'
    },
    {
        id: 'txt',
        name: '纯文本',
        description: '不包含格式的纯文字内容',
        icon: ClipboardDocumentListIcon,
        extension: '.txt',
        size: '小'
    },
    {
        id: 'pdf',
        name: 'PDF',
        description: '便于打印和分享的PDF文档',
        icon: DocumentIcon,
        extension: '.pdf',
        size: '大'
    },
    {
        id: 'zip',
        name: 'ZIP压缩包',
        description: '包含所有格式和图片的完整压缩包',
        icon: ArchiveBoxIcon,
        extension: '.zip',
        size: '大'
    }
]

const templates: ExportTemplate[] = [
    {
        id: 'standard',
        name: '标准模板',
        description: '平衡的内容展示，适合大多数场景',
        icon: DocumentTextIcon
    },
    {
        id: 'academic',
        name: '学术模板',
        description: '详细的结构化格式，适合学术研究',
        icon: ClipboardDocumentListIcon
    },
    {
        id: 'presentation',
        name: '演示模板',
        description: '重点突出，适合会议演示',
        icon: PaintBrushIcon
    },
    {
        id: 'simple',
        name: '简洁模板',
        description: '简单清晰，去除不必要的装饰',
        icon: DocumentIcon
    },
    {
        id: 'detailed',
        name: '详细模板',
        description: '包含所有信息的完整格式',
        icon: TagIcon
    }
]

export default function ExportOptions({
    taskId,
    onExportSuccess,
    onExportError,
    className = ''
}: ExportOptionsProps) {
    const [selectedFormats, setSelectedFormats] = useState<string[]>(['markdown'])
    const [selectedTemplate, setSelectedTemplate] = useState<string>('standard')
    const [includeImages, setIncludeImages] = useState(true)
    const [includeTimestamps, setIncludeTimestamps] = useState(true)
    const [includeMetadata, setIncludeMetadata] = useState(true)
    const [customFilename, setCustomFilename] = useState('')
    const [isExporting, setIsExporting] = useState(false)
    const [exportProgress, setExportProgress] = useState<string | null>(null)

    const toggleFormat = (formatId: string) => {
        setSelectedFormats(prev => {
            if (prev.includes(formatId)) {
                return prev.filter(id => id !== formatId)
            } else {
                return [...prev, formatId]
            }
        })
    }

    const handleExport = async () => {
        if (selectedFormats.length === 0) {
            onExportError?.('请至少选择一种导出格式')
            return
        }

        setIsExporting(true)
        setExportProgress('准备导出任务...')

        try {
            const exportRequest = {
                task_id: taskId,
                formats: selectedFormats,
                template: selectedTemplate,
                include_images: includeImages,
                include_timestamps: includeTimestamps,
                include_metadata: includeMetadata,
                custom_filename: customFilename || undefined
            }

            const response = await api.createExport(exportRequest)

            if (response.export_id) {
                setExportProgress('导出任务已创建，正在处理...')
                onExportSuccess?.(response.export_id)
            } else {
                throw new Error('创建导出任务失败')
            }

        } catch (error) {
            console.error('导出失败:', error)
            onExportError?.(error instanceof Error ? error.message : '导出失败')
        } finally {
            setIsExporting(false)
            setExportProgress(null)
        }
    }

    const getEstimatedSize = (): string => {
        const sizes = selectedFormats.map(formatId => {
            const format = formats.find(f => f.id === formatId)
            return format?.size || '中'
        })

        if (sizes.includes('大')) return '大'
        if (sizes.includes('中')) return '中'
        return '小'
    }

    return (
        <div className={`w-full bg-white rounded-xl shadow-lg overflow-hidden ${className}`}>
            {/* 标题 */}
            <div className="bg-gradient-to-r from-green-500 to-blue-500 text-white p-6">
                <h2 className="text-xl font-bold flex items-center">
                    <ArrowDownTrayIcon className="w-6 h-6 mr-2" />
                    导出选项
                </h2>
                <p className="text-green-100 mt-1">
                    选择导出格式和模板，将处理结果保存为不同格式的文档
                </p>
            </div>

            <div className="p-6 space-y-8">
                {/* 导出格式选择 */}
                <div>
                    <h3 className="text-lg font-semibold mb-4 text-gray-900">
                        选择导出格式
                        <span className="text-sm font-normal text-gray-500 ml-2">
                            (已选择 {selectedFormats.length} 种)
                        </span>
                    </h3>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {formats.map((format) => {
                            const Icon = format.icon
                            const isSelected = selectedFormats.includes(format.id)

                            return (
                                <div
                                    key={format.id}
                                    onClick={() => toggleFormat(format.id)}
                                    className={`
                                        relative p-4 border-2 rounded-lg cursor-pointer transition-all
                                        ${isSelected
                                            ? 'border-blue-500 bg-blue-50 text-blue-700'
                                            : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                                        }
                                    `}
                                >
                                    {isSelected && (
                                        <CheckCircleIcon className="absolute top-2 right-2 w-5 h-5 text-blue-500" />
                                    )}

                                    <div className="flex items-start space-x-3">
                                        <Icon className={`w-6 h-6 mt-1 ${isSelected ? 'text-blue-500' : 'text-gray-400'}`} />
                                        <div className="flex-1">
                                            <div className="flex items-center justify-between">
                                                <h4 className="font-medium">{format.name}</h4>
                                                <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                                                    {format.extension}
                                                </span>
                                            </div>
                                            <p className="text-sm opacity-75 mt-1">
                                                {format.description}
                                            </p>
                                            <div className="flex justify-between items-center mt-2">
                                                <span className="text-xs opacity-60">
                                                    文件大小: {format.size}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )
                        })}
                    </div>
                </div>

                {/* 模板选择 */}
                <div>
                    <h3 className="text-lg font-semibold mb-4 text-gray-900">选择导出模板</h3>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {templates.map((template) => {
                            const Icon = template.icon
                            const isSelected = selectedTemplate === template.id

                            return (
                                <div
                                    key={template.id}
                                    onClick={() => setSelectedTemplate(template.id)}
                                    className={`
                                        relative p-4 border-2 rounded-lg cursor-pointer transition-all
                                        ${isSelected
                                            ? 'border-green-500 bg-green-50 text-green-700'
                                            : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                                        }
                                    `}
                                >
                                    {isSelected && (
                                        <CheckCircleIcon className="absolute top-2 right-2 w-5 h-5 text-green-500" />
                                    )}

                                    <div className="flex items-start space-x-3">
                                        <Icon className={`w-6 h-6 mt-1 ${isSelected ? 'text-green-500' : 'text-gray-400'}`} />
                                        <div className="flex-1">
                                            <h4 className="font-medium">{template.name}</h4>
                                            <p className="text-sm opacity-75 mt-1">
                                                {template.description}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            )
                        })}
                    </div>
                </div>

                {/* 内容选项 */}
                <div>
                    <h3 className="text-lg font-semibold mb-4 text-gray-900">包含内容</h3>

                    <div className="space-y-3">
                        <label className="flex items-center space-x-3 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={includeImages}
                                onChange={(e) => setIncludeImages(e.target.checked)}
                                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                            />
                            <div className="flex items-center space-x-2">
                                <PhotoIcon className="w-5 h-5 text-gray-400" />
                                <span className="text-gray-700">包含关键帧图片</span>
                            </div>
                            <span className="text-sm text-gray-500">
                                (将增加文件大小)
                            </span>
                        </label>

                        <label className="flex items-center space-x-3 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={includeTimestamps}
                                onChange={(e) => setIncludeTimestamps(e.target.checked)}
                                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                            />
                            <div className="flex items-center space-x-2">
                                <ClockIcon className="w-5 h-5 text-gray-400" />
                                <span className="text-gray-700">包含时间戳</span>
                            </div>
                            <span className="text-sm text-gray-500">
                                (显示每段内容的时间位置)
                            </span>
                        </label>

                        <label className="flex items-center space-x-3 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={includeMetadata}
                                onChange={(e) => setIncludeMetadata(e.target.checked)}
                                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                            />
                            <div className="flex items-center space-x-2">
                                <TagIcon className="w-5 h-5 text-gray-400" />
                                <span className="text-gray-700">包含元数据</span>
                            </div>
                            <span className="text-sm text-gray-500">
                                (处理信息、模型版本等)
                            </span>
                        </label>
                    </div>
                </div>

                {/* 自定义文件名 */}
                <div>
                    <h3 className="text-lg font-semibold mb-4 text-gray-900">自定义文件名</h3>
                    <input
                        type="text"
                        value={customFilename}
                        onChange={(e) => setCustomFilename(e.target.value)}
                        placeholder="留空使用默认文件名"
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <p className="text-sm text-gray-500 mt-2">
                        文件名将自动添加适当的扩展名
                    </p>
                </div>

                {/* 导出摘要 */}
                <div className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="font-medium text-gray-900 mb-2">导出摘要</h4>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                            <span className="text-gray-600">格式数量:</span>
                            <span className="ml-2 font-medium">{selectedFormats.length} 种</span>
                        </div>
                        <div>
                            <span className="text-gray-600">模板:</span>
                            <span className="ml-2 font-medium">
                                {templates.find(t => t.id === selectedTemplate)?.name}
                            </span>
                        </div>
                        <div>
                            <span className="text-gray-600">预估大小:</span>
                            <span className="ml-2 font-medium">{getEstimatedSize()}</span>
                        </div>
                        <div>
                            <span className="text-gray-600">包含内容:</span>
                            <span className="ml-2 font-medium">
                                {[
                                    includeImages && '图片',
                                    includeTimestamps && '时间戳',
                                    includeMetadata && '元数据'
                                ].filter(Boolean).join(', ') || '仅文本'}
                            </span>
                        </div>
                    </div>
                </div>

                {/* 导出按钮 */}
                <div className="flex justify-end pt-4 border-t">
                    <button
                        onClick={handleExport}
                        disabled={isExporting || selectedFormats.length === 0}
                        className={`
                            flex items-center px-6 py-3 rounded-lg font-medium transition-all
                            ${isExporting || selectedFormats.length === 0
                                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                : 'bg-gradient-to-r from-green-500 to-blue-500 text-white hover:from-green-600 hover:to-blue-600 shadow-lg hover:shadow-xl'
                            }
                        `}
                    >
                        {isExporting ? (
                            <>
                                <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full mr-2" />
                                导出中...
                            </>
                        ) : (
                            <>
                                <ArrowDownTrayIcon className="w-5 h-5 mr-2" />
                                开始导出
                            </>
                        )}
                    </button>
                </div>

                {/* 导出进度 */}
                {exportProgress && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                        <div className="flex items-center">
                            <div className="animate-spin w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full mr-3" />
                            <span className="text-blue-700">{exportProgress}</span>
                        </div>
                    </div>
                )}

                {/* 错误提示 */}
                {selectedFormats.length === 0 && (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                        <div className="flex items-center">
                            <ExclamationTriangleIcon className="w-5 h-5 text-yellow-500 mr-3" />
                            <span className="text-yellow-700">请至少选择一种导出格式</span>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
} 