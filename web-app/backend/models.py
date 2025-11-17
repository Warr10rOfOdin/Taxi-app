from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    org_number = Column(String)
    address = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    driver_id = Column(String(4), nullable=False)  # 4-digit ID
    commission_percentage = Column(Float, default=45.0)
    bank_account_id = Column(Integer, ForeignKey("bank_accounts.id"), nullable=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bank_account = relationship("BankAccount", back_populates="drivers")
    shift_reports = relationship("ShiftReport", back_populates="driver")
    salary_reports = relationship("SalaryReport", back_populates="driver")


class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String, nullable=False)  # Format: 0000.00.00000
    account_name = Column(String)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    drivers = relationship("Driver", back_populates="bank_account")


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    template_type = Column(String, nullable=False)  # 'shift' or 'salary'
    columns = Column(JSON, nullable=False)  # List of column names
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ShiftReport(Base):
    __tablename__ = "shift_reports"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)
    file_name = Column(String, nullable=False)
    report_date = Column(DateTime, default=datetime.utcnow)
    data = Column(JSON, nullable=False)  # Parsed report data
    summary = Column(JSON)  # Summary statistics
    pdf_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    driver = relationship("Driver", back_populates="shift_reports")
    edits = relationship("ShiftEdit", back_populates="shift_report", cascade="all, delete-orphan")


class ShiftEdit(Base):
    __tablename__ = "shift_edits"

    id = Column(Integer, primary_key=True, index=True)
    shift_report_id = Column(Integer, ForeignKey("shift_reports.id"), nullable=False)
    row_index = Column(Integer, nullable=False)
    column_name = Column(String, nullable=False)
    old_value = Column(String)
    new_value = Column(String, nullable=False)
    note = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    shift_report = relationship("ShiftReport", back_populates="edits")


class SalaryReport(Base):
    __tablename__ = "salary_reports"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False)
    report_period = Column(String)  # e.g., "January 2024"
    file_names = Column(JSON)  # List of imported files
    gross_salary = Column(Float)
    commission_percentage = Column(Float)
    net_salary = Column(Float)
    cash_amount = Column(Float)
    tips = Column(Float)
    data = Column(JSON, nullable=False)  # Detailed salary breakdown
    pdf_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    driver = relationship("Driver", back_populates="salary_reports")
