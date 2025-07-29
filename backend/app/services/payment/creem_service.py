"""
Creem支付平台服务
基于Creem API文档: https://docs.creem.io/api-reference
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import aiohttp
from app.config import get_settings
from .models import (
    CreateCheckoutRequest,
    CheckoutResponse,
    PaymentPlan,
    CustomerInfo,
    SubscriptionInfo,
    PaymentTransaction,
    WebhookEvent,
    LicenseValidationRequest,
    LicenseValidationResponse,
    BillingPeriod,
    PaymentStatus,
    SubscriptionStatus
)

logger = logging.getLogger(__name__)


class CreemAPIError(Exception):
    """Creem API错误"""
    def __init__(self, status_code: int, message: str, details: Optional[Dict] = None):
        self.status_code = status_code
        self.message = message
        self.details = details or {}
        super().__init__(f"Creem API Error {status_code}: {message}")


class CreemPaymentService:
    """Creem支付服务"""
    
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.creem_api_key
        self.base_url = "https://api.creem.io"
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # 预定义的支付套餐
        self.plans = {
            "starter": PaymentPlan(
                id="starter",
                name="入门版",
                description="适合个人用户的基础需求",
                monthly_price=4.99,
                yearly_price=49.99,
                features={
                    "video_length": "10分钟",
                    "upload_methods": ["本地上传"],
                    "ai_notes": "基础结构提取",
                    "speech_to_text": "标准模型",
                    "image_extraction": False,
                    "timeline": False,
                    "languages": ["英语"],
                    "export_formats": ["Markdown"],
                    "history_limit": 5,
                    "processing_speed": "标准",
                    "support": "邮件支持"
                },
                is_popular=False
            ),
            "standard": PaymentPlan(
                id="standard",
                name="标准版",
                description="最受欢迎的选择，功能全面",
                monthly_price=9.99,
                yearly_price=99.99,
                features={
                    "video_length": "30分钟",
                    "upload_methods": ["本地上传", "链接导入"],
                    "ai_notes": "精准语义摘要 + 段落结构",
                    "speech_to_text": "精准模型（支持多口音）",
                    "image_extraction": "1张封面图",
                    "timeline": True,
                    "languages": ["英语", "中文"],
                    "export_formats": ["Markdown", "PDF"],
                    "history_limit": 30,
                    "processing_speed": "标准队列",
                    "support": "邮件 + FAQ教程"
                },
                is_popular=True
            ),
            "premium": PaymentPlan(
                id="premium",
                name="高级版",
                description="专业用户的完整解决方案",
                monthly_price=19.99,
                yearly_price=199.99,
                features={
                    "video_length": "90分钟",
                    "upload_methods": ["本地上传", "链接导入", "云盘导入"],
                    "ai_notes": "多风格笔记（摘要/清单/图表）",
                    "speech_to_text": "专业模型 + 智能断句优化",
                    "image_extraction": "3-5张关键帧图像",
                    "timeline": True,
                    "languages": ["多语言(10+语言)"],
                    "export_formats": ["Markdown", "PDF", "Notion"],
                    "history_limit": -1,  # 无限制
                    "processing_speed": "高优先通道",
                    "support": "邮件 + 实时聊天支持"
                },
                is_popular=False
            )
        }

    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """发起API请求"""
        url = f"{self.base_url}{endpoint}"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data
                ) as response:
                    response_data = await response.json()
                    
                    if response.status >= 400:
                        raise CreemAPIError(
                            status_code=response.status,
                            message=response_data.get("message", "Unknown error"),
                            details=response_data
                        )
                    
                    return response_data
                    
            except aiohttp.ClientError as e:
                logger.error(f"Creem API请求失败: {str(e)}")
                raise CreemAPIError(
                    status_code=500,
                    message=f"网络请求失败: {str(e)}"
                )

    async def create_product(self, plan: PaymentPlan) -> str:
        """
        创建产品
        参考: https://docs.creem.io/api-reference/product/create-product
        """
        data = {
            "name": plan.name,
            "description": plan.description,
            "prices": [
                {
                    "amount": int(plan.monthly_price * 100),  # 转换为分
                    "currency": "USD",
                    "interval": "month"
                },
                {
                    "amount": int(plan.yearly_price * 100),  # 转换为分
                    "currency": "USD",
                    "interval": "year"
                }
            ],
            "metadata": {
                "plan_id": plan.id,
                "features": plan.features
            }
        }
        
        response = await self._make_request("POST", "/product", data)
        return response["product_id"]

    async def create_checkout_session(
        self, 
        request: CreateCheckoutRequest
    ) -> CheckoutResponse:
        """
        创建结账会话
        参考: https://docs.creem.io/api-reference/checkout/create-checkout-session
        """
        plan = self.plans.get(request.plan_id)
        if not plan:
            raise ValueError(f"未知的套餐ID: {request.plan_id}")
        
        # 计算价格
        price = plan.monthly_price if request.billing_period == BillingPeriod.MONTHLY else plan.yearly_price
        
        data = {
            "product_id": request.plan_id,  # 假设product_id与plan_id相同
            "price": int(price * 100),  # 转换为分
            "currency": "USD",
            "interval": request.billing_period.value,
            "success_url": request.return_url,
            "cancel_url": request.cancel_url,
            "metadata": {
                "plan_id": request.plan_id,
                "billing_period": request.billing_period.value
            }
        }
        
        if request.customer_email:
            data["customer_email"] = request.customer_email
        
        if request.customer_name:
            data["customer_name"] = request.customer_name
            
        if request.discount_code:
            data["discount_code"] = request.discount_code
        
        response = await self._make_request("POST", "/checkout", data)
        
        return CheckoutResponse(
            session_id=response["session_id"],
            checkout_url=response["checkout_url"],
            expires_at=datetime.now() + timedelta(hours=1)  # 假设1小时过期
        )

    async def get_checkout_session(self, session_id: str) -> Dict[str, Any]:
        """
        获取结账会话信息
        参考: https://docs.creem.io/api-reference/checkout/get-checkout-session
        """
        return await self._make_request("GET", f"/checkout/{session_id}")

    async def get_customer(self, customer_id: str) -> CustomerInfo:
        """
        获取客户信息
        参考: https://docs.creem.io/api-reference/customer/get-customer
        """
        response = await self._make_request("GET", f"/customer/{customer_id}")
        
        return CustomerInfo(
            customer_id=response["customer_id"],
            email=response["email"],
            name=response.get("name"),
            created_at=datetime.fromisoformat(response["created_at"]),
            subscription_status=SubscriptionStatus(response["subscription_status"]),
            current_plan=response.get("current_plan")
        )

    async def get_subscription(self, subscription_id: str) -> SubscriptionInfo:
        """
        获取订阅信息
        参考: https://docs.creem.io/api-reference/subscription/get-subscription
        """
        response = await self._make_request("GET", f"/subscription/{subscription_id}")
        
        return SubscriptionInfo(
            subscription_id=response["subscription_id"],
            customer_id=response["customer_id"],
            plan_id=response["plan_id"],
            status=SubscriptionStatus(response["status"]),
            billing_period=BillingPeriod(response["billing_period"]),
            current_period_start=datetime.fromisoformat(response["current_period_start"]),
            current_period_end=datetime.fromisoformat(response["current_period_end"]),
            created_at=datetime.fromisoformat(response["created_at"]),
            updated_at=datetime.fromisoformat(response["updated_at"])
        )

    async def update_subscription(
        self, 
        subscription_id: str, 
        new_plan_id: str
    ) -> SubscriptionInfo:
        """
        更新订阅
        参考: https://docs.creem.io/api-reference/subscription/update-subscription
        """
        data = {
            "plan_id": new_plan_id
        }
        
        response = await self._make_request("POST", f"/subscription/{subscription_id}/update", data)
        
        return SubscriptionInfo(
            subscription_id=response["subscription_id"],
            customer_id=response["customer_id"],
            plan_id=response["plan_id"],
            status=SubscriptionStatus(response["status"]),
            billing_period=BillingPeriod(response["billing_period"]),
            current_period_start=datetime.fromisoformat(response["current_period_start"]),
            current_period_end=datetime.fromisoformat(response["current_period_end"]),
            created_at=datetime.fromisoformat(response["created_at"]),
            updated_at=datetime.fromisoformat(response["updated_at"])
        )

    async def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """
        取消订阅
        参考: https://docs.creem.io/api-reference/subscription/cancel-subscription
        """
        return await self._make_request("POST", f"/subscription/{subscription_id}/cancel")

    async def list_transactions(
        self, 
        customer_id: Optional[str] = None,
        limit: int = 50
    ) -> List[PaymentTransaction]:
        """
        列出交易记录
        参考: https://docs.creem.io/api-reference/transactions/list-transactions
        """
        params = {"limit": limit}
        if customer_id:
            params["customer_id"] = customer_id
        
        # 构建查询字符串
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        endpoint = f"/transactions?{query_string}"
        
        response = await self._make_request("GET", endpoint)
        
        transactions = []
        for transaction_data in response.get("transactions", []):
            transactions.append(PaymentTransaction(
                transaction_id=transaction_data["transaction_id"],
                customer_id=transaction_data["customer_id"],
                amount=transaction_data["amount"] / 100,  # 转换为元
                currency=transaction_data.get("currency", "USD"),
                status=PaymentStatus(transaction_data["status"]),
                plan_id=transaction_data.get("plan_id"),
                created_at=datetime.fromisoformat(transaction_data["created_at"]),
                updated_at=datetime.fromisoformat(transaction_data["updated_at"])
            ))
        
        return transactions

    async def validate_license(
        self, 
        request: LicenseValidationRequest
    ) -> LicenseValidationResponse:
        """
        验证许可证密钥
        参考: https://docs.creem.io/api-reference/license/validate-license-key
        """
        data = {
            "license_key": request.license_key
        }
        
        if request.customer_id:
            data["customer_id"] = request.customer_id
        
        response = await self._make_request("POST", "/license/validate", data)
        
        return LicenseValidationResponse(
            valid=response["valid"],
            license_key=response["license_key"],
            customer_id=response.get("customer_id"),
            plan_id=response.get("plan_id"),
            expires_at=datetime.fromisoformat(response["expires_at"]) if response.get("expires_at") else None,
            usage_count=response.get("usage_count", 0),
            usage_limit=response.get("usage_limit")
        )

    async def create_discount_code(
        self, 
        code: str, 
        discount_percent: int,
        expires_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        创建折扣码
        参考: https://docs.creem.io/api-reference/discount-code/create-discount-code
        """
        data = {
            "code": code,
            "discount_percent": discount_percent
        }
        
        if expires_at:
            data["expires_at"] = expires_at.isoformat()
        
        return await self._make_request("POST", "/discount", data)

    async def handle_webhook(self, event_data: Dict[str, Any]) -> WebhookEvent:
        """处理Webhook事件"""
        event = WebhookEvent(
            event_id=event_data["event_id"],
            event_type=event_data["event_type"],
            data=event_data["data"],
            timestamp=datetime.fromisoformat(event_data["timestamp"])
        )
        
        logger.info(f"处理Webhook事件: {event.event_type}")
        
        # 根据事件类型处理不同逻辑
        if event.event_type == "payment.completed":
            await self._handle_payment_completed(event)
        elif event.event_type == "subscription.created":
            await self._handle_subscription_created(event)
        elif event.event_type == "subscription.cancelled":
            await self._handle_subscription_cancelled(event)
        
        return event

    async def _handle_payment_completed(self, event: WebhookEvent):
        """处理支付完成事件"""
        payment_data = event.data
        logger.info(f"支付完成: {payment_data}")
        
        # 这里可以添加业务逻辑，如：
        # - 激活用户账户
        # - 发送确认邮件
        # - 更新用户权限
        pass

    async def _handle_subscription_created(self, event: WebhookEvent):
        """处理订阅创建事件"""
        subscription_data = event.data
        logger.info(f"订阅创建: {subscription_data}")
        
        # 业务逻辑：激活用户功能
        pass

    async def _handle_subscription_cancelled(self, event: WebhookEvent):
        """处理订阅取消事件"""
        subscription_data = event.data
        logger.info(f"订阅取消: {subscription_data}")
        
        # 业务逻辑：禁用用户功能
        pass

    def get_plan(self, plan_id: str) -> Optional[PaymentPlan]:
        """获取套餐信息"""
        return self.plans.get(plan_id)

    def list_plans(self) -> List[PaymentPlan]:
        """列出所有套餐"""
        return list(self.plans.values())


# 全局服务实例
creem_service = CreemPaymentService() 