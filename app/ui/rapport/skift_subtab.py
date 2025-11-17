from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QTableWidget,
    QTableWidgetItem, QLabel, QListWidget, QListWidgetItem, QComboBox, QLineEdit,
    QInputDialog, QMessageBox, QDialog, QFormLayout, QDialogButtonBox, QListView
)
from PySide6.QtCore import Qt
import pandas as pd
import os
import json
from datetime import datetime

try:
    from fpdf import FPDF
except ImportError:
    FPDF = None

EDIT_PATH = os.path.join(os.path.dirname(__file__), "skift_edits.json")

def load_all_edits():
    try:
        with open(EDIT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_all_edits(edits):
    with open(EDIT_PATH, "w", encoding="utf-8") as f:
        json.dump(edits, f, indent=2, ensure_ascii=False)

def safe_float(val):
    try:
        if pd.isna(val) or val is None or val == '' or str(val).lower() == 'nan':
            return 0.0
        return float(str(val).replace(",", ".").replace(" ", ""))
    except Exception:
        return 0.0

def find_loyve_column(df):
    if df is None:
        return None
    for col in df.columns:
        if str(col).strip().lower() in ["løyve", "loyve"]:
            return col
    return None

def find_kontant_column(df):
    if df is None:
        return None
    for col in df.columns:
        if str(col).strip().lower() == "kontant":
            return col
    for col in df.columns:
        if "kontant" in str(col).strip().lower():
            return col
    return None

def find_bomtur_column(df):
    if df is None:
        return None
    for col in df.columns:
        if "bomtur" in str(col).lower():
            return col
    return None

def find_kreditt_column(df):
    if df is None:
        return None
    for col in df.columns:
        if "kreditt" in str(col).lower():
            return col
    return None

def is_sjaafor_column(colname):
    c = colname.lower()
    return ("skiftnr" in c or "sjaafor" in c or "sjåfør" in c or "sjafor" in c)

def is_date_column(colname):
    return str(colname).lower().startswith("start_dato") or str(colname).lower().startswith("slutt_dato")

class SkiftSubTab(QWidget):
    def __init__(self, settings_tab):
        super().__init__()
        self.settings_tab = settings_tab   # <--- add this line!
        self.data = None
        self.file_path = None
        self.current_edits = []
        self.current_template_name = "Standard (alle kolonner)"  # <-- NEW!

        layout = QVBoxLayout()

        # --- File load row ---
        file_row = QHBoxLayout()
        self.load_file_btn = QPushButton("Last inn fil")
        self.load_file_btn.clicked.connect(self.load_file)
        file_row.addWidget(self.load_file_btn)
        self.file_label = QLabel("")
        file_row.addWidget(self.file_label)
        file_row.addStretch()
        layout.addLayout(file_row)

        # --- Edit controls ---
        edit_box = QHBoxLayout()
        edit_box.addWidget(QLabel("Skiftnr:"))
        self.skiftnr_combo = QComboBox()
        edit_box.addWidget(self.skiftnr_combo)
        edit_box.addWidget(QLabel("Løyve:"))
        self.loyve_combo = QComboBox()
        edit_box.addWidget(self.loyve_combo)
        edit_box.addWidget(QLabel("Endre kontant:"))
        self.amount_edit = QLineEdit()
        self.amount_edit.setPlaceholderText("+200 / -150")
        edit_box.addWidget(self.amount_edit)
        edit_box.addWidget(QLabel("Notat:"))
        self.note_edit = QLineEdit()
        edit_box.addWidget(self.note_edit)
        self.add_edit_btn = QPushButton("Legg til endring")
        self.add_edit_btn.clicked.connect(self.add_edit)
        edit_box.addWidget(self.add_edit_btn)
        layout.addLayout(edit_box)

        # --- Edits list ---
        layout.addWidget(QLabel("Endringer for denne filen:"))
        self.edits_list = QListWidget()
        self.edits_list.setSelectionMode(QListWidget.SingleSelection)
        layout.addWidget(self.edits_list)

        edits_btn_row = QHBoxLayout()
        self.edit_selected_btn = QPushButton("Rediger valgt")
        self.edit_selected_btn.clicked.connect(self.edit_selected_edit)
        self.delete_selected_btn = QPushButton("Slett valgt")
        self.delete_selected_btn.clicked.connect(self.delete_selected_edit)
        edits_btn_row.addWidget(self.edit_selected_btn)
        edits_btn_row.addWidget(self.delete_selected_btn)
        edits_btn_row.addStretch()
        layout.addLayout(edits_btn_row)

        # --- Columns selection row ---
        columns_layout = QVBoxLayout()
        check_btns_layout = QHBoxLayout()
        self.check_all_btn = QPushButton("Merk alle")
        self.check_all_btn.clicked.connect(self.check_all_headers)
        self.uncheck_all_btn = QPushButton("Fjern alle")
        self.uncheck_all_btn.clicked.connect(self.uncheck_all_headers)
        check_btns_layout.addWidget(QLabel("Velg kolonner:"))
        check_btns_layout.addWidget(self.check_all_btn)
        check_btns_layout.addWidget(self.uncheck_all_btn)
        check_btns_layout.addStretch()
        columns_layout.addLayout(check_btns_layout)
        self.columns_list = QListWidget()
        self.columns_list.itemChanged.connect(lambda _: self.show_preview())
        columns_layout.addWidget(self.columns_list)
        layout.addLayout(columns_layout)

        # --- Preview table ---
        layout.addWidget(QLabel("Forhåndsvisning:"))
        self.table = QTableWidget()
        layout.addWidget(self.table)

        # --- PDF/Template buttons ---
        btn_row = QHBoxLayout()
        self.generate_pdf_btn = QPushButton("Generer PDF")
        self.generate_pdf_btn.clicked.connect(self.generate_pdf)
        self.template_combo = QComboBox()
        self.template_combo.addItem("Standard (alle kolonner)")
        btn_row.addWidget(QLabel("Mal:"))
        btn_row.addWidget(self.template_combo)
        self.save_template_btn = QPushButton("Lagre mal")
        self.save_template_btn.clicked.connect(self.save_template)
        btn_row.addWidget(self.save_template_btn)
        btn_row.addWidget(self.generate_pdf_btn)
        layout.addLayout(btn_row)

        self.setLayout(layout)
        self.update_template_combo()
        self.template_combo.currentTextChanged.connect(self.apply_template)

    # --- File ops ---
    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Velg fil", "", "Excel Files (*.xlsx);;DAT Files (*.dat);;All Files (*)"
        )
        if not file_path:
            return
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == ".xlsx":
                df = pd.read_excel(file_path)
            elif ext == ".dat":
                try:
                    df = pd.read_csv(file_path, sep=None, engine="python")
                except Exception:
                    df = pd.read_csv(file_path, delimiter=";")
            else:
                return
            self.data = df
            self.file_path = file_path
            self.file_label.setText(os.path.basename(file_path))
            self.refresh_skiftnr_and_loyve_combo()
            self.load_relevant_edits()
            self.update_columns()
            self.apply_template(self.current_template_name)  # <-- auto-apply current template
        except Exception as e:
            QMessageBox.warning(self, "Feil", f"Kunne ikke lese fil: {os.path.basename(file_path)}\n{e}")

    def refresh_skiftnr_and_loyve_combo(self):
        self.skiftnr_combo.clear()
        self.loyve_combo.clear()
        if self.data is not None:
            if "Skiftnr" in self.data.columns:
                unique_vals = [str(val) for val in self.data["Skiftnr"].dropna().unique()]
                for val in unique_vals:
                    self.skiftnr_combo.addItem(val)
            loyve_col = find_loyve_column(self.data)
            if loyve_col:
                unique_vals = [str(val) for val in self.data[loyve_col].dropna().unique()]
                for val in unique_vals:
                    self.loyve_combo.addItem(val)

    def load_relevant_edits(self):
        all_edits = load_all_edits()
        file_keys = set()
        loyve_col = find_loyve_column(self.data)
        if self.data is not None and loyve_col and "Skiftnr" in self.data.columns:
            for _, row in self.data.iterrows():
                file_keys.add((str(row["Skiftnr"]).strip(), str(row[loyve_col]).strip()))
        self.current_edits = [e for e in all_edits if (str(e["skiftnr"]).strip(), str(e["loyve"]).strip()) in file_keys]
        self.refresh_edits_list()

    # --- Edits logic ---
    def add_edit(self):
        skiftnr = self.skiftnr_combo.currentText()
        loyve = self.loyve_combo.currentText()
        try:
            amount = safe_float(self.amount_edit.text())
        except Exception:
            QMessageBox.warning(self, "Feil", "Ugyldig beløp.")
            return
        note = self.note_edit.text().strip()
        if not skiftnr or not loyve:
            QMessageBox.warning(self, "Feil", "Velg både Skiftnr og Løyve.")
            return
        all_edits = load_all_edits()
        all_edits.append({
            "skiftnr": str(skiftnr).strip(),
            "loyve": str(loyve).strip(),
            "amount": amount,
            "note": note,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        save_all_edits(all_edits)
        self.load_relevant_edits()
        self.amount_edit.clear()
        self.note_edit.clear()

    def refresh_edits_list(self):
        self.edits_list.clear()
        for edit in self.current_edits:
            summary = f"Skiftnr {edit['skiftnr']} / Løyve {edit['loyve']}: kontant {'+' if edit['amount'] >= 0 else ''}{edit['amount']} kr"
            if edit["note"]:
                summary += f" | Notat: {edit['note']}"
            summary += f" ({edit['timestamp']})"
            self.edits_list.addItem(summary)
        self.show_preview()

    def edit_selected_edit(self):
        idx = self.edits_list.currentRow()
        if idx < 0:
            return
        edit = self.current_edits[idx]
        new_amount, ok = QInputDialog.getDouble(self, "Rediger beløp", "Nytt beløp:", edit["amount"])
        if not ok:
            return
        new_note, ok2 = QInputDialog.getText(self, "Rediger notat", "Notat:", text=edit["note"])
        if not ok2:
            return
        all_edits = load_all_edits()
        for stored_edit in all_edits:
            if (str(stored_edit["skiftnr"]).strip() == str(edit["skiftnr"]).strip()
                and str(stored_edit["loyve"]).strip() == str(edit["loyve"]).strip()
                and stored_edit.get("timestamp") == edit.get("timestamp")):
                stored_edit["amount"] = new_amount
                stored_edit["note"] = new_note
                stored_edit["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_all_edits(all_edits)
        self.load_relevant_edits()

    def delete_selected_edit(self):
        idx = self.edits_list.currentRow()
        if idx < 0:
            return
        edit = self.current_edits[idx]
        all_edits = load_all_edits()
        all_edits = [
            e for e in all_edits
            if not (
                str(e["skiftnr"]).strip() == str(edit["skiftnr"]).strip()
                and str(e["loyve"]).strip() == str(edit["loyve"]).strip()
                and e.get("timestamp") == edit.get("timestamp")
            )
        ]
        save_all_edits(all_edits)
        self.load_relevant_edits()

    # --- Columns checkboxes ---
    def update_columns(self):
        self.columns_list.blockSignals(True)
        self.columns_list.clear()
        df = self.get_edited_data()
        if df is not None and not df.empty:
            for col in df.columns:
                item = QListWidgetItem(str(col))
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Checked)
                self.columns_list.addItem(item)
        self.columns_list.blockSignals(False)
        self.show_preview()

    def check_all_headers(self):
        self.columns_list.blockSignals(True)
        for i in range(self.columns_list.count()):
            self.columns_list.item(i).setCheckState(Qt.Checked)
        self.columns_list.blockSignals(False)
        self.show_preview()

    def uncheck_all_headers(self):
        self.columns_list.blockSignals(True)
        for i in range(self.columns_list.count()):
            self.columns_list.item(i).setCheckState(Qt.Unchecked)
        self.columns_list.blockSignals(False)
        self.show_preview()

    def get_checked_columns(self):
        checked = []
        for i in range(self.columns_list.count()):
            item = self.columns_list.item(i)
            if item and item.checkState() == Qt.Checked:
                checked.append(item.text())
        return checked

    # --- Preview table, showing edits applied ---
    def get_edited_data(self):
        if self.data is None:
            return None
        df = self.data.copy()
        loyve_col = find_loyve_column(df)
        kontant_col = find_kontant_column(df)
        if loyve_col and "Skiftnr" in df.columns and kontant_col:
            edit_map = {}
            for edit in self.current_edits:
                k = (str(edit["skiftnr"]).strip(), str(edit["loyve"]).strip())
                edit_map.setdefault(k, 0)
                edit_map[k] += safe_float(edit["amount"])
            for (edit_skiftnr, edit_loyve), total_add in edit_map.items():
                idxs = df.index[
                    (df["Skiftnr"].astype(str).str.strip() == edit_skiftnr) &
                    (df[loyve_col].astype(str).str.strip() == edit_loyve)
                ]
                if len(idxs) > 0:
                    i = idxs[0]
                    orig_val = safe_float(df.at[i, kontant_col])
                    df.at[i, kontant_col] = orig_val + total_add
        return df

    def show_preview(self, max_rows=10):
        df = self.get_edited_data()
        if df is None or df.empty:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            return
        checked_columns = self.get_checked_columns()
        checked_columns = [col for col in checked_columns if col in df.columns]
        if not checked_columns:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            return
        self.table.setRowCount(min(max_rows, len(df)))
        self.table.setColumnCount(len(checked_columns))
        self.table.setHorizontalHeaderLabels([str(col) for col in checked_columns])
        for i, row in df[checked_columns].head(max_rows).iterrows():
            for j, value in enumerate(row):
                colname = checked_columns[j]
                if is_sjaafor_column(colname):
                    try:
                        sval = str(int(float(value)))
                    except Exception:
                        sval = str(value)
                elif is_date_column(colname):
                    try:
                        dt = pd.to_datetime(value)
                        sval = dt.strftime('%Y-%m-%d')
                    except Exception:
                        sval = str(value)
                else:
                    try:
                        fval = float(value)
                        sval = "{:,.2f}".format(fval).replace(",", " ").replace(".", ",")
                    except Exception:
                        sval = str(value)
                self.table.setItem(i, j, QTableWidgetItem(sval))

    # --- Templates ---
    def template_file_path(self):
        return os.path.join(os.path.dirname(__file__), "skift_templates.json")

    def load_templates(self):
        try:
            with open(self.template_file_path(), "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def save_templates(self, templates):
        with open(self.template_file_path(), "w", encoding="utf-8") as f:
            json.dump(templates, f, indent=2, ensure_ascii=False)

    def update_template_combo(self):
        self.template_combo.blockSignals(True)
        current = self.template_combo.currentText()
        self.template_combo.clear()
        self.template_combo.addItem("Standard (alle kolonner)")
        for tpl in self.load_templates():
            self.template_combo.addItem(tpl["name"])
        if current:
            idx = self.template_combo.findText(current)
            if idx >= 0:
                self.template_combo.setCurrentIndex(idx)
        self.template_combo.blockSignals(False)

    def save_template(self):
        checked = self.get_checked_columns()
        if not checked:
            QMessageBox.warning(self, "Ingen kolonner", "Du må velge minst én kolonne for å lagre en mal.")
            return
        name, ok = QInputDialog.getText(self, "Lagre mal", "Navn på mal:")
        if not ok or not name.strip():
            return
        templates = self.load_templates()
        for tpl in templates:
            if tpl["name"] == name:
                tpl["columns"] = checked
                break
        else:
            templates.append({"name": name, "columns": checked})
        self.save_templates(templates)
        self.update_template_combo()
        QMessageBox.information(self, "Mal lagret", f"Mal '{name}' lagret.")

    def update_template_combo(self):
        self.template_combo.blockSignals(True)
        current = self.template_combo.currentText() or self.current_template_name
        self.template_combo.clear()
        self.template_combo.addItem("Standard (alle kolonner)")
        for tpl in self.load_templates():
            self.template_combo.addItem(tpl["name"])
        if current:
            idx = self.template_combo.findText(current)
            if idx >= 0:
                self.template_combo.setCurrentIndex(idx)
                self.current_template_name = current
        self.template_combo.blockSignals(False)

    def apply_template(self, name):
        self.current_template_name = name
        if self.data is None or self.columns_list.count() == 0:
            return
        self.columns_list.blockSignals(True)
        if name == "Standard (alle kolonner)":
            for i in range(self.columns_list.count()):
                self.columns_list.item(i).setCheckState(Qt.Checked)
        else:
            selected = set()
            for tpl in self.load_templates():
                if tpl["name"] == name:
                    selected = set(tpl["columns"])
                    break
            for i in range(self.columns_list.count()):
                col = self.columns_list.item(i).text()
                self.columns_list.item(i).setCheckState(
                    Qt.Checked if col in selected else Qt.Unchecked
                )
        self.columns_list.blockSignals(False)
        self.show_preview()

    def extract_year_month_loyve_from_data(self):
        year = ""
        month = ""
        loyve = ""
        if self.data is not None:
            # 1. Find Start_dato tid
            date_col = None
            for col in self.data.columns:
                if str(col).lower().replace(" ", "_").startswith("start_dato"):
                    date_col = col
                    break
            # 2. Parse date
            if date_col and not self.data[date_col].isnull().all():
                try:
                    first_date = pd.to_datetime(self.data[date_col].dropna().iloc[0])
                    year = str(first_date.year)
                    month = str(first_date.month)
                except Exception:
                    pass
            # 3. Løyve
            loyve_col = find_loyve_column(self.data)
            if loyve_col and len(self.data) > 0:
                loyve = str(self.data[loyve_col].iloc[0])
        # Fallbacks from filename if needed
        import re
        if not year and self.file_path:
            m = re.search(r"20\d\d", self.file_path)
            if m:
                year = m.group(0)
        if not month and self.file_path:
            m = re.search(r"[-_](\d{1,2})", self.file_path)
            if m:
                month = m.group(1)
        # Fallback to now
        if not year:
            year = datetime.now().strftime("%Y")
        if not month:
            month = datetime.now().strftime("%m")
        if not loyve:
            loyve = "unknown"
        return year, month, loyve


    def get_report_info_dialog(self, default_year, default_month, default_loyve, default_name):
        months = [
            "Januar", "Februar", "Mars", "April", "Mai", "Juni",
            "Juli", "August", "September", "Oktober", "November", "Desember"
        ]
        dialog = QDialog(self)
        layout = QFormLayout(dialog)
        year_edit = QLineEdit(str(default_year))
        month_combo = QComboBox()
        month_combo.addItems(months)
        # Support both number and text
        idx = -1
        try:
            # If numeric
            month_idx = int(default_month) - 1
            if 0 <= month_idx < 12: idx = month_idx
        except Exception:
            # If name
            try:
                idx = [m.lower() for m in months].index(default_month.lower())
            except Exception:
                pass
        if idx >= 0: month_combo.setCurrentIndex(idx)
        loyve_edit = QLineEdit(str(default_loyve))
        loyve_edit.setReadOnly(True)
        name_edit = QLineEdit(default_name)
        layout.addRow("År:", year_edit)
        layout.addRow("Måned:", month_combo)
        layout.addRow("Løyve:", loyve_edit)
        layout.addRow("Navn på rapport:", name_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        dialog.setLayout(layout)
        if dialog.exec() == QDialog.Accepted:
            return year_edit.text().strip(), month_combo.currentText().strip(), loyve_edit.text().strip(), name_edit.text().strip()
        return None, None, None, None

    def get_first_last_skiftnr(self):
        df = self.get_edited_data()
        if df is not None and "Skiftnr" in df.columns and not df.empty:
            nums = [int(float(x)) for x in df["Skiftnr"].dropna().unique()]
            if nums:
                nums = sorted(nums)
                return nums[0], nums[-1]
        return "", ""

    def generate_pdf(self):
        df = self.get_edited_data()
        checked = self.get_checked_columns()
        checked = [col for col in checked if isinstance(col, str) and col in (df.columns if df is not None else [])]
        if not checked:
            QMessageBox.warning(self, "Ingen kolonner", "Du må velge minst én kolonne for å generere PDF.")
            return
        if df is None or df.empty:
            QMessageBox.warning(self, "Ingen data", "Ingen data å eksportere.")
            return
        if FPDF is None:
            QMessageBox.critical(self, "Mangler fpdf", "Modulen fpdf mangler! Installer med: pip install fpdf")
            return

        # --- Get year, month, løyve (for filename) ---
        year, month, loyve = self.extract_year_month_loyve_from_data()
        months_nb = ["", "Januar", "Februar", "Mars", "April", "Mai", "Juni",
            "Juli", "August", "September", "Oktober", "November", "Desember"]
        try:
            if month.isdigit():
                month_str = months_nb[int(month)]
            else:
                month_str = month
        except Exception:
            month_str = month

        # Ask for report name/confirm month as pulldown
        suggested_name = f"Skift rapport {month_str} {year}"
        year_input, month_input, loyve_input, name = self.get_report_info_dialog(year, month_str, loyve, suggested_name)
        if not (year_input and month_input and loyve_input and name):
            return

        # Make file name with year, month (as number), løyve and report name
        month_number = ""
        for i, m in enumerate(months_nb):
            if m.lower() == month_input.lower():
                month_number = str(i).zfill(2)
                break
        if not month_number and month_input.isdigit():
            month_number = str(int(month_input)).zfill(2)
        filename = f"{name.strip()}_{year_input}-{month_number}-Løyve{loyve_input}.pdf"

        save_dir = os.path.join(os.path.expanduser("~"), "TaxiRapport", "reports", "skift", str(year_input))
        os.makedirs(save_dir, exist_ok=True)
        pdf_path = os.path.join(save_dir, filename)

        font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")
        if not os.path.isfile(font_path):
            QMessageBox.critical(self, "Mangler font", f"Finner ikke fontfilen {font_path}!\nLast ned DejaVuSans.ttf og legg den i samme mappe.")
            return

        pdf = FPDF(orientation='L', unit='mm', format='A4')
        pdf.add_page()
        pdf.add_font('DejaVu', '', font_path, uni=True)
        pdf.add_font('DejaVu', 'B', font_path, uni=True)
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font('DejaVu', '', 11)

        # --- Company info block (top left) ---
        company = self.settings_tab.get_company_info() if hasattr(self.settings_tab, "get_company_info") else {}
        company_name = company.get("name", "")
        company_orgnr = company.get("orgnr", "")
        company_addr = company.get("address", "")

        pdf.set_xy(pdf.l_margin, pdf.get_y())
        pdf.set_font('DejaVu', 'B', 13)
        if company_name:
            pdf.cell(100, 7, company_name, ln=1)
        pdf.set_font('DejaVu', '', 11)
        if company_orgnr:
            pdf.cell(100, 6, f"Org.nr: {company_orgnr}", ln=1)
        if company_addr:
            pdf.cell(100, 6, company_addr, ln=1)
        curr_y = pdf.get_y()

        # Draw a thin grey line under address, full page width
        pdf.set_draw_color(200, 200, 200)
        line_y = curr_y + 2
        pdf.set_line_width(0.4)
        pdf.line(pdf.l_margin, line_y, pdf.w - pdf.l_margin, line_y)
        pdf.set_draw_color(0, 0, 0)
        pdf.ln(8)  # Padding below line

        # --- SUMMARY BLOCK (top, below company info) ---
        kontant_col = find_kontant_column(df)
        kreditt_col = find_kreditt_column(df)
        bomtur_col = find_bomtur_column(df)

        total_kontant = df[kontant_col].apply(safe_float).sum() if kontant_col else 0
        total_kreditt = df[kreditt_col].apply(safe_float).sum() if kreditt_col else 0
        total_bomtur = df[bomtur_col].apply(safe_float).sum() if bomtur_col else 0

        def nf(val):
            if isinstance(val, float) and val.is_integer():
                return "{:,.0f}".format(val).replace(",", " ")
            return "{:,.2f}".format(val).replace(",", " ").replace(".", ",")

        pdf.set_font('DejaVu', 'B', 12)
        summary_line = (
            f"Total Kreditt: {nf(total_kreditt)} kr     "
            f"Total Kontant: {nf(total_kontant)} kr     "
            f"Bomtur: {nf(total_bomtur)} kr"
        )
        pdf.set_fill_color(236, 240, 246)
        pdf.cell(0, 12, summary_line, ln=1, fill=True)
        pdf.ln(2)

        # Horizontal info line with Skiftnr range, not report name
        first_skiftnr, last_skiftnr = self.get_first_last_skiftnr()
        pdf.set_font('DejaVu', '', 11)
        info = f"År: {year_input}     Måned: {month_input}     Løyve: {loyve_input}     Skiftnr: {first_skiftnr} – {last_skiftnr}"
        pdf.cell(0, 10, info, ln=1)
        pdf.ln(2)

        # --- Table: shrink-to-fit, always readable ---
        table_width = pdf.w - 2 * pdf.l_margin
        n_cols = len(checked)
        col_width = table_width / n_cols if n_cols > 0 else table_width

        max_strs = []
        for i, col in enumerate(checked):
            col_lc = str(col).lower()
            strings = [str(col)]
            for val in df[col]:
                if is_sjaafor_column(col):
                    try:
                        sval = str(int(float(val)))
                    except Exception:
                        sval = str(val)
                elif is_date_column(col):
                    try:
                        dt = pd.to_datetime(val)
                        sval = dt.strftime('%Y-%m-%d')
                    except Exception:
                        sval = str(val)
                else:
                    try:
                        fval = float(val)
                        sval = "{:,.2f}".format(fval).replace(",", " ").replace(".", ",")
                    except Exception:
                        sval = str(val)
                strings.append(sval)
            max_strs.append(strings)

        font_size = 11
        while font_size > 4:
            pdf.set_font('DejaVu', 'B', font_size)
            ok = True
            for i, strings in enumerate(max_strs):
                widest = max([pdf.get_string_width(s) for s in strings]) + 1.5
                if widest > col_width:
                    ok = False
                    break
            if ok:
                break
            font_size -= 1

        pdf.set_font('DejaVu', 'B', font_size)
        for i, col in enumerate(checked):
            pdf.cell(col_width, 10, str(col), border=1, align='C')
        pdf.ln()

        pdf.set_font('DejaVu', '', font_size)
        for idx, row in df[checked].iterrows():
            for j, val in enumerate(row):
                colname = checked[j]
                if is_sjaafor_column(colname):
                    try:
                        sval = str(int(float(val)))
                    except Exception:
                        sval = str(val)
                elif is_date_column(colname):
                    try:
                        dt = pd.to_datetime(val)
                        sval = dt.strftime('%Y-%m-%d')
                    except Exception:
                        sval = str(val)
                else:
                    try:
                        fval = float(val)
                        sval = "{:,.2f}".format(fval).replace(",", " ").replace(".", ",")
                    except Exception:
                        sval = str(val)
                align = 'R' if pd.api.types.is_numeric_dtype(df[checked[j]]) else 'C'
                pdf.cell(col_width, 8, sval, border=1, align=align)
            pdf.ln()

        # --- Totals row ---
        pdf.set_font('DejaVu', 'B', font_size)
        has_totals = False
        totals = []
        for col in checked:
            if is_sjaafor_column(col):
                totals.append("")
                continue
            try:
                numeric_vals = pd.to_numeric(df[col], errors="coerce")
                valid = numeric_vals.notnull().sum()
                total_rows = len(df[col])
                if valid >= 0.8 * total_rows and total_rows > 0:
                    tot = numeric_vals.sum()
                    has_totals = True
                    totals.append(tot)
                else:
                    totals.append("")
            except Exception:
                totals.append("")
        if has_totals:
            for i, val in enumerate(totals):
                sval = ""
                if val != "":
                    sval = "{:,.2f}".format(val).replace(",", " ").replace(".", ",") if not float(val).is_integer() else "{:,.0f}".format(val).replace(",", " ")
                pdf.cell(col_width, 8, sval, border=1, align='R')
            pdf.ln()

        # --- Edits log at the end ---
        if self.current_edits:
            pdf.ln(5)
            pdf.set_font('DejaVu', 'B', font_size)
            pdf.cell(0, 8, "Endringslogg:", ln=1)
            pdf.set_font('DejaVu', '', font_size)
            for edit in self.current_edits:
                logmsg = (f"[{edit['timestamp']}] Skiftnr {edit['skiftnr']} / Løyve {edit['loyve']}: "
                        f"kontant {'+' if edit['amount'] >= 0 else ''}{edit['amount']} kr")
                if edit['note']:
                    logmsg += f" Notat: {edit['note']}"
                pdf.multi_cell(0, 8, logmsg)

        try:
            pdf.output(pdf_path)
            QMessageBox.information(self, "PDF lagret", f"PDF lagret til:\n{pdf_path}")
        except Exception as e:
            QMessageBox.critical(self, "Feil ved lagring", str(e))