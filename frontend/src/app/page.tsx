import Header from '@/components/Header'
import Footer from '@/components/Footer'
import VideoUpload from '@/components/VideoUpload'
import Link from 'next/link'
import { CheckIcon } from '@heroicons/react/24/outline'

export default function Home() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
            <Header />

            <main className="container mx-auto px-4 py-8">
                {/* 产品介绍 */}
                <div className="text-center mb-12">
                    <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
                        AI 视频内容
                        <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                            智能分析
                        </span>
                    </h1>
                    <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
                        上传视频或提供视频链接，AI 自动识别语音与图像内容，
                        生成结构化文档，支持 Markdown、PDF、HTML 等多种格式导出
                    </p>

                    {/* 功能特点 */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto mb-12">
                        <div className="bg-white rounded-lg p-6 shadow-md">
                            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2h4a1 1 0 011 1v1a1 1 0 01-1 1h-1v10a2 2 0 01-2 2H6a2 2 0 01-2-2V7H3a1 1 0 01-1-1V5a1 1 0 011-1h4z" />
                                </svg>
                            </div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">智能语音识别</h3>
                            <p className="text-gray-600 text-sm">
                                支持多语言语音转文字，自动添加时间戳，按段落智能分割
                            </p>
                        </div>

                        <div className="bg-white rounded-lg p-6 shadow-md">
                            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                </svg>
                            </div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">图像内容分析</h3>
                            <p className="text-gray-600 text-sm">
                                提取关键帧，OCR文字识别，图文内容智能匹配
                            </p>
                        </div>

                        <div className="bg-white rounded-lg p-6 shadow-md">
                            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                </svg>
                            </div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">多格式导出</h3>
                            <p className="text-gray-600 text-sm">
                                支持 Markdown、PDF、HTML、TXT 等格式，一键批量导出
                            </p>
                        </div>
                    </div>
                </div>

                {/* 免费试用横幅 */}
                <div className="mb-12 max-w-4xl mx-auto">
                    <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-8 text-center text-white">
                        <h2 className="text-2xl font-bold mb-2">🎁 免费试用</h2>
                        <p className="text-indigo-100 mb-6">注册即可获得 3 次免费视频分析机会，无需付费</p>
                        <div className="flex flex-col sm:flex-row gap-4 justify-center">
                            <Link
                                href="/register"
                                className="bg-white text-indigo-600 font-semibold px-8 py-3 rounded-lg hover:bg-indigo-50 transition-colors"
                            >
                                立即免费试用
                            </Link>
                            <Link
                                href="/pricing"
                                className="border-2 border-white text-white font-semibold px-8 py-3 rounded-lg hover:bg-white hover:text-indigo-600 transition-colors"
                            >
                                查看定价方案
                            </Link>
                        </div>
                    </div>
                </div>

                {/* 上传组件 */}
                <VideoUpload />

                {/* 使用说明 */}
                <div className="mt-16 max-w-4xl mx-auto">
                    <h2 className="text-2xl font-bold text-gray-900 text-center mb-8">
                        如何使用
                    </h2>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        <div className="text-center">
                            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                <span className="text-2xl font-bold text-blue-600">1</span>
                            </div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">上传视频</h3>
                            <p className="text-gray-600">
                                支持本地文件上传或粘贴视频链接，
                                兼容主流视频平台和格式
                            </p>
                        </div>

                        <div className="text-center">
                            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                <span className="text-2xl font-bold text-green-600">2</span>
                            </div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">AI 分析</h3>
                            <p className="text-gray-600">
                                自动识别语音内容，提取关键图像，
                                生成结构化摘要和章节
                            </p>
                        </div>

                        <div className="text-center">
                            <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                <span className="text-2xl font-bold text-purple-600">3</span>
                            </div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">导出文档</h3>
                            <p className="text-gray-600">
                                选择所需格式，一键下载整理好的
                                文档，支持在线预览和编辑
                            </p>
                        </div>
                    </div>
                </div>

                {/* 支持的平台 */}
                <div className="mt-16 bg-white rounded-xl shadow-lg p-8 max-w-4xl mx-auto">
                    <h2 className="text-2xl font-bold text-gray-900 text-center mb-8">
                        支持的平台和格式
                    </h2>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                                <svg className="w-5 h-5 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                                </svg>
                                视频平台
                            </h3>
                            <ul className="space-y-2">
                                <li className="flex items-center text-gray-600">
                                    <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
                                    YouTube (youtube.com, youtu.be)
                                </li>
                                <li className="flex items-center text-gray-600">
                                    <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
                                    哔哩哔哩 (bilibili.com, b23.tv)
                                </li>
                                <li className="flex items-center text-gray-600">
                                    <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
                                    Vimeo (vimeo.com)
                                </li>
                                <li className="flex items-center text-gray-600">
                                    <div className="w-2 h-2 bg-gray-400 rounded-full mr-3"></div>
                                    更多平台持续添加...
                                </li>
                            </ul>
                        </div>

                        <div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                                <svg className="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                </svg>
                                文件格式
                            </h3>
                            <div className="space-y-3">
                                <div>
                                    <p className="text-sm font-medium text-gray-700 mb-1">视频格式</p>
                                    <p className="text-gray-600 text-sm">MP4、MOV、AVI、MKV、WEBM、FLV、WMV</p>
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-gray-700 mb-1">输出格式</p>
                                    <p className="text-gray-600 text-sm">Markdown、PDF、HTML、TXT、ZIP 打包</p>
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-gray-700 mb-1">文件大小</p>
                                    <p className="text-gray-600 text-sm">最大支持 2GB 视频文件</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* 定价预览 */}
                <div className="mt-16 max-w-6xl mx-auto">
                    <div className="text-center mb-12">
                        <h2 className="text-3xl font-bold text-gray-900 mb-4">选择适合你的套餐</h2>
                        <p className="text-lg text-gray-600">从个人使用到专业需求，灵活的定价方案</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        {/* 入门版 */}
                        <div className="bg-white rounded-2xl p-8 shadow-lg border">
                            <div className="text-center">
                                <h3 className="text-xl font-semibold text-gray-900 mb-2">入门版</h3>
                                <p className="text-gray-600 mb-6">适合个人用户的基础需求</p>
                                <div className="mb-6">
                                    <span className="text-4xl font-bold text-gray-900">$4.99</span>
                                    <span className="text-gray-600">/月</span>
                                </div>
                            </div>
                            <ul className="space-y-3 mb-8">
                                <li className="flex items-center text-sm">
                                    <CheckIcon className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                                    <span>10分钟视频时长上限</span>
                                </li>
                                <li className="flex items-center text-sm">
                                    <CheckIcon className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                                    <span>本地文件上传</span>
                                </li>
                                <li className="flex items-center text-sm">
                                    <CheckIcon className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                                    <span>基础AI笔记生成</span>
                                </li>
                                <li className="flex items-center text-sm">
                                    <CheckIcon className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                                    <span>Markdown格式导出</span>
                                </li>
                                <li className="flex items-center text-sm">
                                    <CheckIcon className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                                    <span>5篇历史记录</span>
                                </li>
                            </ul>
                            <Link
                                href="/pricing"
                                className="block w-full bg-gray-900 text-white text-center py-3 rounded-lg font-semibold hover:bg-gray-800 transition-colors"
                            >
                                选择入门版
                            </Link>
                        </div>

                        {/* 标准版 */}
                        <div className="bg-white rounded-2xl p-8 shadow-xl border-2 border-indigo-600 relative">
                            <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                                <span className="bg-indigo-600 text-white px-4 py-1 rounded-full text-sm font-medium">
                                    最受欢迎
                                </span>
                            </div>
                            <div className="text-center">
                                <h3 className="text-xl font-semibold text-gray-900 mb-2">标准版</h3>
                                <p className="text-gray-600 mb-6">功能全面的热门选择</p>
                                <div className="mb-6">
                                    <span className="text-4xl font-bold text-gray-900">$9.99</span>
                                    <span className="text-gray-600">/月</span>
                                </div>
                            </div>
                            <ul className="space-y-3 mb-8">
                                <li className="flex items-center text-sm">
                                    <CheckIcon className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                                    <span>30分钟视频时长上限</span>
                                </li>
                                <li className="flex items-center text-sm">
                                    <CheckIcon className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                                    <span>本地上传 + 链接导入</span>
                                </li>
                                <li className="flex items-center text-sm">
                                    <CheckIcon className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                                    <span>精准AI语义摘要</span>
                                </li>
                                <li className="flex items-center text-sm">
                                    <CheckIcon className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                                    <span>1张关键帧图像提取</span>
                                </li>
                                <li className="flex items-center text-sm">
                                    <CheckIcon className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                                    <span>Markdown + PDF导出</span>
                                </li>
                                <li className="flex items-center text-sm">
                                    <CheckIcon className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                                    <span>30篇历史记录</span>
                                </li>
                            </ul>
                            <Link
                                href="/pricing"
                                className="block w-full bg-indigo-600 text-white text-center py-3 rounded-lg font-semibold hover:bg-indigo-700 transition-colors"
                            >
                                选择标准版
                            </Link>
                        </div>

                        {/* 高级版 */}
                        <div className="bg-white rounded-2xl p-8 shadow-lg border">
                            <div className="text-center">
                                <h3 className="text-xl font-semibold text-gray-900 mb-2">高级版</h3>
                                <p className="text-gray-600 mb-6">专业用户的完整解决方案</p>
                                <div className="mb-6">
                                    <span className="text-4xl font-bold text-gray-900">$19.99</span>
                                    <span className="text-gray-600">/月</span>
                                </div>
                            </div>
                            <ul className="space-y-3 mb-8">
                                <li className="flex items-center text-sm">
                                    <CheckIcon className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                                    <span>90分钟视频时长上限</span>
                                </li>
                                <li className="flex items-center text-sm">
                                    <CheckIcon className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                                    <span>全平台导入支持</span>
                                </li>
                                <li className="flex items-center text-sm">
                                    <CheckIcon className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                                    <span>多风格智能笔记</span>
                                </li>
                                <li className="flex items-center text-sm">
                                    <CheckIcon className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                                    <span>3-5张关键帧提取</span>
                                </li>
                                <li className="flex items-center text-sm">
                                    <CheckIcon className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                                    <span>全格式导出 + Notion</span>
                                </li>
                                <li className="flex items-center text-sm">
                                    <CheckIcon className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                                    <span>无限历史记录</span>
                                </li>
                            </ul>
                            <Link
                                href="/pricing"
                                className="block w-full bg-gray-900 text-white text-center py-3 rounded-lg font-semibold hover:bg-gray-800 transition-colors"
                            >
                                选择高级版
                            </Link>
                        </div>
                    </div>

                    <div className="text-center mt-8">
                        <Link
                            href="/pricing"
                            className="inline-flex items-center text-indigo-600 font-semibold hover:text-indigo-700"
                        >
                            查看完整定价详情
                            <svg className="ml-1 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                            </svg>
                        </Link>
                    </div>
                </div>
            </main>

            <Footer />
        </div>
    )
} 