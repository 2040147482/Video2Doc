"""
测试文件结构验证脚本
"""

import os
import sys
from pathlib import Path

def test_file_structure():
    """验证测试文件结构"""
    current_dir = Path(__file__).parent
    
    print("=== 验证测试文件结构 ===")
    
    # 预期的文件分类
    expected_files = {
        "导出功能测试": [
            "test_export.py",
            "test_export_quick.py"
        ],
        "摘要功能测试": [
            "test_summary.py",
            "test_simple_summary.py", 
            "test_complete_summary.py",
            "test_direct_summary.py",
            "test_summary_simple.py",
            "test_summary_debug.py"
        ],
        "语音识别测试": [
            "test_speech.py",
            "test_speech_detailed.py",
            "test_simple_speech.py",
            "test_speech_ultra_simple.py",
            "test_speech_debug.py"
        ],
        "图像识别测试": [
            "test_image_recognition.py",
            "test_direct_image.py",
            "test_simple_image.py",
            "test_image_debug.py"
        ],
        "视频上传测试": [
            "test_video_upload.py"
        ],
        "API集成测试": [
            "test_api.py"
        ],
        "调试测试": [
            "test_app_debug.py",
            "test_debug_with_logs.py",
            "test_simple_debug.py"
        ],
        "测试工具": [
            "run_all_tests.py",
            "README.md",
            "__init__.py"
        ]
    }
    
    all_good = True
    total_files = 0
    found_files = 0
    
    for category, files in expected_files.items():
        print(f"\n{category}:")
        for file_name in files:
            file_path = current_dir / file_name
            if file_path.exists():
                print(f"  ✅ {file_name}")
                found_files += 1
            else:
                print(f"  ❌ {file_name} (缺失)")
                all_good = False
            total_files += 1
    
    # 检查测试资源目录
    print(f"\n测试资源:")
    test_assets_dir = current_dir / "test_assets"
    if test_assets_dir.exists() and test_assets_dir.is_dir():
        print(f"  ✅ test_assets/ 目录存在")
        
        # 检查测试资源文件
        assets = list(test_assets_dir.glob("*"))
        if assets:
            print(f"  📁 包含 {len(assets)} 个资源文件:")
            for asset in assets:
                print(f"    - {asset.name}")
        else:
            print(f"  ⚠️ test_assets/ 目录为空")
    else:
        print(f"  ❌ test_assets/ 目录缺失")
        all_good = False
    
    # 统计结果
    print(f"\n=== 结构验证结果 ===")
    print(f"总文件数: {total_files}")
    print(f"找到文件: {found_files}")
    print(f"缺失文件: {total_files - found_files}")
    
    if all_good:
        print("✅ 测试文件结构验证通过!")
        return True
    else:
        print("❌ 测试文件结构有问题!")
        return False

def list_all_test_files():
    """列出所有测试文件"""
    current_dir = Path(__file__).parent
    
    print(f"\n=== 当前tests目录所有文件 ===")
    
    # 获取所有Python测试文件
    test_files = sorted(current_dir.glob("test_*.py"))
    other_files = [f for f in current_dir.iterdir() if f.is_file() and not f.name.startswith("test_")]
    
    print(f"测试文件 ({len(test_files)} 个):")
    for file in test_files:
        size = file.stat().st_size
        print(f"  📄 {file.name} ({size/1024:.1f}KB)")
    
    print(f"\n其他文件 ({len(other_files)} 个):")
    for file in other_files:
        size = file.stat().st_size  
        print(f"  📄 {file.name} ({size/1024:.1f}KB)")
    
    # 检查子目录
    subdirs = [d for d in current_dir.iterdir() if d.is_dir()]
    if subdirs:
        print(f"\n子目录 ({len(subdirs)} 个):")
        for subdir in subdirs:
            contents = list(subdir.iterdir())
            print(f"  📁 {subdir.name}/ ({len(contents)} 个文件)")

if __name__ == "__main__":
    print("🔍 Video2Doc 测试文件结构验证")
    print("=" * 50)
    
    # 验证文件结构
    structure_ok = test_file_structure()
    
    # 列出所有文件
    list_all_test_files()
    
    print(f"\n{'=' * 50}")
    if structure_ok:
        print("🎉 测试文件组织完成!")
    else:
        print("⚠️ 请检查缺失的测试文件")
    
    sys.exit(0 if structure_ok else 1) 