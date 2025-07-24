'use client'

export function Header() {
    return (
        <header className="bg-white shadow-sm border-b">
            <div className="container mx-auto px-4 py-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                        <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                            </svg>
                        </div>
                        <div>
                            <h1 className="text-xl font-bold text-gray-900">Video2Doc</h1>
                            <p className="text-sm text-gray-500">视频内容AI分析工具</p>
                        </div>
                    </div>

                    <nav className="hidden md:flex items-center space-x-6">
                        <a href="#features" className="text-gray-600 hover:text-gray-900 transition-colors">
                            功能特点
                        </a>
                        <a href="#about" className="text-gray-600 hover:text-gray-900 transition-colors">
                            关于我们
                        </a>
                        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                            开始使用
                        </button>
                    </nav>
                </div>
            </div>
        </header>
    )
} 