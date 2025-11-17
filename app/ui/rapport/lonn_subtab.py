from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QLabel, QListWidget, QListWidgetItem, QComboBox,
    QInputDialog, QMessageBox, QDialog, QFormLayout, QDialogButtonBox, QLineEdit, QFileDialog, QListView
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

def find_subtotal_column(df):
    if df is None:
        return None
    for col in df.columns:
        if "sub_total" in str(col).lower() or "subtotal" in str(col).lower():
            return col
    return None

def find_tips_column(df):
    if df is None:
        return None
    for col in df.columns:
        if "kreditt_tips" in str(col).lower():
            return col
    for col in df.columns:
        if "tips" in str(col).lower():
            return col
    return None

def safe_float(val):
    try:
        if pd.isna(val) or val is None or val == '' or str(val).lower() == 'nan':
            return 0.0
        return float(str(val).replace(",", ".").replace(" ", ""))
    except Exception:
        return 0.0

def apply_kontant_edits(df, all_edits):
    df = df.copy()
    loyve_col = find_loyve_column(df)
    kontant_col = find_kontant_column(df)
    if "Skiftnr" in df.columns and loyve_col and kontant_col:
        for edit in all_edits:
            idxs = df.index[
                (df["Skiftnr"].astype(str) == str(edit["skiftnr"])) &
                (df[loyve_col].astype(str) == str(edit["loyve"]))
            ]
            for i in idxs:
                try:
                    old = safe_float(df.at[i, kontant_col])
                except Exception:
                    old = 0.0
                try:
                    df.at[i, kontant_col] = old + safe_float(edit["amount"])
                except Exception:
                    continue
    return df

def edits_for_file(df):
    loyve_col = find_loyve_column(df)
    if "Skiftnr" not in df.columns or loyve_col is None:
        return []
    file_keys = set()
    for _, row in df.iterrows():
        file_keys.add((str(row["loyve"] if "loyve" in row else row[loyve_col]), str(row["Skiftnr"])))
    all_edits = load_all_edits()
    relevant = []
    for edit in all_edits:
        if (str(edit["loyve"]), str(edit["skiftnr"])) in file_keys:
            relevant.append(edit)
    return relevant

class LonnSubTab(QWidget):
    def __init__(self, settings_tab):
        super().__init__()
        self.settings_tab = settings_tab
        self.dataframes = []
        self.file_paths = []
        self.filtered_data = None

        layout = QVBoxLayout()

        # --- File import row ---
        file_row = QHBoxLayout()
        self.add_file_btn = QPushButton("Legg til fil")
        self.add_file_btn.clicked.connect(self.add_file)
        file_row.addWidget(self.add_file_btn)
        self.remove_file_btn = QPushButton("Fjern valgt fil")
        self.remove_file_btn.clicked.connect(self.remove_selected_file)
        file_row.addWidget(self.remove_file_btn)
        file_row.addWidget(QLabel("Filer:"))
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SingleSelection)
        file_row.addWidget(self.file_list)
        layout.addLayout(file_row)

        # --- Driver picker row ---
        driver_row = QHBoxLayout()
        driver_row.addWidget(QLabel("Velg sjåfør:"))
        self.driver_combo = QComboBox()
        driver_row.addWidget(self.driver_combo)
        layout.addLayout(driver_row)

        # --- Salary summary top right ---
        summary_layout = QHBoxLayout()
        summary_layout.addStretch()
        self.summary_box = QLabel()
        self.summary_box.setStyleSheet("font-size:14px; font-weight:bold; padding: 8px; background: #f2f2f2; border-radius:6px;")
        summary_layout.addWidget(self.summary_box)
        layout.addLayout(summary_layout)

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
        btn_row.addWidget(self.generate_pdf_btn)
        self.template_combo = QComboBox()
        btn_row.addWidget(QLabel("Mal:"))
        btn_row.addWidget(self.template_combo)
        self.save_template_btn = QPushButton("Lagre mal")
        self.save_template_btn.clicked.connect(self.save_template)
        btn_row.addWidget(self.save_template_btn)
        layout.addLayout(btn_row)

        # --- Kontant Edit Box ---
        layout.addWidget(QLabel("<b>Korriger kontant (Skiftnr + Løyve):</b>"))
        edit_row = QHBoxLayout()
        self.edit_skiftnr = QLineEdit()
        self.edit_skiftnr.setPlaceholderText("Skiftnr")
        edit_row.addWidget(self.edit_skiftnr)
        self.edit_loyve = QLineEdit()
        self.edit_loyve.setPlaceholderText("Løyve")
        edit_row.addWidget(self.edit_loyve)
        self.edit_amount = QLineEdit()
        self.edit_amount.setPlaceholderText("+ / - beløp")
        edit_row.addWidget(self.edit_amount)
        self.edit_note = QLineEdit()
        self.edit_note.setPlaceholderText("Notat (valgfritt)")
        edit_row.addWidget(self.edit_note)
        self.add_edit_btn = QPushButton("Legg til / Oppdater endring")
        self.add_edit_btn.clicked.connect(self.add_or_update_edit)
        edit_row.addWidget(self.add_edit_btn)
        layout.addLayout(edit_row)

        # --- Edits List ---
        layout.addWidget(QLabel("Endringer i denne filen:"))
        self.edits_list = QListWidget()
        self.edits_list.setViewMode(QListView.ListMode)
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

        self.setLayout(layout)

        self.update_driver_combo()
        self.driver_combo.currentTextChanged.connect(self.filter_data_by_driver)

        self.update_template_combo()
        self.template_combo.currentTextChanged.connect(self.apply_template)

    # --- File operations ---
    def add_file(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Velg filer", "", "Excel Files (*.xlsx);;DAT Files (*.dat);;All Files (*)"
        )
        if not paths:
            return
        for path in paths:
            if path not in self.file_paths:
                self.file_paths.append(path)
                self.file_list.addItem(os.path.basename(path))
        self.load_all_files()
        self.update_columns()
        self.filter_data_by_driver()

    def remove_selected_file(self):
        row = self.file_list.currentRow()
        if row >= 0:
            self.file_paths.pop(row)
            self.file_list.takeItem(row)
            self.load_all_files()
            self.update_columns()
            self.filter_data_by_driver()

    def load_all_files(self):
        self.dataframes.clear()
        all_columns = set()
        for path in self.file_paths:
            ext = os.path.splitext(path)[1].lower()
            try:
                if ext == ".xlsx":
                    df = pd.read_excel(path)
                elif ext == ".dat":
                    try:
                        df = pd.read_csv(path, sep=None, engine="python")
                    except Exception:
                        df = pd.read_csv(path, delimiter=";")
                else:
                    continue
                self.dataframes.append(df)
                all_columns.update(df.columns.tolist())
            except Exception as e:
                QMessageBox.warning(self, "Feil", f"Kunne ikke lese fil: {os.path.basename(path)}\n{e}")
        # --- Update available columns for templates in settings! ---
        if hasattr(self.settings_tab, "set_available_columns"):
            self.settings_tab.set_available_columns(list(all_columns))
        self.update_template_combo()

    # --- Driver picker ---
    def update_driver_combo(self):
        self.driver_combo.blockSignals(True)
        self.driver_combo.clear()
        drivers = self.settings_tab.get_drivers() if hasattr(self.settings_tab, "get_drivers") else []
        default_driver = self.settings_tab.get_default_driver() if hasattr(self.settings_tab, "get_default_driver") else ""
        default_idx = -1
        for idx, driver in enumerate(drivers):
            self.driver_combo.addItem(f"{driver['name']} ({driver['id']})", driver["id"])
            if str(driver["id"]) == str(default_driver):
                default_idx = idx
        if default_idx >= 0:
            self.driver_combo.setCurrentIndex(default_idx)
        self.driver_combo.blockSignals(False)
        self.filter_data_by_driver()

    def find_driver_column(self, df):
        for col in df.columns:
            c = col.lower()
            if any(word in c for word in ["sjaafor", "sjåfør", "sjafor", "sjåfor", "driver", "sjåførid", "sjaforid"]):
                return col
        return None

    def get_selected_driver_id(self):
        idx = self.driver_combo.currentIndex()
        if idx < 0:
            return None
        return self.driver_combo.currentData()

    def filter_data_by_driver(self):
        if not self.dataframes:
            self.filtered_data = None
            self.update_columns()
            self.show_preview()
            self.update_edits_list()
            self.calculate_salary_summary()
            return
        driver_id = self.get_selected_driver_id()
        dfs = []
        for df in self.dataframes:
            driver_col = self.find_driver_column(df)
            if driver_col and driver_id is not None:
                mask = df[driver_col].astype(str).str.zfill(4) == str(driver_id).zfill(4)
                filtered = df[mask]
                if not filtered.empty:
                    filtered = apply_kontant_edits(filtered, load_all_edits())
                    dfs.append(filtered)
            else:
                continue
        if dfs:
            self.filtered_data = pd.concat(dfs, ignore_index=True)
        else:
            self.filtered_data = None
        self.update_columns()
        self.show_preview()
        self.update_edits_list()
        self.calculate_salary_summary()

    # --- Columns checkboxes ---
    def update_columns(self):
        self.columns_list.blockSignals(True)
        self.columns_list.clear()
        df = self.filtered_data
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
            try:
                if item is not None and hasattr(item, "checkState") and hasattr(item, "text"):
                    if item.checkState() == Qt.Checked:
                        txt = item.text()
                        if isinstance(txt, str) and (self.filtered_data is None or txt in self.filtered_data.columns):
                            checked.append(txt)
            except Exception:
                continue
        checked = [col for col in checked if isinstance(col, str) and (self.filtered_data is None or col in self.filtered_data.columns)]
        return checked

    # --- Table preview ---
    def show_preview(self, max_rows=10):
        df = self.filtered_data
        if df is None or df.empty:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            return
        checked_columns = self.get_checked_columns()
        checked_columns = [col for col in checked_columns if isinstance(col, str) and col in df.columns]
        if not checked_columns:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            return
        try:
            preview_data = df[checked_columns].head(max_rows)
        except Exception as e:
            QMessageBox.critical(self, "Feil i forhåndsvisning", str(e))
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            return
        self.table.setRowCount(len(preview_data))
        self.table.setColumnCount(len(checked_columns))
        self.table.setHorizontalHeaderLabels([str(col) for col in checked_columns])
        for i, row in preview_data.iterrows():
            for j, value in enumerate(row):
                colname = checked_columns[j]
                sval = str(value)
                if colname.lower().startswith("start_dato") or colname.lower().startswith("slutt_dato"):
                    try:
                        dt = pd.to_datetime(value)
                        sval = dt.strftime('%Y-%m-%d')
                    except Exception:
                        sval = str(value)
                self.table.setItem(i, j, QTableWidgetItem(sval))

    # --- Templates (now use SettingsTab) ---
    def update_template_combo(self):
        self.template_combo.blockSignals(True)
        self.template_combo.clear()
        self.template_combo.addItem("Standard (alle kolonner)")
        templates = self.settings_tab.get_templates() if hasattr(self.settings_tab, "get_templates") else []
        default_template = self.settings_tab.get_default_template() if hasattr(self.settings_tab, "get_default_template") else ""
        default_idx = 0
        for idx, tpl in enumerate(templates, start=1):
            name = tpl["name"]
            self.template_combo.addItem(name)
            if name == default_template:
                default_idx = idx
        self.template_combo.setCurrentIndex(default_idx)
        self.template_combo.blockSignals(False)

    def save_template(self):
        checked = self.get_checked_columns()
        if not checked:
            QMessageBox.warning(self, "Ingen kolonner", "Du må velge minst én kolonne for å lagre en mal.")
            return
        name, ok = QInputDialog.getText(self, "Lagre mal", "Navn på mal:")
        if not ok or not name.strip():
            return
        templates = self.settings_tab.get_templates()
        for tpl in templates:
            if tpl["name"] == name:
                tpl["columns"] = checked
                break
        else:
            templates.append({"name": name, "columns": checked})
        # Save to settings tab
        if hasattr(self.settings_tab, "save_templates"):
            self.settings_tab.templates = templates
            self.settings_tab.save_templates()
            self.update_template_combo()
            QMessageBox.information(self, "Mal lagret", f"Mal '{name}' lagret.")

    def apply_template(self, name):
        if self.filtered_data is None or self.columns_list.count() == 0:
            return
        self.columns_list.blockSignals(True)
        if name == "Standard (alle kolonner)":
            for i in range(self.columns_list.count()):
                self.columns_list.item(i).setCheckState(Qt.Checked)
        else:
            selected = set()
            templates = self.settings_tab.get_templates() if hasattr(self.settings_tab, "get_templates") else []
            for tpl in templates:
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

    # --- Year/month/name dialog and extraction ---
    def extract_year_month(self):
        # Try to extract from data
        year = month = None
        for df in self.dataframes:
            for col in df.columns:
                low = str(col).lower()
                if "start_dato" in low or "start_date" in low:
                    try:
                        date = pd.to_datetime(df.iloc[0][col])
                        year = date.year
                        month = date.month
                        break
                    except Exception:
                        continue
            if year and month:
                break
        # Fallback: look for numeric month in file name
        import re
        if not year and self.file_paths:
            m = re.search(r"20\d\d", self.file_paths[0])
            if m:
                year = int(m.group(0))
        if not month and self.file_paths:
            m = re.search(r"[-_](\d{1,2})", self.file_paths[0])
            if m:
                month = int(m.group(1))
        if not month:
            month = int(datetime.now().strftime("%m"))
        if not year:
            year = int(datetime.now().strftime("%Y"))
        return str(year), int(month)

    def get_report_info_dialog(self, default_year, default_month, default_name):
        dialog = QDialog(self)
        layout = QFormLayout(dialog)
        year_edit = QLineEdit(str(default_year))

        # --- Month as dropdown ---
        months_nb = ["Januar", "Februar", "Mars", "April", "Mai", "Juni",
                    "Juli", "August", "September", "Oktober", "November", "Desember"]
        month_combo = QComboBox()
        month_combo.addItems(months_nb)
        # If default_month is "6" or "06", select 5 (June, 0-indexed)
        try:
            # If given as name, convert to index; if given as int, select that
            if default_month.isdigit():
                idx = int(default_month) - 1
            else:
                idx = [m.lower() for m in months_nb].index(default_month.lower())
            if 0 <= idx < 12:
                month_combo.setCurrentIndex(idx)
        except Exception:
            pass

        name_edit = QLineEdit(default_name)
        layout.addRow("År:", year_edit)
        layout.addRow("Måned:", month_combo)
        layout.addRow("Navn på rapport:", name_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        dialog.setLayout(layout)
        if dialog.exec() == QDialog.Accepted:
            year = year_edit.text().strip()
            month = str(month_combo.currentIndex() + 1)  # for data and filename, use number
            month_label = month_combo.currentText()      # for display, use Norwegian name
            name = name_edit.text().strip()
            return year, month_label, name
        return None, None, None



    # --- Kontant Edits UI ---
    def update_edits_list(self):
        self.edits_list.clear()
        df = self.filtered_data
        if df is None or df.empty:
            return
        all_edits = edits_for_file(df)
        for edit in all_edits:
            self.edits_list.addItem(
                f"Skiftnr {edit['skiftnr']} / Løyve {edit['loyve']} | {edit['amount']} kr | {edit.get('note','')}"
            )

    def add_or_update_edit(self):
        skiftnr = self.edit_skiftnr.text().strip()
        loyve = self.edit_loyve.text().strip()
        amount = self.edit_amount.text().strip().replace(",", ".")
        note = self.edit_note.text().strip()
        if not (skiftnr and loyve and amount):
            QMessageBox.warning(self, "Mangler felt", "Fyll ut skiftnr, løyve og beløp.")
            return
        try:
            amount = float(amount)
        except Exception:
            QMessageBox.warning(self, "Feil beløp", "Beløp må være et tall.")
            return
        all_edits = load_all_edits()
        replaced = False
        for edit in all_edits:
            if (str(edit["skiftnr"]) == str(skiftnr) and str(edit["loyve"]) == str(loyve)):
                edit["amount"] = amount
                edit["note"] = note
                edit["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                replaced = True
        if not replaced:
            all_edits.append({
                "skiftnr": str(skiftnr),
                "loyve": str(loyve),
                "amount": amount,
                "note": note,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        save_all_edits(all_edits)
        self.filter_data_by_driver()
        self.calculate_salary_summary()

    def edit_selected_edit(self):
        row = self.edits_list.currentRow()
        df = self.filtered_data
        if df is None or df.empty:
            return
        all_edits = edits_for_file(df)
        if row < 0 or row >= len(all_edits):
            return
        edit = all_edits[row]
        self.edit_skiftnr.setText(str(edit["skiftnr"]))
        self.edit_loyve.setText(str(edit["loyve"]))
        self.edit_amount.setText(str(edit["amount"]))
        self.edit_note.setText(edit.get("note", ""))

    def delete_selected_edit(self):
        row = self.edits_list.currentRow()
        df = self.filtered_data
        if df is None or df.empty:
            return
        all_edits = load_all_edits()
        file_edits = edits_for_file(df)
        if row < 0 or row >= len(file_edits):
            return
        to_remove = file_edits[row]
        all_edits = [e for e in all_edits if not (
            str(e["skiftnr"]) == str(to_remove["skiftnr"])
            and str(e["loyve"]) == str(to_remove["loyve"])
        )]
        save_all_edits(all_edits)
        self.filter_data_by_driver()
        self.calculate_salary_summary()

    # --- Salary summary calculation with BANK/INNSKUDD info ---

    def calculate_salary_summary(self):
        df = self.filtered_data
        if df is None or df.empty:
            self.summary_box.setText("")
            self._kontant_val = 0
            self._company_bank_account = ""
            self._month_str = ""
            self._initials = ""
            self._driver_percent = 45.0
            return

        kontant_col = find_kontant_column(df)
        subtotal_col = find_subtotal_column(df)
        bomtur_col = find_bomtur_column(df)
        tips_col = find_tips_column(df)

        kontant_sum = df[kontant_col].apply(safe_float).sum() if kontant_col else 0
        subtotal_sum = df[subtotal_col].apply(safe_float).sum() if subtotal_col else 0
        bomtur_sum = df[bomtur_col].apply(safe_float).sum() if bomtur_col else 0
        tips_sum = df[tips_col].apply(safe_float).sum() if tips_col else 0

        driver_id = self.get_selected_driver_id()
        driver_percent = 45.0
        if hasattr(self.settings_tab, "get_driver_percent"):
            driver_percent = self.settings_tab.get_driver_percent(driver_id)
        try:
            driver_percent = float(driver_percent)
        except Exception:
            driver_percent = 45.0

        kontant_val = kontant_sum - bomtur_sum

        brutto = 0.0
        if subtotal_sum > 0:
            brutto = (subtotal_sum / 1.12) * (driver_percent / 100.0)
        brutto += tips_sum

        def nf(val):
            if isinstance(val, float) and val.is_integer():
                return "{:,.0f}".format(val).replace(",", " ")
            return "{:,.2f}".format(val).replace(",", " ").replace(".", ",")

        initials = ""
        drivers = self.settings_tab.get_drivers() if hasattr(self.settings_tab, "get_drivers") else []
        driver_name = ""
        for d in drivers:
            if str(d["id"]) == str(driver_id):
                driver_name = d["name"]
                if d["name"]:
                    initials = ''.join([n[0] for n in d["name"].split() if n]).upper()
                break
        _, month = self.extract_year_month()
        months_nb = ["", "Januar", "Februar", "Mars", "April", "Mai", "Juni",
                    "Juli", "August", "September", "Oktober", "November", "Desember"]
        try:
            month_num = int(month)
            month_str = months_nb[month_num] if 1 <= month_num <= 12 else str(month)
        except Exception:
            month_str = str(month)

        # --- COMPANY BANK ACCOUNT from settings ---
        company_bank_account = ""
        if hasattr(self.settings_tab, "get_default_bank_account"):
            company_bank_account = self.settings_tab.get_default_bank_account()

        # --- Just the summary, no "sett inn kontant" here ---
        summary = (
            f"<b>Kontant:</b> {nf(kontant_val)} kr &nbsp;&nbsp;"
            f"<b>Brutto lønn:</b> {nf(brutto)} kr &nbsp;&nbsp;"
            f"<b>Tips:</b> {nf(tips_sum)} kr &nbsp;&nbsp;"
            f"<b>Lønnsprosent:</b> {driver_percent:.2f}%"
        )
        self.summary_box.setText(summary)

        # Save info for PDF
        self._kontant_val = kontant_val
        self._company_bank_account = company_bank_account
        self._month_str = month_str
        self._initials = initials
        self._driver_percent = driver_percent



    # --- PDF Export ---
    def generate_pdf(self):
        import re
        df = self.filtered_data
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

        # --- Extract date info
        year, month_idx = self.extract_year_month()
        months_nb = ["Januar", "Februar", "Mars", "April", "Mai", "Juni",
                    "Juli", "August", "September", "Oktober", "November", "Desember"]
        month_str = months_nb[month_idx-1] if 1 <= month_idx <= 12 else str(month_idx)

        # --- Driver info
        driver_id = self.get_selected_driver_id()
        drivers = self.settings_tab.get_drivers() if hasattr(self.settings_tab, "get_drivers") else []
        driver_name = ""
        for d in drivers:
            if d["id"] == driver_id:
                driver_name = d["name"]

        # --- Suggest file/report name
        suggested_name = f"Lønn - {driver_name} {month_str} {year}"

        # --- Ask user for year/month/name
        year, month_input, name = self.get_report_info_dialog(year, month_idx, suggested_name)
        if not (year and month_input and name):
            return

        save_dir = os.path.join(os.path.expanduser("~"), "TaxiRapport", "reports", "lonn", str(year))
        os.makedirs(save_dir, exist_ok=True)
        pdf_path = os.path.join(save_dir, f"{name}.pdf")

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

        # ---- Get company info from settings ----
        company = self.settings_tab.get_company_info() if hasattr(self.settings_tab, "get_company_info") else {}
        company_name = company.get("name", "")
        company_orgnr = company.get("orgnr", "")
        company_addr = company.get("address", "")

        # ---- Kontant innskudd info ----
        self.calculate_salary_summary()
        kontant_val = getattr(self, "_kontant_val", None)
        company_bank_account = getattr(self, "_company_bank_account", "")
        initials = getattr(self, "_initials", "")
        kontant_line = ""
        if company_bank_account and kontant_val and kontant_val > 0:
            def nf(val):
                if isinstance(val, float) and val.is_integer():
                    return "{:,.0f}".format(val).replace(",", " ")
                return "{:,.2f}".format(val).replace(",", " ").replace(".", ",")
            kontant_line = f"Sett inn kontant kr {nf(kontant_val)} på {company_bank_account}, merkes med \"Kontant innskudd {month_input} {initials}\""

        # --- HEADER BLOCK ---
        margin_x = pdf.l_margin
        top_y = pdf.get_y()
        # Left: Company info
        pdf.set_xy(margin_x, top_y)
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
        pdf.line(margin_x, line_y, pdf.w - margin_x, line_y)
        pdf.set_draw_color(0, 0, 0)
        pdf.ln(8)

        # Right: Kontant innskudd (one line, top right)
        if kontant_line:
            pdf.set_font('DejaVu', '', 11)
            text_width = pdf.get_string_width(kontant_line)
            right_x = pdf.w - pdf.r_margin - text_width
            pdf.set_xy(right_x, top_y)
            pdf.set_text_color(0, 60, 120)
            pdf.cell(text_width, 7, kontant_line, ln=0, align='R')
            pdf.set_text_color(0, 0, 0)
        pdf.set_xy(margin_x, line_y + 5)

        # --- Horizontal info line ---
        pdf.ln(2)
        pdf.set_font('DejaVu', 'B', 13)
        info = f"Lønn - Sjåfør: {driver_name} ({driver_id})     År: {year}     Måned: {month_input}"
        pdf.cell(0, 11, info, ln=1)
        pdf.ln(1)

        # ---- Salary summary block (NO kontant innskudd repeat!) ----
        salary_html = self.summary_box.text()
        salary_txt = re.sub(r"<[^>]+>", "", salary_html).replace("&nbsp;", " ")
        pdf.set_font('DejaVu', '', 12)
        pdf.multi_cell(0, 8, salary_txt)
        pdf.ln(2)


        # --- Table: shrink-to-fit, always readable ---
        table_width = pdf.w - 2 * pdf.l_margin
        n_cols = len(checked)
        col_width = table_width / n_cols if n_cols > 0 else table_width

        # Precalculate: for each column, the **widest** string (including header)
        max_strs = []
        for i, col in enumerate(checked):
            strings = [str(col)]
            for val in df[col]:
                sval = str(val)
                if col.lower().startswith("start_dato") or col.lower().startswith("slutt_dato"):
                    try:
                        dt = pd.to_datetime(sval)
                        sval = dt.strftime('%Y-%m-%d')
                    except Exception:
                        pass
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
                sval = str(val)
                if colname.lower().startswith("start_dato") or colname.lower().startswith("slutt_dato"):
                    try:
                        dt = pd.to_datetime(sval)
                        sval = dt.strftime('%Y-%m-%d')
                    except Exception:
                        pass
                align = 'R' if pd.api.types.is_numeric_dtype(df[checked[j]]) else 'C'
                pdf.cell(col_width, 8, sval, border=1, align=align)
            pdf.ln()

        # --- Totals row: skip Skiftnr/Løyve/Sjaafor/Sjåfør etc ---
        skip_sum_names = [
            "skiftnr", "løyve", "loyve", "sjaafor", "sjåfør", "sjafor", "sjåfor", "driver", "sjåførid", "sjaforid"
        ]
        pdf.set_font('DejaVu', 'B', font_size)
        has_totals = False
        totals = []
        for col in checked:
            if any(skip in col.lower() for skip in skip_sum_names):
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

        # --- Edits summary ---
        edits = edits_for_file(df)
        if edits:
            pdf.ln(5)
            pdf.set_font('DejaVu', 'B', font_size)
            pdf.cell(0, 8, "Endringer (kontant):", ln=1)
            pdf.set_font('DejaVu', '', font_size)
            for edit in edits:
                line = f"Skiftnr {edit['skiftnr']}, Løyve {edit['loyve']}, {edit['amount']} kr"
                if edit.get("note", ""):
                    line += f" ({edit['note']})"
                pdf.cell(0, 7, line, ln=1)

        try:
            pdf.output(pdf_path)
            QMessageBox.information(self, "PDF lagret", f"PDF lagret til:\n{pdf_path}")
        except Exception as e:
            QMessageBox.critical(self, "Feil ved lagring", str(e))
