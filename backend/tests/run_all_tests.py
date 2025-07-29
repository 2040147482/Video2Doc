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
            print_color(f"✅ {script_name} 通过 ({duration:.2f}秒)", GREEN)
        else:
            print_color(f"❌ {script_name} 失败 (返回码: {result.returncode}, {duration:.2f}秒)", RED)
        
        return success, duration
        
    except subprocess.TimeoutExpired:
        print_color(f"⏰ {script_name} 超时 ({timeout}秒)", YELLOW)
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
    
    for category, scripts in test_categories.items():
        print_color(f"\n{'='*60}", BLUE)
        print_color(f"{category}", BLUE)
        print_color(f"{'='*60}", BLUE)
        
        category_results = []
        for script_name in scripts:
            script_path = os.path.join(current_dir, script_name)
            if os.path.exists(script_path):
                success, duration = run_test(script_path)
                category_results.append((script_name, success, duration))
                total_duration += duration
            else:
                print_color(f"⚠️ 测试脚本不存在: {script_name}", YELLOW)
                category_results.append((script_name, None, 0))
        
        all_results.extend(category_results)
    
    # 询问是否运行调试测试
    print_color(f"\n{'='*60}", YELLOW)
    print_color("🐛 调试测试 (可选)", YELLOW)
    print_color(f"{'='*60}", YELLOW)
    
    try:
        run_debug = input("是否运行调试测试? (y/N): ").lower() == 'y'
        if run_debug:
            for script_name in debug_tests:
                script_path = os.path.join(current_dir, script_name)
                if os.path.exists(script_path):
                    success, duration = run_test(script_path)
                    all_results.append((script_name, success, duration))
                    total_duration += duration
    except (KeyboardInterrupt, EOFError):
        print_color("\n跳过调试测试", YELLOW)
    
    # 打印详细摘要
    print_color(f"\n{'='*60}", CYAN)
    print_color("📊 测试结果详细摘要", CYAN)
    print_color(f"{'='*60}", CYAN)
    
    passed = 0
    failed = 0
    skipped = 0
    
    # 按类别显示结果
    for category, scripts in test_categories.items():
        print_color(f"\n{category}:", BLUE)
        for script_name in scripts:
            result_item = next((item for item in all_results if item[0] == script_name), None)
            if result_item:
                name, result, duration = result_item
                if result is True:
                    status = f"{GREEN}✅ 通过{RESET} ({duration:.2f}s)"
                    passed += 1
                elif result is False:
                    status = f"{RED}❌ 失败{RESET} ({duration:.2f}s)"
                    failed += 1
                else:
                    status = f"{YELLOW}⚠️ 跳过{RESET}"
                    skipped += 1
                print(f"  {name}: {status}")
    
    # 总体统计
    print_color(f"\n{'='*60}", CYAN)
    print_color(f"🎯 总体结果:", CYAN)
    print_color(f"总测试数: {len(all_results)}", CYAN)
    print_color(f"通过: {passed} | 失败: {failed} | 跳过: {skipped}", CYAN)
    print_color(f"总耗时: {total_duration:.2f}秒", CYAN)
    
    if failed == 0 and passed > 0:
        print_color(f"🎉 所有测试通过!", GREEN)
    elif failed > 0:
        print_color(f"⚠️ 有 {failed} 个测试失败", RED)
    else:
        print_color(f"⚠️ 没有成功运行的测试", YELLOW)
    
    print_color(f"{'='*60}", CYAN)
    
    return failed == 0 and passed > 0

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_color("\n\n测试被用户中断", YELLOW)
        sys.exit(130) 