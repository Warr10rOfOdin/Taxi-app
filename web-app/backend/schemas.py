from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import re


# Company Schemas
class CompanyBase(BaseModel):
    name: str
    org_number: Optional[str] = None
    address: Optional[str] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(CompanyBase):
    pass


class Company(CompanyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Driver Schemas
class DriverBase(BaseModel):
    name: str
    driver_id: str = Field(..., min_length=4, max_length=4)
    commission_percentage: float = Field(default=45.0, ge=0, le=100)
    bank_account_id: Optional[int] = None
    is_default: bool = False

    @validator('driver_id')
    def validate_driver_id(cls, v):
        if not v.isdigit():
            raise ValueError('Driver ID must be 4 digits')
        return v


class DriverCreate(DriverBase):
    pass


class DriverUpdate(BaseModel):
    name: Optional[str] = None
    driver_id: Optional[str] = Field(None, min_length=4, max_length=4)
    commission_percentage: Optional[float] = Field(None, ge=0, le=100)
    bank_account_id: Optional[int] = None
    is_default: Optional[bool] = None


class Driver(DriverBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Bank Account Schemas
class BankAccountBase(BaseModel):
    account_number: str
    account_name: Optional[str] = None
    is_default: bool = False

    @validator('account_number')
    def validate_account_number(cls, v):
        # Norwegian bank account format: 0000.00.00000
        pattern = r'^\d{4}\.\d{2}\.\d{5}$'
        if not re.match(pattern, v):
            raise ValueError('Bank account must be in format: 0000.00.00000')
        return v


class BankAccountCreate(BankAccountBase):
    pass


class BankAccountUpdate(BaseModel):
    account_number: Optional[str] = None
    account_name: Optional[str] = None
    is_default: Optional[bool] = None


class BankAccount(BankAccountBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Template Schemas
class TemplateBase(BaseModel):
    name: str
    template_type: str  # 'shift' or 'salary'
    columns: List[str]
    is_default: bool = False

    @validator('template_type')
    def validate_template_type(cls, v):
        if v not in ['shift', 'salary']:
            raise ValueError('Template type must be "shift" or "salary"')
        return v


class TemplateCreate(TemplateBase):
    pass


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    template_type: Optional[str] = None
    columns: Optional[List[str]] = None
    is_default: Optional[bool] = None


class Template(TemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Shift Report Schemas
class ShiftEditBase(BaseModel):
    row_index: int
    column_name: str
    old_value: Optional[str] = None
    new_value: str
    note: Optional[str] = None


class ShiftEditCreate(ShiftEditBase):
    pass


class ShiftEdit(ShiftEditBase):
    id: int
    shift_report_id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class ShiftReportBase(BaseModel):
    driver_id: Optional[int] = None
    file_name: str
    report_date: Optional[datetime] = None
    data: Dict[str, Any]
    summary: Optional[Dict[str, Any]] = None


class ShiftReportCreate(ShiftReportBase):
    pass


class ShiftReport(ShiftReportBase):
    id: int
    pdf_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    edits: List[ShiftEdit] = []

    class Config:
        from_attributes = True


# Salary Report Schemas
class SalaryReportBase(BaseModel):
    driver_id: int
    report_period: Optional[str] = None
    file_names: List[str]
    gross_salary: Optional[float] = None
    commission_percentage: Optional[float] = None
    net_salary: Optional[float] = None
    cash_amount: Optional[float] = None
    tips: Optional[float] = None
    data: Dict[str, Any]


class SalaryReportCreate(SalaryReportBase):
    pass


class SalaryReport(SalaryReportBase):
    id: int
    pdf_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# File Upload Response
class FileUploadResponse(BaseModel):
    filename: str
    columns: List[str]
    row_count: int
    preview: List[Dict[str, Any]]


# PDF Generation Request
class PDFGenerateRequest(BaseModel):
    report_id: int
    report_type: str  # 'shift' or 'salary'

    @validator('report_type')
    def validate_report_type(cls, v):
        if v not in ['shift', 'salary']:
            raise ValueError('Report type must be "shift" or "salary"')
        return v
