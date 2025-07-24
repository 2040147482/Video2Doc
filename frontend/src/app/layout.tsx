import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
    title: 'Video2Doc - 视频内容AI分析工具',
    description: '一个在线AI工具平台，用户上传视频或粘贴视频链接后，AI自动识别视频中的语音与图像内容，并将其结构化生成为可编辑、可导出的文档格式',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="zh">
            <body className={inter.className}>
                <div className="min-h-screen bg-gray-50">
                    {children}
                </div>
            </body>
        </html>
    )
} 