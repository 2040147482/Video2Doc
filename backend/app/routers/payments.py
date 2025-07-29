"""
支付相关的API路由
集成Creem支付平台
"""

import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict

from app.services.payment import (
    creem_service,
    CreateCheckoutRequest,
    CheckoutResponse,
    PaymentPlan,
    CustomerInfo,
    SubscriptionInfo,
    LicenseValidationRequest,
    LicenseValidationResponse
)
from app.services.payment.creem_service import CreemAPIError
from app.exceptions import create_error_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["支付管理"])


@router.get("/plans", response_model=List[PaymentPlan])
async def list_plans():
    """
    获取所有可用的支付套餐
    """
    try:
        plans = creem_service.list_plans()
        return plans
    except Exception as e:
        logger.error(f"获取套餐列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取套餐列表失败")


@router.get("/plans/{plan_id}", response_model=PaymentPlan)
async def get_plan(plan_id: str):
    """
    获取特定套餐信息
    """
    plan = creem_service.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"套餐 {plan_id} 不存在")
    
    return plan


@router.post("/create-checkout", response_model=Dict[str, str])
async def create_checkout_session(request: CreateCheckoutRequest):
    """
    创建Creem结账会话
    """
    try:
        checkout = await creem_service.create_checkout_session(request)
        
        return {
            "session_id": checkout.session_id,
            "checkoutUrl": checkout.checkout_url
        }
        
    except ValueError as e:
        logger.warning(f"创建结账会话失败 - 参数错误: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except CreemAPIError as e:
        logger.error(f"Creem API错误: {e.status_code} - {e.message}")
        raise HTTPException(
            status_code=e.status_code if e.status_code < 500 else 500,
            detail=f"支付服务错误: {e.message}"
        )
    
    except Exception as e:
        logger.error(f"创建结账会话失败: {str(e)}")
        raise HTTPException(status_code=500, detail="创建支付会话失败")


@router.get("/checkout/{session_id}")
async def get_checkout_session(session_id: str):
    """
    获取结账会话状态
    """
    try:
        session_data = await creem_service.get_checkout_session(session_id)
        return session_data
        
    except CreemAPIError as e:
        if e.status_code == 404:
            raise HTTPException(status_code=404, detail="结账会话不存在")
        raise HTTPException(status_code=500, detail="获取会话信息失败")
    
    except Exception as e:
        logger.error(f"获取结账会话失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取会话信息失败")


@router.get("/customer/{customer_id}", response_model=CustomerInfo)
async def get_customer(customer_id: str):
    """
    获取客户信息
    """
    try:
        customer = await creem_service.get_customer(customer_id)
        return customer
        
    except CreemAPIError as e:
        if e.status_code == 404:
            raise HTTPException(status_code=404, detail="客户不存在")
        raise HTTPException(status_code=500, detail="获取客户信息失败")
    
    except Exception as e:
        logger.error(f"获取客户信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取客户信息失败")


@router.get("/subscription/{subscription_id}", response_model=SubscriptionInfo)
async def get_subscription(subscription_id: str):
    """
    获取订阅信息
    """
    try:
        subscription = await creem_service.get_subscription(subscription_id)
        return subscription
        
    except CreemAPIError as e:
        if e.status_code == 404:
            raise HTTPException(status_code=404, detail="订阅不存在")
        raise HTTPException(status_code=500, detail="获取订阅信息失败")
    
    except Exception as e:
        logger.error(f"获取订阅信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取订阅信息失败")


@router.post("/subscription/{subscription_id}/upgrade", response_model=SubscriptionInfo)
async def upgrade_subscription(subscription_id: str, new_plan_id: str):
    """
    升级订阅套餐
    """
    try:
        # 验证新套餐是否存在
        if not creem_service.get_plan(new_plan_id):
            raise HTTPException(status_code=400, detail=f"套餐 {new_plan_id} 不存在")
        
        subscription = await creem_service.update_subscription(subscription_id, new_plan_id)
        return subscription
        
    except CreemAPIError as e:
        if e.status_code == 404:
            raise HTTPException(status_code=404, detail="订阅不存在")
        raise HTTPException(status_code=500, detail="升级订阅失败")
    
    except Exception as e:
        logger.error(f"升级订阅失败: {str(e)}")
        raise HTTPException(status_code=500, detail="升级订阅失败")


@router.post("/subscription/{subscription_id}/cancel")
async def cancel_subscription(subscription_id: str):
    """
    取消订阅
    """
    try:
        result = await creem_service.cancel_subscription(subscription_id)
        return {"message": "订阅已取消", "data": result}
        
    except CreemAPIError as e:
        if e.status_code == 404:
            raise HTTPException(status_code=404, detail="订阅不存在")
        raise HTTPException(status_code=500, detail="取消订阅失败")
    
    except Exception as e:
        logger.error(f"取消订阅失败: {str(e)}")
        raise HTTPException(status_code=500, detail="取消订阅失败")


@router.get("/transactions")
async def list_transactions(
    customer_id: Optional[str] = None,
    limit: int = 50
):
    """
    获取交易记录
    """
    try:
        transactions = await creem_service.list_transactions(customer_id, limit)
        return {
            "transactions": [t.dict() for t in transactions],
            "total": len(transactions)
        }
        
    except CreemAPIError as e:
        raise HTTPException(status_code=500, detail="获取交易记录失败")
    
    except Exception as e:
        logger.error(f"获取交易记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取交易记录失败")


@router.post("/validate-license", response_model=LicenseValidationResponse)
async def validate_license(request: LicenseValidationRequest):
    """
    验证许可证密钥
    """
    try:
        validation_result = await creem_service.validate_license(request)
        return validation_result
        
    except CreemAPIError as e:
        raise HTTPException(
            status_code=400 if e.status_code == 400 else 500,
            detail="许可证验证失败"
        )
    
    except Exception as e:
        logger.error(f"许可证验证失败: {str(e)}")
        raise HTTPException(status_code=500, detail="许可证验证失败")


@router.post("/webhook")
async def handle_webhook(request: Request):
    """
    处理Creem Webhook事件
    """
    try:
        # 获取请求体
        body = await request.body()
        event_data = await request.json()
        
        # 这里应该验证Webhook签名（生产环境必需）
        # signature = request.headers.get("x-creem-signature")
        # if not verify_webhook_signature(body, signature):
        #     raise HTTPException(status_code=401, detail="无效的Webhook签名")
        
        # 处理事件
        event = await creem_service.handle_webhook(event_data)
        
        logger.info(f"Webhook事件处理完成: {event.event_type}")
        
        return {"status": "success", "event_id": event.event_id}
        
    except Exception as e:
        logger.error(f"Webhook处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook处理失败")


@router.post("/discount")
async def create_discount_code(
    code: str,
    discount_percent: int,
    expires_at: Optional[str] = None
):
    """
    创建折扣码（管理员功能）
    """
    try:
        from datetime import datetime
        expires_datetime = None
        if expires_at:
            expires_datetime = datetime.fromisoformat(expires_at)
        
        result = await creem_service.create_discount_code(
            code=code,
            discount_percent=discount_percent,
            expires_at=expires_datetime
        )
        
        return {"message": "折扣码创建成功", "data": result}
        
    except CreemAPIError as e:
        raise HTTPException(
            status_code=400 if e.status_code == 400 else 500,
            detail="创建折扣码失败"
        )
    
    except Exception as e:
        logger.error(f"创建折扣码失败: {str(e)}")
        raise HTTPException(status_code=500, detail="创建折扣码失败")


@router.get("/health")
async def payment_health_check():
    """
    支付服务健康检查
    """
    try:
        # 简单检查服务配置
        plans = creem_service.list_plans()
        
        return {
            "status": "healthy",
            "service": "creem_payment",
            "plans_available": len(plans),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"支付服务健康检查失败: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "creem_payment",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        ) 