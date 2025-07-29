#!/usr/bin/env python
"""
运行所有测试脚本 - Video2Doc 测试套件
"""

import os
import sys
import subprocess
import time
from collections import OrderedDict

# 颜色常量
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'

def print_color(text, color):
    """打印彩色文本"""
    print(f"{color}{text}{RESET}")

def run_test(test_script, timeout=120):
    """运行测试脚本并返回结果"""
    script_name = os.path.basename(test_script)
    print_color(f"\n{'='*60}", BLUE)
    print_color(f"运行测试: {script_name}", BLUE)
    print_color(f"{'='*60}", BLUE)
    
    start_time = time.time()
    try:
        result = subprocess.run(
            [sys.executable, test_script], 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        end_time = time.time()
        
        # 打印输出
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print_color(f"错误输出:", RED)
            print(result.stderr)
        
        duration = end_time - start_time
        success = result.returncode == 0
        
        if success:
            print_color(f"✅ {script_name} 测试通过 ({duration:.1f}s)", GREEN)
        else:
            print_color(f"❌ {script_name} 测试失败 ({duration:.1f}s)", RED)
        
        return success, duration
        
    except subprocess.TimeoutExpired:
        print_color(f"⏰ {script_name} 测试超时 ({timeout}s)", YELLOW)
        return False, timeout
    except Exception as e:
        print_color(f"💥 {script_name} 执行异常: {str(e)}", RED)
        return False, 0

def main():
    """主函数"""
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 按功能模块组织的测试脚本
    test_categories = OrderedDict([
        ("🔄 导出功能测试", [
            "test_export_quick.py",
            "test_export.py"
        ]),
        ("📝 摘要功能测试", [
            "test_summary_simple.py", 
            "test_summary.py",
            "test_simple_summary.py",
            "test_complete_summary.py",
            "test_direct_summary.py"
        ]),
        ("🎤 语音识别测试", [
            "test_speech_ultra_simple.py",
            "test_simple_speech.py",
            "test_speech.py",
            "test_speech_detailed.py"
        ]),
        ("🖼️ 图像识别测试", [
            "test_direct_image.py",
            "test_simple_image.py", 
            "test_image_recognition.py"
        ]),
        ("📤 视频上传测试", [
            "test_video_upload.py"
        ]),
        ("☁️ 云存储测试", [
            "test_simple_storage.py",
            "test_cloud_storage.py",
            "test_storage_api.py"
        ]),
        ("🔄 任务队列测试", [
            "test_queue_simple.py",
            "test_queue_system.py"
        ]),
        ("🌐 API集成测试", [
            "test_api.py"
        ])
    ])
    
    # 调试测试（默认跳过）
    debug_tests = [
        "test_app_debug.py",
        "test_debug_with_logs.py", 
        "test_simple_debug.py",
        "test_summary_debug.py",
        "test_image_debug.py",
        "test_speech_debug.py"
    ]
    
    print_color(f"{'='*60}", CYAN)
    print_color("🚀 Video2Doc 测试套件", CYAN)
    print_color(f"{'='*60}", CYAN)
    print_color("测试分类组织 - 按功能模块运行", CYAN)
    
    # 运行测试
    all_results = []
    total_duration = 0
    
    for category, test_files in test_categories.items():
        print_color(f"\n📋 {category}", CYAN)
        print_color("-" * 60, CYAN)
        
        category_results = []
        for test_file in test_files:
            test_path = os.path.join(current_dir, test_file)
            if os.path.exists(test_path):
                success, duration = run_test(test_path)
                category_results.append((test_file, success, duration))
                total_duration += duration
            else:
                print_color(f"⚠️  测试文件不存在: {test_file}", YELLOW)
                category_results.append((test_file, False, 0))
        
        all_results.extend(category_results)
        
        # 分类汇总
        passed = sum(1 for _, success, _ in category_results if success)
        total = len(category_results)
        print_color(f"\n{category} 汇总: {passed}/{total} 通过", 
                   GREEN if passed == total else YELLOW)
    
    # 总体汇总
    print_color(f"\n{'='*60}", CYAN)
    print_color("📊 总体测试结果汇总", CYAN)
    print_color(f"{'='*60}", CYAN)
    
    total_tests = len(all_results)
    passed_tests = sum(1 for _, success, _ in all_results if success)
    
    print_color(f"总测试数: {total_tests}", BLUE)
    print_color(f"通过测试: {passed_tests}", GREEN)
    print_color(f"失败测试: {total_tests - passed_tests}", RED)
    print_color(f"成功率: {(passed_tests/total_tests)*100:.1f}%", 
               GREEN if passed_tests == total_tests else YELLOW)
    print_color(f"总耗时: {total_duration:.1f}s", BLUE)
    
    # 详细结果
    print_color(f"\n📝 详细结果:", BLUE)
    for test_file, success, duration in all_results:
        status_icon = "✅" if success else "❌"
        status_color = GREEN if success else RED
        print_color(f"  {status_icon} {test_file:<30} ({duration:.1f}s)", status_color)
    
    # 失败测试列表
    failed_tests = [test_file for test_file, success, _ in all_results if not success]
    if failed_tests:
        print_color(f"\n❌ 失败的测试:", RED)
        for test_file in failed_tests:
            print_color(f"  - {test_file}", RED)
        
        print_color(f"\n💡 建议:", YELLOW)
        print_color("  1. 检查服务是否正常运行 (FastAPI, Redis等)", YELLOW)
        print_color("  2. 确认测试环境配置正确", YELLOW)  
        print_color("  3. 查看具体错误日志进行调试", YELLOW)
    else:
        print_color(f"\n🎉 所有测试通过！", GREEN)
    
    # 询问是否运行调试测试
    if debug_tests:
        print_color(f"\n🐛 调试测试 (默认跳过):", YELLOW)
        for debug_test in debug_tests:
            print_color(f"  - {debug_test}", YELLOW)
        
        run_debug = input(f"\n是否运行调试测试? (y/N): ").lower().strip()
        if run_debug in ['y', 'yes']:
            print_color(f"\n🔧 运行调试测试:", CYAN)
            for debug_test in debug_tests:
                debug_path = os.path.join(current_dir, debug_test)
                if os.path.exists(debug_path):
                    run_test(debug_path)

    return 0 if passed_tests == total_tests else 1

if __name__ == "__main__":
    sys.exit(main()) 