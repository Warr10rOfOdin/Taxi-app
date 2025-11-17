from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from datetime import datetime
import json

import crud
import models
import schemas
import services
from database import get_db, init_db, engine

# Initialize database
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Voss Taxi Web App", version="1.0.0")

# CORS middleware
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories for uploads and PDFs (use /tmp in serverless)
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
PDF_DIR = os.getenv("PDF_DIR", "pdfs")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)


# Health check
@app.get("/")
def read_root():
    return {"status": "ok", "message": "Voss Taxi Web App API"}


# ========== Company Endpoints ==========
@app.get("/api/companies", response_model=List[schemas.Company])
def get_companies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_companies(db, skip=skip, limit=limit)


@app.get("/api/companies/{company_id}", response_model=schemas.Company)
def get_company(company_id: int, db: Session = Depends(get_db)):
    company = crud.get_company(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@app.post("/api/companies", response_model=schemas.Company)
def create_company(company: schemas.CompanyCreate, db: Session = Depends(get_db)):
    return crud.create_company(db, company)


@app.put("/api/companies/{company_id}", response_model=schemas.Company)
def update_company(company_id: int, company: schemas.CompanyUpdate, db: Session = Depends(get_db)):
    updated = crud.update_company(db, company_id, company)
    if not updated:
        raise HTTPException(status_code=404, detail="Company not found")
    return updated


@app.delete("/api/companies/{company_id}")
def delete_company(company_id: int, db: Session = Depends(get_db)):
    if not crud.delete_company(db, company_id):
        raise HTTPException(status_code=404, detail="Company not found")
    return {"message": "Company deleted successfully"}


# ========== Driver Endpoints ==========
@app.get("/api/drivers", response_model=List[schemas.Driver])
def get_drivers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_drivers(db, skip=skip, limit=limit)


@app.get("/api/drivers/{driver_id}", response_model=schemas.Driver)
def get_driver(driver_id: int, db: Session = Depends(get_db)):
    driver = crud.get_driver(db, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver


@app.post("/api/drivers", response_model=schemas.Driver)
def create_driver(driver: schemas.DriverCreate, db: Session = Depends(get_db)):
    return crud.create_driver(db, driver)


@app.put("/api/drivers/{driver_id}", response_model=schemas.Driver)
def update_driver(driver_id: int, driver: schemas.DriverUpdate, db: Session = Depends(get_db)):
    updated = crud.update_driver(db, driver_id, driver)
    if not updated:
        raise HTTPException(status_code=404, detail="Driver not found")
    return updated


@app.delete("/api/drivers/{driver_id}")
def delete_driver(driver_id: int, db: Session = Depends(get_db)):
    if not crud.delete_driver(db, driver_id):
        raise HTTPException(status_code=404, detail="Driver not found")
    return {"message": "Driver deleted successfully"}


# ========== Bank Account Endpoints ==========
@app.get("/api/bank-accounts", response_model=List[schemas.BankAccount])
def get_bank_accounts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_bank_accounts(db, skip=skip, limit=limit)


@app.get("/api/bank-accounts/{account_id}", response_model=schemas.BankAccount)
def get_bank_account(account_id: int, db: Session = Depends(get_db)):
    account = crud.get_bank_account(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Bank account not found")
    return account


@app.post("/api/bank-accounts", response_model=schemas.BankAccount)
def create_bank_account(account: schemas.BankAccountCreate, db: Session = Depends(get_db)):
    return crud.create_bank_account(db, account)


@app.put("/api/bank-accounts/{account_id}", response_model=schemas.BankAccount)
def update_bank_account(account_id: int, account: schemas.BankAccountUpdate, db: Session = Depends(get_db)):
    updated = crud.update_bank_account(db, account_id, account)
    if not updated:
        raise HTTPException(status_code=404, detail="Bank account not found")
    return updated


@app.delete("/api/bank-accounts/{account_id}")
def delete_bank_account(account_id: int, db: Session = Depends(get_db)):
    if not crud.delete_bank_account(db, account_id):
        raise HTTPException(status_code=404, detail="Bank account not found")
    return {"message": "Bank account deleted successfully"}


# ========== Template Endpoints ==========
@app.get("/api/templates", response_model=List[schemas.Template])
def get_templates(template_type: Optional[str] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_templates(db, template_type=template_type, skip=skip, limit=limit)


@app.get("/api/templates/{template_id}", response_model=schemas.Template)
def get_template(template_id: int, db: Session = Depends(get_db)):
    template = crud.get_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@app.post("/api/templates", response_model=schemas.Template)
def create_template(template: schemas.TemplateCreate, db: Session = Depends(get_db)):
    return crud.create_template(db, template)


@app.put("/api/templates/{template_id}", response_model=schemas.Template)
def update_template(template_id: int, template: schemas.TemplateUpdate, db: Session = Depends(get_db)):
    updated = crud.update_template(db, template_id, template)
    if not updated:
        raise HTTPException(status_code=404, detail="Template not found")
    return updated


@app.delete("/api/templates/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    if not crud.delete_template(db, template_id):
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template deleted successfully"}


# ========== File Upload Endpoints ==========
@app.post("/api/upload/parse", response_model=schemas.FileUploadResponse)
async def parse_uploaded_file(file: UploadFile = File(...)):
    """Parse uploaded Excel/DAT file and return preview"""
    try:
        # Save uploaded file temporarily
        temp_path = f"{UPLOAD_DIR}/temp_{datetime.now().timestamp()}_{file.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Parse file
        df, columns, row_count = services.parse_excel_file(temp_path)

        # Generate preview (first 10 rows)
        preview = df.head(10).to_dict('records')

        # Clean up temp file
        os.remove(temp_path)

        return {
            "filename": file.filename,
            "columns": columns,
            "row_count": row_count,
            "preview": preview
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing file: {str(e)}")


# ========== Shift Report Endpoints ==========
@app.get("/api/reports/shift", response_model=List[schemas.ShiftReport])
def get_shift_reports(driver_id: Optional[int] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_shift_reports(db, driver_id=driver_id, skip=skip, limit=limit)


@app.get("/api/reports/shift/{report_id}", response_model=schemas.ShiftReport)
def get_shift_report(report_id: int, db: Session = Depends(get_db)):
    report = crud.get_shift_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Shift report not found")
    return report


@app.post("/api/reports/shift", response_model=schemas.ShiftReport)
async def create_shift_report(
    file: UploadFile = File(...),
    driver_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    """Create a new shift report from uploaded file"""
    try:
        # Save uploaded file
        file_path = f"{UPLOAD_DIR}/{datetime.now().timestamp()}_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Parse file
        df, columns, row_count = services.parse_excel_file(file_path)

        # Calculate summary
        summary = services.calculate_shift_summary(df)

        # Convert dataframe to dict for storage
        data = df.to_dict('records')

        # Create report
        report_create = schemas.ShiftReportCreate(
            driver_id=driver_id,
            file_name=file.filename,
            report_date=datetime.now(),
            data={"rows": data, "columns": columns},
            summary=summary
        )

        report = crud.create_shift_report(db, report_create)
        return report

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating shift report: {str(e)}")


@app.post("/api/reports/shift/{report_id}/edits", response_model=schemas.ShiftEdit)
def create_shift_edit(report_id: int, edit: schemas.ShiftEditCreate, db: Session = Depends(get_db)):
    """Add an edit to a shift report"""
    report = crud.get_shift_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Shift report not found")

    return crud.create_shift_edit(db, report_id, edit)


@app.delete("/api/reports/shift/{report_id}")
def delete_shift_report(report_id: int, db: Session = Depends(get_db)):
    if not crud.delete_shift_report(db, report_id):
        raise HTTPException(status_code=404, detail="Shift report not found")
    return {"message": "Shift report deleted successfully"}


# ========== Salary Report Endpoints ==========
@app.get("/api/reports/salary", response_model=List[schemas.SalaryReport])
def get_salary_reports(driver_id: Optional[int] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_salary_reports(db, driver_id=driver_id, skip=skip, limit=limit)


@app.get("/api/reports/salary/{report_id}", response_model=schemas.SalaryReport)
def get_salary_report(report_id: int, db: Session = Depends(get_db)):
    report = crud.get_salary_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Salary report not found")
    return report


@app.post("/api/reports/salary", response_model=schemas.SalaryReport)
async def create_salary_report(
    driver_id: int = Form(...),
    files: List[UploadFile] = File(...),
    report_period: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Create a new salary report from uploaded files"""
    try:
        # Get driver info
        driver = crud.get_driver(db, driver_id)
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")

        # Parse all files and combine data
        all_data = []
        file_names = []

        for file in files:
            # Save uploaded file
            file_path = f"{UPLOAD_DIR}/{datetime.now().timestamp()}_{file.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Parse file
            df, _, _ = services.parse_excel_file(file_path)

            # Filter by driver if needed
            df = services.filter_dataframe_by_driver(df, driver.driver_id)

            all_data.append(df)
            file_names.append(file.filename)

        # Combine all dataframes
        import pandas as pd
        combined_df = pd.concat(all_data, ignore_index=True)

        # Calculate salary
        salary_calc = services.calculate_salary(combined_df, driver.commission_percentage)

        # Create report
        report_create = schemas.SalaryReportCreate(
            driver_id=driver_id,
            report_period=report_period or datetime.now().strftime("%B %Y"),
            file_names=file_names,
            gross_salary=salary_calc["gross_salary"],
            commission_percentage=salary_calc["commission_percentage"],
            net_salary=salary_calc["net_salary"],
            cash_amount=salary_calc["cash_amount"],
            tips=salary_calc["tips"],
            data={"rows": combined_df.to_dict('records'), "breakdown": salary_calc["breakdown"]}
        )

        report = crud.create_salary_report(db, report_create)
        return report

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating salary report: {str(e)}")


@app.delete("/api/reports/salary/{report_id}")
def delete_salary_report(report_id: int, db: Session = Depends(get_db)):
    if not crud.delete_salary_report(db, report_id):
        raise HTTPException(status_code=404, detail="Salary report not found")
    return {"message": "Salary report deleted successfully"}


# ========== PDF Generation Endpoints ==========
@app.post("/api/reports/shift/{report_id}/pdf")
def generate_shift_pdf(report_id: int, db: Session = Depends(get_db)):
    """Generate PDF for shift report"""
    report = crud.get_shift_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Shift report not found")

    try:
        # Get company info (use first company or default)
        companies = crud.get_companies(db, limit=1)
        company_info = {
            "name": companies[0].name if companies else "Voss Taxi",
            "org_number": companies[0].org_number if companies else "",
            "address": companies[0].address if companies else ""
        }

        # Recreate DataFrame from stored data
        import pandas as pd
        df = pd.DataFrame(report.data.get("rows", []))

        # Generate PDF
        pdf_filename = f"shift_report_{report_id}_{datetime.now().timestamp()}.pdf"
        pdf_path = f"{PDF_DIR}/{pdf_filename}"

        services.generate_shift_pdf(
            pdf_path,
            df,
            report.summary or {},
            company_info,
            [edit.__dict__ for edit in report.edits] if report.edits else []
        )

        # Update report with PDF path
        report.pdf_path = pdf_path
        db.commit()

        return FileResponse(pdf_path, media_type="application/pdf", filename=pdf_filename)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")


@app.post("/api/reports/salary/{report_id}/pdf")
def generate_salary_pdf(report_id: int, db: Session = Depends(get_db)):
    """Generate PDF for salary report"""
    report = crud.get_salary_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Salary report not found")

    try:
        # Get driver info
        driver = crud.get_driver(db, report.driver_id)
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")

        # Get company info
        companies = crud.get_companies(db, limit=1)
        company_info = {
            "name": companies[0].name if companies else "Voss Taxi",
            "org_number": companies[0].org_number if companies else "",
            "address": companies[0].address if companies else ""
        }

        driver_info = {
            "name": driver.name,
            "driver_id": driver.driver_id
        }

        salary_data = {
            "gross_salary": report.gross_salary,
            "commission_percentage": report.commission_percentage,
            "net_salary": report.net_salary,
            "cash_amount": report.cash_amount,
            "tips": report.tips
        }

        # Generate PDF
        pdf_filename = f"salary_report_{report_id}_{datetime.now().timestamp()}.pdf"
        pdf_path = f"{PDF_DIR}/{pdf_filename}"

        services.generate_salary_pdf(pdf_path, salary_data, driver_info, company_info)

        # Update report with PDF path
        report.pdf_path = pdf_path
        db.commit()

        return FileResponse(pdf_path, media_type="application/pdf", filename=pdf_filename)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
