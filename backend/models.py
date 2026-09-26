"""
Pydantic models for request/response validation.
"""

from __future__ import annotations
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# ── Auth ───────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=150)
    email: str = Field(..., max_length=200)
    password: str = Field(..., min_length=6)
    phone: Optional[str] = Field(None, max_length=15)
    address: Optional[str] = None
    date_of_birth: Optional[date] = None
    aadhaar_number: Optional[str] = Field(None, min_length=12, max_length=12)
    role: str = Field(default="citizen")


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    role: str
    full_name: str


class UserResponse(BaseModel):
    user_id: int
    full_name: str
    email: str
    phone: Optional[str]
    address: Optional[str]
    date_of_birth: Optional[date]
    aadhaar_number: Optional[str]
    role: str
    is_active: bool
    created_at: Optional[datetime]


# ── Services ───────────────────────────────────────────────────────────────────

class ServiceResponse(BaseModel):
    service_id: int
    department_id: int
    name: str
    description: Optional[str]
    category: Optional[str]
    fee: float
    processing_days: int
    is_active: bool
    department_name: Optional[str] = None


class ServiceRequirementResponse(BaseModel):
    requirement_id: int
    service_id: int
    document_name: str
    description: Optional[str]
    is_mandatory: bool


# ── Applications ───────────────────────────────────────────────────────────────

class ApplicationCreate(BaseModel):
    service_id: int


class ApplicationStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(Submitted|Under Review|Documents Verified|Approved|Rejected|Returned)$")
    remarks: Optional[str] = None


class ApplicationResponse(BaseModel):
    application_id: int
    application_ref: str
    citizen_id: int
    service_id: int
    officer_id: Optional[int]
    status: str
    remarks: Optional[str]
    submitted_at: Optional[datetime]
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    citizen_name: Optional[str] = None
    service_name: Optional[str] = None
    department_name: Optional[str] = None
    officer_name: Optional[str] = None


# ── Payments ───────────────────────────────────────────────────────────────────

class PaymentCreate(BaseModel):
    application_id: int
    payment_method: str = Field(default="UPI", pattern="^(UPI|Net Banking|Debit Card|Credit Card|Cash)$")


class PaymentResponse(BaseModel):
    payment_id: int
    application_id: int
    citizen_id: int
    amount: float
    payment_method: str
    transaction_ref: Optional[str]
    status: str
    paid_at: Optional[datetime]


# ── Complaints ─────────────────────────────────────────────────────────────────

class ComplaintCreate(BaseModel):
    application_id: Optional[int] = None
    subject: str = Field(..., min_length=5, max_length=300)
    description: str = Field(..., min_length=10)
    priority: str = Field(default="Medium", pattern="^(Low|Medium|High|Critical)$")


class ComplaintStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(Open|In Progress|Resolved|Closed)$")


class ComplaintResponse(BaseModel):
    complaint_id: int
    complaint_ref: str
    citizen_id: int
    application_id: Optional[int]
    subject: str
    description: str
    status: str
    priority: str
    created_at: Optional[datetime]
    resolved_at: Optional[datetime]


# ── Notifications ──────────────────────────────────────────────────────────────

class NotificationResponse(BaseModel):
    notification_id: int
    user_id: int
    title: str
    message: str
    type: str
    is_read: bool
    created_at: Optional[datetime]


# ── Reports / Analytics ───────────────────────────────────────────────────────

class OverallStats(BaseModel):
    total_applications: int
    approved: int
    rejected: int
    pending: int
    under_review: int
    avg_processing_days: Optional[float]


class DepartmentSummary(BaseModel):
    department_id: int
    department_name: str
    total_applications: int
    approved: int
    rejected: int
    pending: int
    under_review: int


class ServiceRanking(BaseModel):
    service_id: int
    service_name: str
    department_name: str
    total_applications: int
    popularity_rank: int
