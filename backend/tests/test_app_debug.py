"""
调试应用实例和路由
"""
import sys
import traceback

def test_app_creation():
    """测试应用创建"""
    print("=== 测试应用创建 ===")
    try:
        from main import app
        print("✅ 应用创建成功")
        print(f"应用类型: {type(app)}")
        return app
    except Exception as e:
        print(f"❌ 应用创建失败: {e}")
        traceback.print_exc()
        return None

def test_routes(app):
    """测试路由"""
    print("\n=== 测试路由 ===")
    try:
        routes = app.routes
        print(f"路由总数: {len(routes)}")
        
        for route in routes:
            route_info = getattr(route, 'path', 'Unknown path')
            route_methods = getattr(route, 'methods', set())
            print(f"  - {route_info} [{', '.join(route_methods)}]")
        
        # 查找我们的超级简化路由
        ultra_simple_routes = [r for r in routes if hasattr(r, 'path') and 'speech-ultra-simple' in r.path]
        print(f"\n超级简化路由数量: {len(ultra_simple_routes)}")
        for route in ultra_simple_routes:
            print(f"  - {route.path}")
        
        return True
    except Exception as e:
        print(f"❌ 路由测试失败: {e}")
        traceback.print_exc()
        return False

def test_ultra_simple_import():
    """测试超级简化路由导入"""
    print("\n=== 测试超级简化路由导入 ===")
    try:
        from app.routers.speech_ultra_simple import router
        print("✅ 超级简化路由导入成功")
        print(f"路由类型: {type(router)}")
        print(f"路由前缀: {router.prefix}")
        print(f"路由标签: {router.tags}")
        
        # 检查路由定义
        routes = router.routes
        print(f"路由端点数量: {len(routes)}")
        for route in routes:
            print(f"  - {route.path} [{', '.join(route.methods)}]")
        
        return True
    except Exception as e:
        print(f"❌ 超级简化路由导入失败: {e}")
        traceback.print_exc()
        return False

def test_dependencies():
    """测试依赖项"""
    print("\n=== 测试依赖项 ===")
    dependencies = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "python-multipart"
    ]
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError as e:
            print(f"❌ {dep}: {e}")

def main():
    """主函数"""
    print("开始应用调试...")
    
    # 测试依赖项
    test_dependencies()
    
    # 测试超级简化路由导入
    if not test_ultra_simple_import():
        print("停止调试：超级简化路由导入失败")
        return
    
    # 测试应用创建
    app = test_app_creation()
    if not app:
        print("停止调试：应用创建失败")
        return
    
    # 测试路由
    test_routes(app)
    
    print("\n调试完成！")

if __name__ == "__main__":
    main() 