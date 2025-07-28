#!/usr/bin/env python
"""
运行所有测试脚本
"""

import os
import sys
import subprocess
import time

# 颜色常量
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_color(text, color):
    """打印彩色文本"""
    print(f"{color}{text}{RESET}")

def run_test(test_script):
    """运行测试脚本并返回结果"""
    print_color(f"\n{'='*50}", BLUE)
    print_color(f"运行测试: {test_script}", BLUE)
    print_color(f"{'='*50}", BLUE)
    
    start_time = time.time()
    result = subprocess.run([sys.executable, test_script], capture_output=True, text=True)
    end_time = time.time()
    
    # 打印输出
    print(result.stdout)
    if result.stderr:
        print_color(f"错误输出:", RED)
        print(result.stderr)
    
    duration = end_time - start_time
    success = result.returncode == 0
    
    if success:
        print_color(f"✅ {os.path.basename(test_script)} 通过 ({duration:.2f}秒)", GREEN)
    else:
        print_color(f"❌ {os.path.basename(test_script)} 失败 ({duration:.2f}秒)", RED)
    
    return success

def main():
    """主函数"""
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 测试脚本列表
    test_scripts = [
        os.path.join(current_dir, "test_api.py"),
        os.path.join(current_dir, "test_speech.py"),
        os.path.join(current_dir, "test_speech_detailed.py"),
        os.path.join(current_dir, "test_video_upload.py")
    ]
    
    print_color(f"{'='*50}", BLUE)
    print_color("Video2Doc 测试套件", BLUE)
    print_color(f"{'='*50}", BLUE)
    
    # 运行测试
    results = []
    for script in test_scripts:
        if os.path.exists(script):
            success = run_test(script)
            results.append((os.path.basename(script), success))
        else:
            print_color(f"⚠️ 测试脚本不存在: {script}", YELLOW)
            results.append((os.path.basename(script), None))
    
    # 打印摘要
    print_color(f"\n{'='*50}", BLUE)
    print_color("测试结果摘要:", BLUE)
    print_color(f"{'='*50}", BLUE)
    
    passed = 0
    failed = 0
    skipped = 0
    
    for name, result in results:
        if result is True:
            status = f"{GREEN}✅ 通过{RESET}"
            passed += 1
        elif result is False:
            status = f"{RED}❌ 失败{RESET}"
            failed += 1
        else:
            status = f"{YELLOW}⚠️ 跳过{RESET}"
            skipped += 1
        
        print(f"{name}: {status}")
    
    print_color(f"\n{'='*50}", BLUE)
    print_color(f"测试完成: {passed} 通过, {failed} 失败, {skipped} 跳过", BLUE)
    print_color(f"{'='*50}", BLUE)
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 