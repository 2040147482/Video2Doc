"use client"

import { useState } from 'react'
import { CheckIcon, XMarkIcon, StarIcon } from '@heroicons/react/24/outline'

interface PricingPlan {
    id: string
    name: string
    price: {
        monthly: number
        yearly: number
    }
    description: string
    features: {
        videoLength: string
        uploadMethods: string
        aiNotes: string
        speechToText: string
        imageExtraction: string
        timeline: boolean
        languages: string
        exportFormats: string
        historyLimit: string
        processingSpeed: string
        support: string
    }
    highlight?: boolean
    popular?: boolean
}

const pricingPlans: PricingPlan[] = [
    {
        id: 'starter',
        name: '入门版',
        price: { monthly: 4.99, yearly: 49.99 },
        description: '适合个人用户的基础需求',
        features: {
            videoLength: '10 分钟',
            uploadMethods: '本地上传',
            aiNotes: '基础结构提取',
            speechToText: '标准模型',
            imageExtraction: '❌',
            timeline: false,
            languages: '英语',
            exportFormats: 'Markdown',
            historyLimit: '5 篇',
            processingSpeed: '❌',
            support: '邮件支持'
        }
    },
    {
        id: 'standard',
        name: '标准版',
        price: { monthly: 9.99, yearly: 99.99 },
        description: '最受欢迎的选择，功能全面',
        features: {
            videoLength: '30 分钟',
            uploadMethods: '本地 / 链接导入',
            aiNotes: '精准语义摘要 + 段落结构',
            speechToText: '精准模型（支持多口音）',
            imageExtraction: '支持 1 张封面图',
            timeline: true,
            languages: '英语 / 中文',
            exportFormats: 'Markdown / PDF',
            historyLimit: '30 篇',
            processingSpeed: '标准队列',
            support: '邮件 + FAQ 教程'
        },
        highlight: true,
        popular: true
    },
    {
        id: 'premium',
        name: '高级版',
        price: { monthly: 19.99, yearly: 199.99 },
        description: '专业用户的完整解决方案',
        features: {
            videoLength: '90 分钟',
            uploadMethods: '本地 / 链接 / 云盘导入',
            aiNotes: '多风格笔记（摘要/清单/图表）',
            speechToText: '专业模型 + 智能断句优化',
            imageExtraction: '支持 3～5 张关键帧图像',
            timeline: true,
            languages: '多语言（支持 10+ 语言）',
            exportFormats: 'Markdown / PDF / Notion',
            historyLimit: '无限制',
            processingSpeed: '高优先通道',
            support: '邮件 + 实时聊天支持'
        }
    }
]

const featureLabels = {
    videoLength: '🎥 视频时长上限（每次）',
    uploadMethods: '📥 视频上传方式支持',
    aiNotes: '🧠 AI 智能笔记生成',
    speechToText: '🗣️ 视频语音转文字（ASR）',
    imageExtraction: '🖼️ 视频图像提取（关键帧）',
    timeline: '🧾 自动生成时间轴目录',
    languages: '🌐 多语言识别支持',
    exportFormats: '📤 笔记导出格式',
    historyLimit: '🔄 历史笔记保存（每月）',
    processingSpeed: '🚀 加速处理通道（优先级）',
    support: '👤 客服支持'
}

export default function PricingSection() {
    const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'yearly'>('monthly')
    const [isLoading, setIsLoading] = useState<string | null>(null)

    const handleSubscribe = async (planId: string) => {
        setIsLoading(planId)

        try {
            // 调用后端API创建Creem结账会话
            const response = await fetch('/api/payments/create-checkout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    planId,
                    billingPeriod,
                    returnUrl: `${window.location.origin}/dashboard`,
                    cancelUrl: `${window.location.origin}/pricing`
                })
            })

            if (!response.ok) {
                throw new Error('Failed to create checkout session')
            }

            const { checkoutUrl } = await response.json()

            // 跳转到Creem支付页面
            window.location.href = checkoutUrl
        } catch (error) {
            console.error('Payment error:', error)
            alert('支付初始化失败，请稍后重试')
        } finally {
            setIsLoading(null)
        }
    }

    const getYearlyDiscount = (monthly: number, yearly: number) => {
        const monthlyTotal = monthly * 12
        const discount = ((monthlyTotal - yearly) / monthlyTotal) * 100
        return Math.round(discount)
    }

    return (
        <section className="bg-white py-24 sm:py-32">
            <div className="mx-auto max-w-7xl px-6 lg:px-8">
                {/* Header */}
                <div className="mx-auto max-w-4xl text-center">
                    <h2 className="text-base font-semibold leading-7 text-indigo-600">定价</h2>
                    <p className="mt-2 text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
                        选择适合你的套餐
                    </p>
                    <p className="mt-6 text-lg leading-8 text-gray-600">
                        从基础版到专业版，我们提供灵活的定价方案满足不同用户需求
                    </p>
                </div>

                {/* Free Trial Banner */}
                <div className="mx-auto mt-16 max-w-2xl rounded-3xl ring-1 ring-gray-200 p-8 bg-gradient-to-r from-indigo-50 to-purple-50">
                    <div className="text-center">
                        <h3 className="text-2xl font-bold text-gray-900">🎁 免费试用</h3>
                        <p className="mt-2 text-gray-600">注册即可获得 3 次免费视频分析机会</p>
                        <div className="mt-4">
                            <button
                                className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                                onClick={() => window.location.href = '/register'}
                            >
                                立即免费试用
                            </button>
                        </div>
                    </div>
                </div>

                {/* Billing Toggle */}
                <div className="mt-16 flex justify-center">
                    <div className="relative">
                        <div className="flex rounded-lg bg-gray-100 p-1">
                            <button
                                className={`relative whitespace-nowrap rounded-md py-2 px-6 text-sm font-medium transition-all focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${billingPeriod === 'monthly'
                                        ? 'bg-white text-gray-900 shadow-sm'
                                        : 'text-gray-700 hover:text-gray-900'
                                    }`}
                                onClick={() => setBillingPeriod('monthly')}
                            >
                                按月付费
                            </button>
                            <button
                                className={`relative whitespace-nowrap rounded-md py-2 px-6 text-sm font-medium transition-all focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${billingPeriod === 'yearly'
                                        ? 'bg-white text-gray-900 shadow-sm'
                                        : 'text-gray-700 hover:text-gray-900'
                                    }`}
                                onClick={() => setBillingPeriod('yearly')}
                            >
                                按年付费
                                <span className="ml-1 inline-flex items-center rounded-full bg-indigo-100 px-2 py-0.5 text-xs font-medium text-indigo-800">
                                    省17%
                                </span>
                            </button>
                        </div>
                    </div>
                </div>

                {/* Pricing Cards */}
                <div className="isolate mx-auto mt-16 grid max-w-md grid-cols-1 gap-y-8 sm:mt-20 lg:mx-0 lg:max-w-none lg:grid-cols-3 lg:gap-x-8">
                    {pricingPlans.map((plan) => (
                        <div
                            key={plan.id}
                            className={`flex flex-col justify-between rounded-3xl p-8 ring-1 xl:p-10 ${plan.highlight
                                    ? 'ring-2 ring-indigo-600 relative'
                                    : 'ring-gray-200'
                                }`}
                        >
                            {plan.popular && (
                                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                                    <span className="inline-flex items-center rounded-full bg-indigo-600 px-4 py-1 text-sm font-medium text-white">
                                        <StarIcon className="mr-1 h-4 w-4" />
                                        最受欢迎
                                    </span>
                                </div>
                            )}

                            <div>
                                <div className="flex items-center justify-between gap-x-4">
                                    <h3 className="text-lg font-semibold leading-8 text-gray-900">
                                        {plan.name}
                                    </h3>
                                </div>
                                <p className="mt-4 text-sm leading-6 text-gray-600">
                                    {plan.description}
                                </p>
                                <p className="mt-6 flex items-baseline gap-x-1">
                                    <span className="text-4xl font-bold tracking-tight text-gray-900">
                                        ${billingPeriod === 'monthly' ? plan.price.monthly : plan.price.yearly}
                                    </span>
                                    <span className="text-sm font-semibold leading-6 text-gray-600">
                                        /{billingPeriod === 'monthly' ? '月' : '年'}
                                    </span>
                                </p>
                                {billingPeriod === 'yearly' && (
                                    <p className="mt-2 text-sm text-green-600">
                                        比月付节省 {getYearlyDiscount(plan.price.monthly, plan.price.yearly)}%
                                    </p>
                                )}

                                <button
                                    onClick={() => handleSubscribe(plan.id)}
                                    disabled={isLoading === plan.id}
                                    className={`mt-10 block w-full rounded-md py-2 px-3 text-center text-sm font-semibold leading-6 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 ${plan.highlight
                                            ? 'bg-indigo-600 text-white shadow-sm hover:bg-indigo-500 focus-visible:outline-indigo-600'
                                            : 'bg-indigo-50 text-indigo-600 ring-1 ring-inset ring-indigo-200 hover:ring-indigo-300 focus-visible:outline-indigo-600'
                                        } disabled:opacity-50 disabled:cursor-not-allowed`}
                                >
                                    {isLoading === plan.id ? '处理中...' : '选择套餐'}
                                </button>
                            </div>

                            <ul role="list" className="mt-8 space-y-3 text-sm leading-6 text-gray-600">
                                {Object.entries(plan.features).map(([key, value]) => (
                                    <li key={key} className="flex gap-x-3">
                                        {value === true || (typeof value === 'string' && value !== '❌') ? (
                                            <CheckIcon className="h-6 w-5 flex-none text-indigo-600" aria-hidden="true" />
                                        ) : (
                                            <XMarkIcon className="h-6 w-5 flex-none text-gray-300" aria-hidden="true" />
                                        )}
                                        <span>
                                            <strong>{featureLabels[key as keyof typeof featureLabels]}:</strong>{' '}
                                            {typeof value === 'boolean' ? (value ? '支持' : '不支持') : value}
                                        </span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}
                </div>

                {/* FAQ Section */}
                <div className="mx-auto mt-24 max-w-4xl">
                    <h3 className="text-2xl font-bold text-gray-900 text-center mb-12">常见问题</h3>
                    <div className="space-y-8">
                        <div>
                            <h4 className="text-lg font-semibold text-gray-900">可以随时取消订阅吗？</h4>
                            <p className="mt-2 text-gray-600">
                                是的，您可以随时在账户设置中取消订阅。取消后您仍可使用服务直到当前计费周期结束。
                            </p>
                        </div>
                        <div>
                            <h4 className="text-lg font-semibold text-gray-900">支持哪些支付方式？</h4>
                            <p className="mt-2 text-gray-600">
                                我们支持信用卡、借记卡以及多种在线支付方式，所有支付都通过安全加密处理。
                            </p>
                        </div>
                        <div>
                            <h4 className="text-lg font-semibold text-gray-900">可以升级或降级套餐吗？</h4>
                            <p className="mt-2 text-gray-600">
                                可以。您可以随时在账户中心升级或降级套餐，费用将按比例调整。
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    )
} 