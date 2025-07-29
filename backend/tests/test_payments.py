"""
支付功能测试脚本
测试Creem支付集成
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import httpx
import json
from datetime import datetime


async def test_payment_endpoints():
    """测试支付相关的API端点"""
    
    base_url = "http://localhost:8000/api"
    
    print("🔄 开始测试支付功能...")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    async with httpx.AsyncClient() as client:
        
        # 1. 测试支付服务健康检查
        print("1️⃣ 测试支付服务健康检查...")
        try:
            response = await client.get(f"{base_url}/payments/health")
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   服务状态: {data['status']}")
                print(f"   可用套餐数: {data['plans_available']}")
                print("   ✅ 支付服务健康检查通过")
            else:
                print(f"   ❌ 健康检查失败: {response.text}")
        except Exception as e:
            print(f"   ❌ 健康检查异常: {str(e)}")
        print()
        
        # 2. 测试获取套餐列表
        print("2️⃣ 测试获取套餐列表...")
        try:
            response = await client.get(f"{base_url}/payments/plans")
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                plans = response.json()
                print(f"   套餐数量: {len(plans)}")
                for plan in plans:
                    print(f"   - {plan['name']}: ${plan['monthly_price']}/月, ${plan['yearly_price']}/年")
                print("   ✅ 套餐列表获取成功")
            else:
                print(f"   ❌ 获取套餐列表失败: {response.text}")
        except Exception as e:
            print(f"   ❌ 获取套餐列表异常: {str(e)}")
        print()
        
        # 3. 测试获取特定套餐
        print("3️⃣ 测试获取特定套餐...")
        try:
            response = await client.get(f"{base_url}/payments/plans/standard")
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                plan = response.json()
                print(f"   套餐名称: {plan['name']}")
                print(f"   套餐描述: {plan['description']}")
                print(f"   月付价格: ${plan['monthly_price']}")
                print(f"   年付价格: ${plan['yearly_price']}")
                print(f"   是否热门: {plan['is_popular']}")
                print("   ✅ 特定套餐获取成功")
            else:
                print(f"   ❌ 获取特定套餐失败: {response.text}")
        except Exception as e:
            print(f"   ❌ 获取特定套餐异常: {str(e)}")
        print()
        
        # 4. 测试创建结账会话（模拟）
        print("4️⃣ 测试创建结账会话...")
        try:
            checkout_data = {
                "plan_id": "standard",
                "billing_period": "monthly",
                "return_url": "http://localhost:3000/dashboard",
                "cancel_url": "http://localhost:3000/pricing",
                "customer_email": "test@example.com",
                "customer_name": "测试用户"
            }
            
            print(f"   请求数据: {json.dumps(checkout_data, indent=2, ensure_ascii=False)}")
            
            # 注意：这个测试可能会失败，因为需要真实的Creem API密钥
            response = await client.post(
                f"{base_url}/payments/create-checkout",
                json=checkout_data
            )
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   会话ID: {result.get('session_id', 'N/A')}")
                print(f"   结账URL: {result.get('checkoutUrl', 'N/A')}")
                print("   ✅ 结账会话创建成功")
            else:
                print(f"   ⚠️ 结账会话创建失败（可能需要真实API密钥）: {response.text}")
                
        except Exception as e:
            print(f"   ⚠️ 结账会话创建异常（可能需要真实API密钥）: {str(e)}")
        print()
        
        # 5. 测试获取不存在的套餐
        print("5️⃣ 测试获取不存在的套餐...")
        try:
            response = await client.get(f"{base_url}/payments/plans/nonexistent")
            print(f"   状态码: {response.status_code}")
            if response.status_code == 404:
                print("   ✅ 正确返回404错误")
            else:
                print(f"   ❌ 未正确处理不存在的套餐: {response.text}")
        except Exception as e:
            print(f"   ❌ 测试不存在套餐异常: {str(e)}")
        print()


def test_payment_models():
    """测试支付相关的数据模型"""
    
    print("6️⃣ 测试支付数据模型...")
    
    try:
        from app.services.payment.models import (
            PaymentPlan, CreateCheckoutRequest, BillingPeriod
        )
        
        # 测试创建套餐
        plan = PaymentPlan(
            id="test",
            name="测试套餐",
            description="这是一个测试套餐",
            monthly_price=9.99,
            yearly_price=99.99,
            features={"test": True},
            is_popular=False
        )
        print(f"   套餐创建成功: {plan.name}")
        
        # 测试创建结账请求
        request = CreateCheckoutRequest(
            plan_id="test",
            billing_period=BillingPeriod.MONTHLY,
            return_url="http://localhost:3000/success",
            cancel_url="http://localhost:3000/cancel"
        )
        print(f"   结账请求创建成功: {request.plan_id}")
        
        print("   ✅ 支付数据模型测试通过")
        
    except Exception as e:
        print(f"   ❌ 支付数据模型测试失败: {str(e)}")
    print()


async def main():
    """主测试函数"""
    
    print("🚀 Video2Doc 支付功能测试")
    print("=" * 50)
    
    # 测试数据模型
    test_payment_models()
    
    # 测试API端点
    await test_payment_endpoints()
    
    print("=" * 50)
    print("✅ 支付功能测试完成！")
    print()
    print("📝 注意事项:")
    print("   1. 某些测试可能需要真实的Creem API密钥才能完全通过")
    print("   2. 在生产环境中，请确保配置正确的API密钥和Webhook密钥")
    print("   3. 建议在测试环境中使用Creem的测试API密钥")


if __name__ == "__main__":
    asyncio.run(main()) 