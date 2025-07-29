"""
支付服务相关的数据模型
"""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class BillingPeriod(str, Enum):
    """计费周期"""
    MONTHLY = "monthly"
    YEARLY = "yearly"


class PaymentStatus(str, Enum):
    """支付状态"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class SubscriptionStatus(str, Enum):
    """订阅状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PAUSED = "paused"


class PaymentPlan(BaseModel):
    """支付套餐"""
    id: str = Field(..., description="套餐ID")
    name: str = Field(..., description="套餐名称")
    description: str = Field(..., description="套餐描述")
    monthly_price: float = Field(..., description="月付价格", ge=0)
    yearly_price: float = Field(..., description="年付价格", ge=0)
    features: Dict[str, Any] = Field(default_factory=dict, description="套餐功能")
    is_popular: bool = Field(default=False, description="是否为热门套餐")


class CreateCheckoutRequest(BaseModel):
    """创建结账会话请求"""
    plan_id: str = Field(..., description="套餐ID")
    billing_period: BillingPeriod = Field(..., description="计费周期")
    return_url: str = Field(..., description="支付成功返回URL")
    cancel_url: str = Field(..., description="支付取消返回URL")
    customer_email: Optional[str] = Field(None, description="客户邮箱")
    customer_name: Optional[str] = Field(None, description="客户姓名")
    discount_code: Optional[str] = Field(None, description="折扣码")


class CheckoutResponse(BaseModel):
    """结账会话响应"""
    session_id: str = Field(..., description="会话ID")
    checkout_url: str = Field(..., description="结账URL")
    expires_at: datetime = Field(..., description="会话过期时间")


class CustomerInfo(BaseModel):
    """客户信息"""
    customer_id: str = Field(..., description="客户ID")
    email: str = Field(..., description="邮箱")
    name: Optional[str] = Field(None, description="姓名")
    created_at: datetime = Field(..., description="创建时间")
    subscription_status: SubscriptionStatus = Field(..., description="订阅状态")
    current_plan: Optional[str] = Field(None, description="当前套餐")


class SubscriptionInfo(BaseModel):
    """订阅信息"""
    subscription_id: str = Field(..., description="订阅ID")
    customer_id: str = Field(..., description="客户ID")
    plan_id: str = Field(..., description="套餐ID")
    status: SubscriptionStatus = Field(..., description="订阅状态")
    billing_period: BillingPeriod = Field(..., description="计费周期")
    current_period_start: datetime = Field(..., description="当前周期开始时间")
    current_period_end: datetime = Field(..., description="当前周期结束时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class PaymentTransaction(BaseModel):
    """支付交易"""
    transaction_id: str = Field(..., description="交易ID")
    customer_id: str = Field(..., description="客户ID")
    amount: float = Field(..., description="金额", ge=0)
    currency: str = Field(default="USD", description="货币")
    status: PaymentStatus = Field(..., description="支付状态")
    plan_id: Optional[str] = Field(None, description="套餐ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class WebhookEvent(BaseModel):
    """Webhook事件"""
    event_id: str = Field(..., description="事件ID")
    event_type: str = Field(..., description="事件类型")
    data: Dict[str, Any] = Field(..., description="事件数据")
    timestamp: datetime = Field(..., description="事件时间")


class LicenseValidationRequest(BaseModel):
    """许可证验证请求"""
    license_key: str = Field(..., description="许可证密钥")
    customer_id: Optional[str] = Field(None, description="客户ID")


class LicenseValidationResponse(BaseModel):
    """许可证验证响应"""
    valid: bool = Field(..., description="是否有效")
    license_key: str = Field(..., description="许可证密钥")
    customer_id: Optional[str] = Field(None, description="客户ID")
    plan_id: Optional[str] = Field(None, description="套餐ID")
    expires_at: Optional[datetime] = Field(None, description="过期时间")
    usage_count: int = Field(default=0, description="使用次数")
    usage_limit: Optional[int] = Field(None, description="使用限制") 