import pandas as pd
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from fpdf import FPDF


def safe_float(val) -> float:
    """Convert value to float safely, handling various edge cases"""
    try:
        if pd.isna(val) or val is None or val == '' or str(val).lower() == 'nan':
            return 0.0
        return float(str(val).replace(",", ".").replace(" ", ""))
    except Exception:
        return 0.0


# Column finding utilities
def find_loyve_column(df: pd.DataFrame) -> Optional[str]:
    """Find the løyve (license) column in dataframe"""
    if df is None:
        return None
    for col in df.columns:
        if str(col).strip().lower() in ["løyve", "loyve"]:
            return col
    return None


def find_kontant_column(df: pd.DataFrame) -> Optional[str]:
    """Find the kontant (cash) column in dataframe"""
    if df is None:
        return None
    for col in df.columns:
        if str(col).strip().lower() == "kontant":
            return col
    for col in df.columns:
        if "kontant" in str(col).strip().lower():
            return col
    return None


def find_bomtur_column(df: pd.DataFrame) -> Optional[str]:
    """Find the bomtur (toll) column in dataframe"""
    if df is None:
        return None
    for col in df.columns:
        if "bomtur" in str(col).lower():
            return col
    return None


def find_kreditt_column(df: pd.DataFrame) -> Optional[str]:
    """Find the kreditt (credit) column in dataframe"""
    if df is None:
        return None
    for col in df.columns:
        if "kreditt" in str(col).lower():
            return col
    return None


def find_subtotal_column(df: pd.DataFrame) -> Optional[str]:
    """Find the subtotal column in dataframe"""
    if df is None:
        return None
    for col in df.columns:
        if "sub_total" in str(col).lower() or "subtotal" in str(col).lower():
            return col
    return None


def find_tips_column(df: pd.DataFrame) -> Optional[str]:
    """Find the tips column in dataframe"""
    if df is None:
        return None
    for col in df.columns:
        if "kreditt_tips" in str(col).lower():
            return col
    for col in df.columns:
        if "tips" in str(col).lower():
            return col
    return None


def is_sjaafor_column(colname: str) -> bool:
    """Check if column is a driver/shift number column"""
    c = colname.lower()
    return ("skiftnr" in c or "sjaafor" in c or "sjåfør" in c or "sjafor" in c)


def is_date_column(colname: str) -> bool:
    """Check if column is a date column"""
    return str(colname).lower().startswith("start_dato") or str(colname).lower().startswith("slutt_dato")


# File parsing
def parse_excel_file(file_path: str) -> Tuple[pd.DataFrame, List[str], int]:
    """Parse Excel or DAT file and return DataFrame, columns, and row count"""
    try:
        # Try reading as Excel first
        df = pd.read_excel(file_path)
    except Exception:
        # If Excel fails, try as CSV/DAT with various encodings
        encodings = ['utf-8', 'iso-8859-1', 'cp1252']
        df = None
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, sep='\t', encoding=encoding)
                break
            except Exception:
                try:
                    df = pd.read_csv(file_path, sep=',', encoding=encoding)
                    break
                except Exception:
                    continue

        if df is None:
            raise ValueError("Could not parse file with any known format")

    # Clean up column names
    df.columns = [str(col).strip() for col in df.columns]

    return df, list(df.columns), len(df)


def calculate_shift_summary(df: pd.DataFrame) -> Dict[str, float]:
    """Calculate summary statistics for shift report"""
    kontant_col = find_kontant_column(df)
    kreditt_col = find_kreditt_column(df)
    bomtur_col = find_bomtur_column(df)

    summary = {
        "total_kontant": 0.0,
        "total_kreditt": 0.0,
        "total_bomtur": 0.0,
        "grand_total": 0.0
    }

    if kontant_col:
        summary["total_kontant"] = df[kontant_col].apply(safe_float).sum()

    if kreditt_col:
        summary["total_kreditt"] = df[kreditt_col].apply(safe_float).sum()

    if bomtur_col:
        summary["total_bomtur"] = df[bomtur_col].apply(safe_float).sum()

    summary["grand_total"] = summary["total_kontant"] + summary["total_kreditt"]

    return summary


def filter_dataframe_by_driver(df: pd.DataFrame, driver_id: str) -> pd.DataFrame:
    """Filter dataframe to only include rows for a specific driver"""
    if df is None or driver_id is None:
        return df

    # Try to find driver/shift column
    for col in df.columns:
        if is_sjaafor_column(col):
            # Filter rows where this column contains the driver_id
            mask = df[col].astype(str).str.contains(driver_id, na=False)
            return df[mask].copy()

    return df


def calculate_salary(df: pd.DataFrame, commission_percentage: float = 45.0) -> Dict[str, Any]:
    """Calculate salary from shift data"""
    subtotal_col = find_subtotal_column(df)
    kontant_col = find_kontant_column(df)
    bomtur_col = find_bomtur_column(df)
    tips_col = find_tips_column(df)

    result = {
        "gross_salary": 0.0,
        "commission_percentage": commission_percentage,
        "net_salary": 0.0,
        "cash_amount": 0.0,
        "tips": 0.0,
        "total_bomtur": 0.0,
        "breakdown": {}
    }

    # Calculate gross salary from subtotals
    if subtotal_col:
        gross = df[subtotal_col].apply(safe_float).sum()
        result["gross_salary"] = gross
        result["net_salary"] = gross * (commission_percentage / 100.0)

    # Calculate cash amount (kontant - bomtur)
    if kontant_col:
        kontant = df[kontant_col].apply(safe_float).sum()
        result["cash_amount"] = kontant

        if bomtur_col:
            bomtur = df[bomtur_col].apply(safe_float).sum()
            result["total_bomtur"] = bomtur
            result["cash_amount"] = kontant - bomtur

    # Calculate tips
    if tips_col:
        result["tips"] = df[tips_col].apply(safe_float).sum()

    return result


# PDF Generation
class ShiftReportPDF(FPDF):
    """PDF generator for shift reports"""

    def __init__(self, company_info: Dict[str, str]):
        super().__init__()
        self.company_info = company_info

    def header(self):
        """Add header with company info"""
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, self.company_info.get('name', 'Voss Taxi'), 0, 1, 'C')
        self.set_font('Arial', '', 10)
        if self.company_info.get('org_number'):
            self.cell(0, 6, f"Org.nr: {self.company_info['org_number']}", 0, 1, 'C')
        if self.company_info.get('address'):
            self.cell(0, 6, self.company_info['address'], 0, 1, 'C')
        self.ln(5)

    def footer(self):
        """Add footer with page number"""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Side {self.page_no()}', 0, 0, 'C')


def generate_shift_pdf(
    output_path: str,
    df: pd.DataFrame,
    summary: Dict[str, float],
    company_info: Dict[str, str],
    edits: List[Dict[str, Any]] = None
) -> str:
    """Generate PDF for shift report"""
    pdf = ShiftReportPDF(company_info)
    pdf.add_page()

    # Title
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Skiftrapport', 0, 1, 'L')
    pdf.ln(5)

    # Summary section
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Sammendrag:', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 6, f"Total Kontant: {summary.get('total_kontant', 0):.2f} kr", 0, 1)
    pdf.cell(0, 6, f"Total Kreditt: {summary.get('total_kreditt', 0):.2f} kr", 0, 1)
    pdf.cell(0, 6, f"Total Bomtur: {summary.get('total_bomtur', 0):.2f} kr", 0, 1)
    pdf.cell(0, 6, f"Totalt: {summary.get('grand_total', 0):.2f} kr", 0, 1)
    pdf.ln(10)

    # Edit log
    if edits and len(edits) > 0:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'Endringer:', 0, 1)
        pdf.set_font('Arial', '', 9)
        for edit in edits:
            timestamp = edit.get('timestamp', '')
            note = edit.get('note', 'Ingen merknad')
            pdf.cell(0, 5, f"- {timestamp}: {note}", 0, 1)
        pdf.ln(5)

    # Data table (simplified - would need proper table formatting)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 8, 'Detaljert data:', 0, 1)
    pdf.set_font('Arial', '', 8)
    pdf.cell(0, 5, f"Totalt {len(df)} rader importert", 0, 1)

    pdf.output(output_path)
    return output_path


def generate_salary_pdf(
    output_path: str,
    salary_data: Dict[str, Any],
    driver_info: Dict[str, Any],
    company_info: Dict[str, str]
) -> str:
    """Generate PDF for salary report"""
    pdf = ShiftReportPDF(company_info)
    pdf.add_page()

    # Title
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Lønnsrapport', 0, 1, 'L')
    pdf.ln(5)

    # Driver info
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, f"Sjåfør: {driver_info.get('name', 'N/A')}", 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 6, f"Sjåfør-ID: {driver_info.get('driver_id', 'N/A')}", 0, 1)
    pdf.ln(5)

    # Salary breakdown
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Lønnsdetaljer:', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 6, f"Bruttolønn: {salary_data.get('gross_salary', 0):.2f} kr", 0, 1)
    pdf.cell(0, 6, f"Provisjon: {salary_data.get('commission_percentage', 45)}%", 0, 1)
    pdf.cell(0, 6, f"Nettolønn: {salary_data.get('net_salary', 0):.2f} kr", 0, 1)
    pdf.cell(0, 6, f"Kontant beløp: {salary_data.get('cash_amount', 0):.2f} kr", 0, 1)
    pdf.cell(0, 6, f"Tips: {salary_data.get('tips', 0):.2f} kr", 0, 1)
    pdf.ln(10)

    # Total
    pdf.set_font('Arial', 'B', 12)
    total = salary_data.get('net_salary', 0) + salary_data.get('tips', 0)
    pdf.cell(0, 8, f"Total utbetaling: {total:.2f} kr", 0, 1)

    pdf.output(output_path)
    return output_path
