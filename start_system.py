#!/usr/bin/env python3
"""
Video2Doc 系统启动脚本
自动启动所有必要的服务
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path
from threading import Thread


class SystemManager:
    """系统管理器"""
    
    def __init__(self):
        self.processes = {}
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / "backend"
        
    def start_redis(self):
        """启动Redis服务（使用Docker）"""
        print("🔄 启动Redis服务...")
        
        try:
            # 检查是否已有Redis容器在运行
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=video2doc-redis", "--format", "{{.Names}}"],
                capture_output=True, text=True, check=True
            )
            
            if "video2doc-redis" in result.stdout:
                print("   ✅ Redis容器已在运行")
                return True
            
            # 启动Redis容器
            subprocess.run([
                "docker", "run", "-d", 
                "--name", "video2doc-redis",
                "-p", "6379:6379",
                "redis:7-alpine", 
                "redis-server", "--appendonly", "yes"
            ], check=True)
            
            print("   ✅ Redis服务启动成功")
            time.sleep(2)  # 等待Redis完全启动
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Redis启动失败: {e}")
            return False
        except FileNotFoundError:
            print("   ❌ Docker未安装或不在PATH中")
            return False
    
    def start_fastapi(self):
        """启动FastAPI应用"""
        print("🔄 启动FastAPI应用...")
        
        try:
            # 切换到backend目录
            os.chdir(self.backend_dir)
            
            # 激活虚拟环境并启动FastAPI
            if sys.platform == "win32":
                cmd = [
                    "cmd", "/c",
                    "venv\\Scripts\\activate.bat && python main.py"
                ]
            else:
                cmd = [
                    "bash", "-c", 
                    "source venv/bin/activate && python main.py"
                ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.processes['fastapi'] = process
            
            # 启动输出监控线程
            def monitor_output():
                for line in iter(process.stdout.readline, ''):
                    print(f"[FastAPI] {line.strip()}")
                    
            Thread(target=monitor_output, daemon=True).start()
            
            print("   ✅ FastAPI应用启动中...")
            time.sleep(3)  # 等待应用启动
            return True
            
        except Exception as e:
            print(f"   ❌ FastAPI启动失败: {e}")
            return False
    
    def start_celery_worker(self):
        """启动Celery Worker"""
        print("🔄 启动Celery Worker...")
        
        try:
            # 切换到backend目录
            os.chdir(self.backend_dir)
            
            # 启动Celery Worker
            if sys.platform == "win32":
                cmd = [
                    "cmd", "/c",
                    "venv\\Scripts\\activate.bat && python start_celery_worker.py"
                ]
            else:
                cmd = [
                    "bash", "-c",
                    "source venv/bin/activate && python start_celery_worker.py"
                ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.processes['celery_worker'] = process
            
            # 启动输出监控线程
            def monitor_output():
                for line in iter(process.stdout.readline, ''):
                    print(f"[Celery Worker] {line.strip()}")
                    
            Thread(target=monitor_output, daemon=True).start()
            
            print("   ✅ Celery Worker启动中...")
            time.sleep(3)  # 等待Worker启动
            return True
            
        except Exception as e:
            print(f"   ❌ Celery Worker启动失败: {e}")
            return False
    
    def start_celery_beat(self):
        """启动Celery Beat"""
        print("🔄 启动Celery Beat...")
        
        try:
            # 切换到backend目录
            os.chdir(self.backend_dir)
            
            # 启动Celery Beat
            if sys.platform == "win32":
                cmd = [
                    "cmd", "/c",
                    "venv\\Scripts\\activate.bat && python start_celery_beat.py"
                ]
            else:
                cmd = [
                    "bash", "-c",
                    "source venv/bin/activate && python start_celery_beat.py"
                ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.processes['celery_beat'] = process
            
            # 启动输出监控线程
            def monitor_output():
                for line in iter(process.stdout.readline, ''):
                    print(f"[Celery Beat] {line.strip()}")
                    
            Thread(target=monitor_output, daemon=True).start()
            
            print("   ✅ Celery Beat启动中...")
            time.sleep(2)  # 等待Beat启动
            return True
            
        except Exception as e:
            print(f"   ❌ Celery Beat启动失败: {e}")
            return False
    
    def check_services(self):
        """检查服务状态"""
        print("\n🔍 检查服务状态...")
        
        # 检查Redis
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0)
            r.ping()
            print("   ✅ Redis: 运行中")
        except Exception:
            print("   ❌ Redis: 连接失败")
        
        # 检查FastAPI
        try:
            import requests
            response = requests.get("http://localhost:8000/api/health", timeout=5)
            if response.status_code == 200:
                print("   ✅ FastAPI: 运行中")
            else:
                print(f"   ❌ FastAPI: 状态码 {response.status_code}")
        except Exception as e:
            print(f"   ❌ FastAPI: 连接失败 ({e})")
        
        # 检查队列系统
        try:
            import requests
            response = requests.get("http://localhost:8000/api/queue/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')
                workers = data.get('workers', 0)
                print(f"   ✅ 队列系统: {status} ({workers} 工作者)")
            else:
                print(f"   ❌ 队列系统: 状态码 {response.status_code}")
        except Exception as e:
            print(f"   ❌ 队列系统: 连接失败 ({e})")
    
    def shutdown(self):
        """关闭所有服务"""
        print("\n🛑 关闭服务...")
        
        # 关闭Python进程
        for name, process in self.processes.items():
            try:
                print(f"   关闭 {name}...")
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                print(f"   关闭 {name} 失败: {e}")
        
        # 关闭Redis容器
        try:
            subprocess.run(
                ["docker", "stop", "video2doc-redis"], 
                check=True, 
                capture_output=True
            )
            subprocess.run(
                ["docker", "rm", "video2doc-redis"], 
                check=True, 
                capture_output=True
            )
            print("   ✅ Redis容器已关闭")
        except Exception:
            pass
        
        print("   ✅ 所有服务已关闭")
    
    def start_all(self):
        """启动所有服务"""
        print("🚀 启动Video2Doc系统")
        print("=" * 50)
        
        # 1. 启动Redis
        if not self.start_redis():
            print("❌ 系统启动失败：Redis启动失败")
            return False
        
        # 2. 启动FastAPI
        if not self.start_fastapi():
            print("❌ 系统启动失败：FastAPI启动失败")
            return False
        
        # 3. 启动Celery Worker
        if not self.start_celery_worker():
            print("❌ 系统启动失败：Celery Worker启动失败")
            return False
        
        # 4. 启动Celery Beat（可选）
        self.start_celery_beat()
        
        # 5. 检查服务状态
        time.sleep(5)  # 等待所有服务完全启动
        self.check_services()
        
        print("\n🎉 系统启动完成！")
        print("=" * 50)
        print("📍 服务地址:")
        print("   FastAPI文档: http://localhost:8000/docs")
        print("   API健康检查: http://localhost:8000/api/health")
        print("   队列管理: http://localhost:8000/api/queue/health")
        print("\n按 Ctrl+C 退出")
        
        return True


def signal_handler(signum, frame):
    """信号处理器"""
    print("\n收到退出信号...")
    if 'manager' in globals():
        manager.shutdown()
    sys.exit(0)


def main():
    """主函数"""
    global manager
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    manager = SystemManager()
    
    try:
        if manager.start_all():
            # 保持运行状态
            while True:
                time.sleep(1)
        else:
            print("系统启动失败")
            return 1
            
    except KeyboardInterrupt:
        pass
    finally:
        manager.shutdown()
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 