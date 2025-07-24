import { VideoUpload } from '@/components/VideoUpload'
import { Header } from '@/components/Header'
import { Footer } from '@/components/Footer'

export default function Home() {
    return (
        <main className="min-h-screen flex flex-col">
            <Header />

            <div className="flex-1 container mx-auto px-4 py-8">
                <div className="max-w-4xl mx-auto">
                    {/* 页面标题 */}
                    <div className="text-center mb-12">
                        <h1 className="text-4xl font-bold text-gray-900 mb-4">
                            Video2Doc
                        </h1>
                        <p className="text-xl text-gray-600 mb-8">
                            AI 视频内容分析工具
                        </p>
                        <p className="text-gray-500 max-w-2xl mx-auto">
                            上传视频或粘贴视频链接，AI 自动识别语音与图像内容，
                            生成结构化文档，支持 Markdown、PDF、HTML 等格式导出
                        </p>
                    </div>

                    {/* 视频上传组件 */}
                    <VideoUpload />

                    {/* 功能特点 */}
                    <div className="mt-16 grid md:grid-cols-3 gap-8">
                        <div className="text-center p-6 bg-white rounded-lg shadow-sm">
                            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                </svg>
                            </div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">智能识别</h3>
                            <p className="text-gray-600">支持语音转文字、图像OCR识别，自动提取视频中的所有内容</p>
                        </div>

                        <div className="text-center p-6 bg-white rounded-lg shadow-sm">
                            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                </svg>
                            </div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">结构化整理</h3>
                            <p className="text-gray-600">AI 自动生成摘要、章节划分，形成条理清晰的文档结构</p>
                        </div>

                        <div className="text-center p-6 bg-white rounded-lg shadow-sm">
                            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                </svg>
                            </div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">多格式导出</h3>
                            <p className="text-gray-600">支持 Markdown、PDF、HTML 等多种格式，适配各种笔记工具</p>
                        </div>
                    </div>
                </div>
            </div>

            <Footer />
        </main>
    )
} 