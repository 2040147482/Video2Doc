export default function Footer() {
    return (
        <footer className="bg-gray-800 text-white">
            <div className="container mx-auto px-4 py-8">
                <div className="grid md:grid-cols-4 gap-8">
                    <div>
                        <h3 className="text-lg font-semibold mb-4">Video2Doc</h3>
                        <p className="text-gray-300 text-sm">
                            AI驱动的视频内容分析工具，让视频信息获取更高效
                        </p>
                    </div>

                    <div>
                        <h4 className="text-md font-semibold mb-4">产品功能</h4>
                        <ul className="space-y-2 text-sm">
                            <li><a href="#" className="text-gray-300 hover:text-white">语音识别</a></li>
                            <li><a href="#" className="text-gray-300 hover:text-white">图像识别</a></li>
                            <li><a href="#" className="text-gray-300 hover:text-white">智能摘要</a></li>
                            <li><a href="#" className="text-gray-300 hover:text-white">多格式导出</a></li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="text-md font-semibold mb-4">支持格式</h4>
                        <ul className="space-y-2 text-sm">
                            <li><span className="text-gray-300">Markdown</span></li>
                            <li><span className="text-gray-300">PDF</span></li>
                            <li><span className="text-gray-300">HTML</span></li>
                            <li><span className="text-gray-300">纯文本</span></li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="text-md font-semibold mb-4">联系我们</h4>
                        <ul className="space-y-2 text-sm">
                            <li><a href="#" className="text-gray-300 hover:text-white">技术支持</a></li>
                            <li><a href="#" className="text-gray-300 hover:text-white">用户反馈</a></li>
                            <li><a href="#" className="text-gray-300 hover:text-white">合作咨询</a></li>
                        </ul>
                    </div>
                </div>

                <div className="border-t border-gray-700 mt-8 pt-8 text-center">
                    <p className="text-gray-400 text-sm">
                        © 2024 Video2Doc. All rights reserved.
                    </p>
                </div>
            </div>
        </footer>
    )
} 