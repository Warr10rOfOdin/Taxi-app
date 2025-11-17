from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import models
import schemas


# Company CRUD
def get_company(db: Session, company_id: int) -> Optional[models.Company]:
    return db.query(models.Company).filter(models.Company.id == company_id).first()


def get_companies(db: Session, skip: int = 0, limit: int = 100) -> List[models.Company]:
    return db.query(models.Company).offset(skip).limit(limit).all()


def create_company(db: Session, company: schemas.CompanyCreate) -> models.Company:
    db_company = models.Company(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


def update_company(db: Session, company_id: int, company: schemas.CompanyUpdate) -> Optional[models.Company]:
    db_company = get_company(db, company_id)
    if db_company:
        for key, value in company.dict(exclude_unset=True).items():
            setattr(db_company, key, value)
        db.commit()
        db.refresh(db_company)
    return db_company


def delete_company(db: Session, company_id: int) -> bool:
    db_company = get_company(db, company_id)
    if db_company:
        db.delete(db_company)
        db.commit()
        return True
    return False


# Driver CRUD
def get_driver(db: Session, driver_id: int) -> Optional[models.Driver]:
    return db.query(models.Driver).filter(models.Driver.id == driver_id).first()


def get_drivers(db: Session, skip: int = 0, limit: int = 100) -> List[models.Driver]:
    return db.query(models.Driver).offset(skip).limit(limit).all()


def create_driver(db: Session, driver: schemas.DriverCreate) -> models.Driver:
    # If this driver is set as default, unset other defaults
    if driver.is_default:
        db.query(models.Driver).update({models.Driver.is_default: False})

    db_driver = models.Driver(**driver.dict())
    db.add(db_driver)
    db.commit()
    db.refresh(db_driver)
    return db_driver


def update_driver(db: Session, driver_id: int, driver: schemas.DriverUpdate) -> Optional[models.Driver]:
    db_driver = get_driver(db, driver_id)
    if db_driver:
        update_data = driver.dict(exclude_unset=True)

        # If setting as default, unset other defaults
        if update_data.get('is_default'):
            db.query(models.Driver).filter(models.Driver.id != driver_id).update({models.Driver.is_default: False})

        for key, value in update_data.items():
            setattr(db_driver, key, value)
        db.commit()
        db.refresh(db_driver)
    return db_driver


def delete_driver(db: Session, driver_id: int) -> bool:
    db_driver = get_driver(db, driver_id)
    if db_driver:
        db.delete(db_driver)
        db.commit()
        return True
    return False


# Bank Account CRUD
def get_bank_account(db: Session, account_id: int) -> Optional[models.BankAccount]:
    return db.query(models.BankAccount).filter(models.BankAccount.id == account_id).first()


def get_bank_accounts(db: Session, skip: int = 0, limit: int = 100) -> List[models.BankAccount]:
    return db.query(models.BankAccount).offset(skip).limit(limit).all()


def create_bank_account(db: Session, account: schemas.BankAccountCreate) -> models.BankAccount:
    # If this account is set as default, unset other defaults
    if account.is_default:
        db.query(models.BankAccount).update({models.BankAccount.is_default: False})

    db_account = models.BankAccount(**account.dict())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


def update_bank_account(db: Session, account_id: int, account: schemas.BankAccountUpdate) -> Optional[models.BankAccount]:
    db_account = get_bank_account(db, account_id)
    if db_account:
        update_data = account.dict(exclude_unset=True)

        # If setting as default, unset other defaults
        if update_data.get('is_default'):
            db.query(models.BankAccount).filter(models.BankAccount.id != account_id).update({models.BankAccount.is_default: False})

        for key, value in update_data.items():
            setattr(db_account, key, value)
        db.commit()
        db.refresh(db_account)
    return db_account


def delete_bank_account(db: Session, account_id: int) -> bool:
    db_account = get_bank_account(db, account_id)
    if db_account:
        db.delete(db_account)
        db.commit()
        return True
    return False


# Template CRUD
def get_template(db: Session, template_id: int) -> Optional[models.Template]:
    return db.query(models.Template).filter(models.Template.id == template_id).first()


def get_templates(db: Session, template_type: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[models.Template]:
    query = db.query(models.Template)
    if template_type:
        query = query.filter(models.Template.template_type == template_type)
    return query.offset(skip).limit(limit).all()


def create_template(db: Session, template: schemas.TemplateCreate) -> models.Template:
    # If this template is set as default, unset other defaults of same type
    if template.is_default:
        db.query(models.Template).filter(models.Template.template_type == template.template_type).update({models.Template.is_default: False})

    db_template = models.Template(**template.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


def update_template(db: Session, template_id: int, template: schemas.TemplateUpdate) -> Optional[models.Template]:
    db_template = get_template(db, template_id)
    if db_template:
        update_data = template.dict(exclude_unset=True)

        # If setting as default, unset other defaults of same type
        if update_data.get('is_default'):
            db.query(models.Template).filter(
                models.Template.template_type == db_template.template_type,
                models.Template.id != template_id
            ).update({models.Template.is_default: False})

        for key, value in update_data.items():
            setattr(db_template, key, value)
        db.commit()
        db.refresh(db_template)
    return db_template


def delete_template(db: Session, template_id: int) -> bool:
    db_template = get_template(db, template_id)
    if db_template:
        db.delete(db_template)
        db.commit()
        return True
    return False


# Shift Report CRUD
def get_shift_report(db: Session, report_id: int) -> Optional[models.ShiftReport]:
    return db.query(models.ShiftReport).filter(models.ShiftReport.id == report_id).first()


def get_shift_reports(db: Session, driver_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[models.ShiftReport]:
    query = db.query(models.ShiftReport).order_by(desc(models.ShiftReport.created_at))
    if driver_id:
        query = query.filter(models.ShiftReport.driver_id == driver_id)
    return query.offset(skip).limit(limit).all()


def create_shift_report(db: Session, report: schemas.ShiftReportCreate) -> models.ShiftReport:
    db_report = models.ShiftReport(**report.dict())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


def create_shift_edit(db: Session, report_id: int, edit: schemas.ShiftEditCreate) -> models.ShiftEdit:
    db_edit = models.ShiftEdit(shift_report_id=report_id, **edit.dict())
    db.add(db_edit)
    db.commit()
    db.refresh(db_edit)
    return db_edit


def delete_shift_report(db: Session, report_id: int) -> bool:
    db_report = get_shift_report(db, report_id)
    if db_report:
        db.delete(db_report)
        db.commit()
        return True
    return False


# Salary Report CRUD
def get_salary_report(db: Session, report_id: int) -> Optional[models.SalaryReport]:
    return db.query(models.SalaryReport).filter(models.SalaryReport.id == report_id).first()


def get_salary_reports(db: Session, driver_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[models.SalaryReport]:
    query = db.query(models.SalaryReport).order_by(desc(models.SalaryReport.created_at))
    if driver_id:
        query = query.filter(models.SalaryReport.driver_id == driver_id)
    return query.offset(skip).limit(limit).all()


def create_salary_report(db: Session, report: schemas.SalaryReportCreate) -> models.SalaryReport:
    db_report = models.SalaryReport(**report.dict())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


def delete_salary_report(db: Session, report_id: int) -> bool:
    db_report = get_salary_report(db, report_id)
    if db_report:
        db.delete(db_report)
        db.commit()
        return True
    return False
