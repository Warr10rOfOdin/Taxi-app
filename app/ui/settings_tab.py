from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QCheckBox, QListWidget,
    QPushButton, QInputDialog, QMessageBox, QListWidgetItem, QDialog, QFormLayout,
    QDialogButtonBox, QMenu, QListView, QAbstractItemView, QLineEdit
)
from PySide6.QtCore import Signal, Qt
import os
import json
import re

def star(s): return f"★ {s}" if s else s
def unstar(s): return s[2:] if s.startswith("★ ") else s

class CollapsiblePanel(QWidget):
    def __init__(self, title, childwidget):
        super().__init__()
        self.child = childwidget
        self.collapsed = True
        self.btn = QPushButton("▶ " + title)
        self.btn.setFlat(True)
        self.btn.setStyleSheet("text-align: left; font-weight: bold;")
        self.btn.clicked.connect(self.toggle)
        self.child.setVisible(False)
        layout = QVBoxLayout()
        layout.addWidget(self.btn)
        layout.addWidget(self.child)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def toggle(self):
        self.collapsed = not self.collapsed
        self.child.setVisible(not self.collapsed)
        self.btn.setText(("▶ " if self.collapsed else "▼ ") + self.btn.text()[2:])

class MultiColumnDialog(QDialog):
    def __init__(self, all_columns, selected=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Velg kolonner")
        self.selected = set(selected or [])
        self.list = QListWidget()
        self.list.setSelectionMode(QAbstractItemView.NoSelection)
        for col in all_columns:
            item = QListWidgetItem(str(col))
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if col in self.selected else Qt.Unchecked)
            self.list.addItem(item)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Velg hvilke kolonner som skal være med i malen:"))
        layout.addWidget(self.list)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)
        self.setLayout(layout)

    def get_selected_columns(self):
        return [self.list.item(i).text() for i in range(self.list.count())
                if self.list.item(i).checkState() == Qt.Checked]

class SettingsTab(QWidget):
    dark_mode_toggled = Signal(bool)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("<h3>Innstillinger</h3>"))

        # --- COMPANY INFO (New Section) ---
        basedir = os.path.dirname(__file__)
        self._company_file = os.path.join(basedir, "company_info.json")
        self.load_company_info()
        company = self.company_info

        company_form = QHBoxLayout()
        self.company_name_edit = QLineEdit(company.get("name", ""))
        self.company_name_edit.setPlaceholderText("Firmanavn")
        self.company_orgnr_edit = QLineEdit(company.get("orgnr", ""))
        self.company_orgnr_edit.setPlaceholderText("Org.nr")
        self.company_addr_edit = QLineEdit(company.get("address", ""))
        self.company_addr_edit.setPlaceholderText("Adresse")

        company_form.addWidget(QLabel("Firmanavn:"))
        company_form.addWidget(self.company_name_edit)
        company_form.addWidget(QLabel("Org.nr:"))
        company_form.addWidget(self.company_orgnr_edit)
        company_form.addWidget(QLabel("Adresse:"))
        company_form.addWidget(self.company_addr_edit)
        layout.addLayout(company_form)

        self.save_company_btn = QPushButton("Lagre firmainformasjon")
        self.save_company_btn.clicked.connect(self.save_company_fields)
        layout.addWidget(self.save_company_btn)
        # --- END COMPANY INFO ---

        # --- Language ---
        layout.addWidget(QLabel("Språkvalg:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Norsk Bokmål", "Nynorsk", "English"])
        layout.addWidget(self.lang_combo)

        # --- Dark mode toggle ---
        self.dark_checkbox = QCheckBox("Mørk modus")
        layout.addWidget(self.dark_checkbox)
        self.dark_checkbox.stateChanged.connect(self.emit_dark_mode)

        # --- Dynamic columns for templates (set from app after loading files!) ---
        self._available_columns = [
            "Skiftnr", "Løyve", "Sub_Total", "Kontant", "Kreditt_Tips", "Bomtur", "Start_Dato", "Slutt_Dato"
        ]

        # --- Drivers Section ---
        self.driver_panel = self.make_driver_panel()
        layout.addWidget(self.driver_panel)

        # --- Bank Accounts Section ---
        self.bank_panel = self.make_bank_panel()
        layout.addWidget(self.bank_panel)

        # --- Templates Section ---
        self.tmpl_panel = self.make_template_panel()
        layout.addWidget(self.tmpl_panel)

        layout.addStretch()
        self.setLayout(layout)

        self._drivers_file = os.path.join(basedir, "drivers.json")
        self._bank_file = os.path.join(basedir, "bank_accounts.json")
        self._tmpl_file = os.path.join(basedir, "templates.json")

        self.load_bank_accounts()
        self.load_templates()
        self.load_drivers()

    # --- COMPANY INFO STORAGE & UI Methods ---
    def load_company_info(self):
        try:
            with open(self._company_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.company_info = data
        except Exception:
            self.company_info = {
                "name": "",
                "orgnr": "",
                "address": ""
            }

    def save_company_info(self):
        with open(self._company_file, "w", encoding="utf-8") as f:
            json.dump(self.company_info, f, indent=2, ensure_ascii=False)

    def save_company_fields(self):
        self.company_info["name"] = self.company_name_edit.text().strip()
        self.company_info["orgnr"] = self.company_orgnr_edit.text().strip()
        self.company_info["address"] = self.company_addr_edit.text().strip()
        self.save_company_info()
        QMessageBox.information(self, "Lagret", "Firmainformasjon lagret.")

    def get_company_info(self):
        return self.company_info.copy()
    # --- END COMPANY INFO ---

    # --- Externally callable to set columns for templates dynamically! ---
    def set_available_columns(self, columns):
        # Use columns from app/tabs; remove duplicates, keep order.
        seen = set()
        self._available_columns = [c for c in columns if not (c in seen or seen.add(c))]

    # ---------- Collapsibles construction ----------
    def make_driver_panel(self):
        widget = QWidget()
        vbox = QVBoxLayout(widget)
        self.driver_list = QListWidget()
        vbox.addWidget(self.driver_list)

        btns = QHBoxLayout()
        self.add_btn = QPushButton("Legg til sjåfør")
        self.add_btn.clicked.connect(self.add_driver)
        btns.addWidget(self.add_btn)
        self.edit_btn = QPushButton("Rediger valgt")
        self.edit_btn.clicked.connect(self.edit_driver)
        btns.addWidget(self.edit_btn)
        self.del_btn = QPushButton("Slett valgt")
        self.del_btn.clicked.connect(self.delete_driver)
        btns.addWidget(self.del_btn)
        self.set_def_btn = QPushButton("Sett som standard")
        self.set_def_btn.clicked.connect(self.set_default_driver)
        btns.addWidget(self.set_def_btn)
        self.unset_def_btn = QPushButton("Fjern som standard")
        self.unset_def_btn.clicked.connect(self.unset_default_driver)
        btns.addWidget(self.unset_def_btn)
        btns.addStretch()
        vbox.addLayout(btns)

        self.driver_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.driver_list.customContextMenuRequested.connect(self.driver_context_menu)
        return CollapsiblePanel("Sjåfører (navn + 4-sifret ID)", widget)

    def make_bank_panel(self):
        widget = QWidget()
        vbox = QVBoxLayout(widget)
        self.bank_list = QListWidget()
        vbox.addWidget(self.bank_list)
        btns = QHBoxLayout()
        self.add_bank_btn = QPushButton("Legg til konto")
        self.add_bank_btn.clicked.connect(self.add_bank_account)
        btns.addWidget(self.add_bank_btn)
        self.edit_bank_btn = QPushButton("Rediger valgt")
        self.edit_bank_btn.clicked.connect(self.edit_bank_account)
        btns.addWidget(self.edit_bank_btn)
        self.del_bank_btn = QPushButton("Slett valgt")
        self.del_bank_btn.clicked.connect(self.delete_bank_account)
        btns.addWidget(self.del_bank_btn)
        self.set_def_bank_btn = QPushButton("Sett som standard")
        self.set_def_bank_btn.clicked.connect(self.set_default_bank_account)
        btns.addWidget(self.set_def_bank_btn)
        self.unset_def_bank_btn = QPushButton("Fjern som standard")
        self.unset_def_bank_btn.clicked.connect(self.unset_default_bank_account)
        btns.addWidget(self.unset_def_bank_btn)
        btns.addStretch()
        vbox.addLayout(btns)
        self.bank_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.bank_list.customContextMenuRequested.connect(self.bank_context_menu)
        return CollapsiblePanel("Bankkonti (format 0000.00.00000)", widget)

    def make_template_panel(self):
        widget = QWidget()
        vbox = QVBoxLayout(widget)
        self.templates_list = QListWidget()
        vbox.addWidget(self.templates_list)
        btns = QHBoxLayout()
        self.add_tmpl_btn = QPushButton("Legg til mal")
        self.add_tmpl_btn.clicked.connect(self.add_template)
        btns.addWidget(self.add_tmpl_btn)
        self.edit_tmpl_btn = QPushButton("Rediger valgt")
        self.edit_tmpl_btn.clicked.connect(self.edit_template)
        btns.addWidget(self.edit_tmpl_btn)
        self.del_tmpl_btn = QPushButton("Slett valgt")
        self.del_tmpl_btn.clicked.connect(self.delete_template)
        btns.addWidget(self.del_tmpl_btn)
        self.set_def_tmpl_btn = QPushButton("Sett som standard")
        self.set_def_tmpl_btn.clicked.connect(self.set_default_template)
        btns.addWidget(self.set_def_tmpl_btn)
        self.unset_def_tmpl_btn = QPushButton("Fjern som standard")
        self.unset_def_tmpl_btn.clicked.connect(self.unset_default_template)
        btns.addWidget(self.unset_def_tmpl_btn)
        btns.addStretch()
        vbox.addLayout(btns)
        self.templates_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.templates_list.customContextMenuRequested.connect(self.template_context_menu)
        return CollapsiblePanel("Maler (for lønn og skift)", widget)

    def emit_dark_mode(self, state):
        self.dark_mode_toggled.emit(bool(state))

    # ======================= Drivers management ==========================
    def load_drivers(self):
        try:
            with open(self._drivers_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    self.drivers = data.get("drivers", [])
                    self.default_driver = data.get("default", "")
                else:
                    self.drivers = data
                    self.default_driver = ""
        except Exception:
            self.drivers, self.default_driver = [], ""
        self.refresh_driver_list()

    def save_drivers(self):
        with open(self._drivers_file, "w", encoding="utf-8") as f:
            json.dump({"drivers": self.drivers, "default": self.default_driver}, f, indent=2, ensure_ascii=False)

    def refresh_driver_list(self):
        self.driver_list.clear()
        for d in self.drivers:
            s = f"{d['name']} ({d['id']}) - {d.get('percent',45):.1f}%"
            if d.get("bank_account"):
                s += f" [{d['bank_account']}]"
            if str(d["id"]) == str(self.default_driver):
                s = star(s)
            self.driver_list.addItem(s)

    def add_driver(self):
        name, ok = QInputDialog.getText(self, "Ny sjåfør", "Navn på sjåfør:")
        if not ok or not name.strip(): return
        id, ok = QInputDialog.getText(self, "Ny sjåfør", "Sjåfør-ID (4 siffer):")
        if not ok or not id.isdigit() or len(id) != 4:
            QMessageBox.warning(self, "Feil", "ID må være nøyaktig 4 siffer.")
            return
        if any(d["id"] == id for d in self.drivers):
            QMessageBox.warning(self, "Feil", "ID finnes allerede.")
            return
        percent, ok = QInputDialog.getDouble(self, "Kommisjon", "Kommisjon (prosent, f.eks. 45):", 45.0, 0, 100, 1)
        if not ok: percent = 45.0
        bank = self.select_bank_account_dialog()
        self.drivers.append({"name": name.strip(), "id": id, "percent": percent, "bank_account": bank})
        self.save_drivers()
        self.refresh_driver_list()

    def edit_driver(self):
        row = self.driver_list.currentRow()
        if row < 0: return
        d = self.drivers[row]
        name, ok = QInputDialog.getText(self, "Rediger sjåfør", "Navn på sjåfør:", text=d["name"])
        if not ok or not name.strip(): return
        id, ok = QInputDialog.getText(self, "Rediger sjåfør", "Sjåfør-ID (4 siffer):", text=d["id"])
        if not ok or not id.isdigit() or len(id) != 4:
            QMessageBox.warning(self, "Feil", "ID må være nøyaktig 4 siffer.")
            return
        for i, other in enumerate(self.drivers):
            if i != row and other["id"] == id:
                QMessageBox.warning(self, "Feil", "ID finnes allerede.")
                return
        percent, ok = QInputDialog.getDouble(self, "Kommisjon", "Kommisjon (prosent, f.eks. 45):", float(d.get("percent", 45.0)), 0, 100, 1)
        if not ok: percent = d.get("percent", 45.0)
        bank = self.select_bank_account_dialog(initial=d.get("bank_account", ""))
        self.drivers[row] = {"name": name.strip(), "id": id, "percent": percent, "bank_account": bank}
        self.save_drivers()
        self.refresh_driver_list()

    def delete_driver(self):
        row = self.driver_list.currentRow()
        if row < 0: return
        d = self.drivers[row]
        ok = QMessageBox.question(self, "Slett sjåfør", f"Er du sikker på at du vil slette {d['name']} ({d['id']})?")
        if ok == QMessageBox.Yes:
            if str(d["id"]) == str(self.default_driver):
                self.default_driver = ""
            self.drivers.pop(row)
            self.save_drivers()
            self.refresh_driver_list()

    def set_default_driver(self):
        row = self.driver_list.currentRow()
        if row < 0: return
        d = self.drivers[row]
        self.default_driver = d["id"]
        self.save_drivers()
        self.refresh_driver_list()

    def unset_default_driver(self):
        self.default_driver = ""
        self.save_drivers()
        self.refresh_driver_list()

    def driver_context_menu(self, point):
        menu = QMenu()
        row = self.driver_list.indexAt(point).row()
        setdef = menu.addAction("Sett som standard")
        if row >= 0:
            label = self.driver_list.item(row).text()
            if label.startswith("★"):
                unsetdef = menu.addAction("Fjern som standard")
        act = menu.exec_(self.driver_list.mapToGlobal(point))
        if act == setdef:
            self.driver_list.setCurrentRow(row)
            self.set_default_driver()
        elif act and act.text() == "Fjern som standard":
            self.unset_default_driver()

    def select_bank_account_dialog(self, initial=None):
        accounts = [f"{b['account']} ({b.get('name','')})" if b.get("name") else b["account"] for b in self.bank_accounts]
        accounts.insert(0, "Ingen konto")
        current = 0
        if initial:
            for i, b in enumerate(self.bank_accounts, start=1):
                if b["account"] == initial: current = i; break
        item, ok = QInputDialog.getItem(self, "Velg bankkonto", "Bankkonto:", accounts, current, False)
        if not ok or item == "Ingen konto":
            return ""
        for b in self.bank_accounts:
            disp = f"{b['account']} ({b.get('name','')})" if b.get("name") else b["account"]
            if item == disp: return b["account"]
        return ""

    def get_drivers(self): return self.drivers.copy()
    def get_driver_percent(self, driver_id):
        for d in self.get_drivers():
            if str(d["id"]) == str(driver_id): return float(d.get("percent", 45.0))
        return 45.0
    def get_driver_bank_account(self, driver_id):
        for d in self.get_drivers():
            if str(d["id"]) == str(driver_id): return d.get("bank_account", "")
        return ""
    def get_default_driver(self): return self.default_driver

    # ======================= Bank accounts ==========================
    def load_bank_accounts(self):
        try:
            with open(self._bank_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    self.bank_accounts = data.get("accounts", [])
                    self.default_bank = data.get("default", "")
                else:
                    self.bank_accounts = data
                    self.default_bank = ""
        except Exception:
            self.bank_accounts, self.default_bank = [], ""
        self.refresh_bank_list()

    def save_bank_accounts(self):
        with open(self._bank_file, "w", encoding="utf-8") as f:
            json.dump({"accounts": self.bank_accounts, "default": self.default_bank}, f, indent=2, ensure_ascii=False)

    def refresh_bank_list(self):
        self.bank_list.clear()
        for b in self.bank_accounts:
            s = f"{b['account']} ({b.get('name','')})" if b.get("name") else b["account"]
            if b["account"] == self.default_bank: s = star(s)
            self.bank_list.addItem(s)

    def add_bank_account(self):
        account, ok = QInputDialog.getText(self, "Ny bankkonto", "Kontonummer (0000.00.00000):")
        if not ok or not self.is_valid_account(account):
            QMessageBox.warning(self, "Feil", "Ugyldig kontonummer. Format: 0000.00.00000")
            return
        name, ok = QInputDialog.getText(self, "Ny bankkonto", "Navn (valgfritt):")
        if not ok: name = ""
        if any(b["account"] == account for b in self.bank_accounts):
            QMessageBox.warning(self, "Feil", "Kontonummeret finnes allerede.")
            return
        self.bank_accounts.append({"account": account, "name": name.strip()})
        self.save_bank_accounts()
        self.refresh_bank_list()

    def edit_bank_account(self):
        row = self.bank_list.currentRow()
        if row < 0: return
        b = self.bank_accounts[row]
        account, ok = QInputDialog.getText(self, "Rediger bankkonto", "Kontonummer (0000.00.00000):", text=b["account"])
        if not ok or not self.is_valid_account(account):
            QMessageBox.warning(self, "Feil", "Ugyldig kontonummer. Format: 0000.00.00000")
            return
        name, ok = QInputDialog.getText(self, "Rediger bankkonto", "Navn (valgfritt):", text=b.get("name", ""))
        if not ok: name = b.get("name", "")
        for i, other in enumerate(self.bank_accounts):
            if i != row and other["account"] == account:
                QMessageBox.warning(self, "Feil", "Kontonummeret finnes allerede.")
                return
        self.bank_accounts[row] = {"account": account, "name": name.strip()}
        self.save_bank_accounts()
        self.refresh_bank_list()
        self.load_drivers()

    def delete_bank_account(self):
        row = self.bank_list.currentRow()
        if row < 0: return
        b = self.bank_accounts[row]
        ok = QMessageBox.question(self, "Slett bankkonto", f"Slett {b['account']}?")
        if ok == QMessageBox.Yes:
            if b["account"] == self.default_bank:
                self.default_bank = ""
            self.bank_accounts.pop(row)
            self.save_bank_accounts()
            self.refresh_bank_list()
            self.load_drivers()

    def set_default_bank_account(self):
        row = self.bank_list.currentRow()
        if row < 0: return
        b = self.bank_accounts[row]
        self.default_bank = b["account"]
        self.save_bank_accounts()
        self.refresh_bank_list()

    def unset_default_bank_account(self):
        self.default_bank = ""
        self.save_bank_accounts()
        self.refresh_bank_list()

    def bank_context_menu(self, point):
        menu = QMenu()
        row = self.bank_list.indexAt(point).row()
        setdef = menu.addAction("Sett som standard")
        if row >= 0:
            label = self.bank_list.item(row).text()
            if label.startswith("★"):
                unsetdef = menu.addAction("Fjern som standard")
        act = menu.exec_(self.bank_list.mapToGlobal(point))
        if act == setdef:
            self.bank_list.setCurrentRow(row)
            self.set_default_bank_account()
        elif act and act.text() == "Fjern som standard":
            self.unset_default_bank_account()

    def is_valid_account(self, account):
        return bool(re.match(r"^\d{4}\.\d{2}\.\d{5}$", account))

    def get_bank_accounts(self): return self.bank_accounts.copy()
    def get_default_bank_account(self): return self.default_bank

    # =================== Templates (multi-section) =====================
    def load_templates(self):
        try:
            with open(self._tmpl_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    self.templates = data.get("templates", [])
                    self.default_template = data.get("default", "")
                else:
                    self.templates = data
                    self.default_template = ""
        except Exception:
            self.templates, self.default_template = [], ""
        self.refresh_templates_list()

    def save_templates(self):
        with open(self._tmpl_file, "w", encoding="utf-8") as f:
            json.dump({"templates": self.templates, "default": self.default_template}, f, indent=2, ensure_ascii=False)

    def refresh_templates_list(self):
        self.templates_list.clear()
        for t in self.templates:
            s = t["name"]
            if s == self.default_template: s = star(s)
            self.templates_list.addItem(s)

    def add_template(self):
        name, ok = QInputDialog.getText(self, "Ny mal", "Navn på mal:")
        if not ok or not name.strip(): return
        columns = self.columns_dialog([])
        if not columns: return
        if any(t["name"] == name for t in self.templates):
            QMessageBox.warning(self, "Feil", "Navnet finnes allerede.")
            return
        self.templates.append({"name": name, "columns": columns})
        self.save_templates()
        self.refresh_templates_list()

    def edit_template(self):
        row = self.templates_list.currentRow()
        if row < 0: return
        t = self.templates[row]
        name, ok = QInputDialog.getText(self, "Rediger mal", "Navn på mal:", text=t["name"])
        if not ok or not name.strip(): return
        columns = self.columns_dialog(t["columns"])
        if not columns: return
        for i, other in enumerate(self.templates):
            if i != row and other["name"] == name:
                QMessageBox.warning(self, "Feil", "Navnet finnes allerede.")
                return
        self.templates[row] = {"name": name.strip(), "columns": columns}
        self.save_templates()
        self.refresh_templates_list()

    def delete_template(self):
        row = self.templates_list.currentRow()
        if row < 0: return
        t = self.templates[row]
        ok = QMessageBox.question(self, "Slett mal", f"Er du sikker på at du vil slette malen '{t['name']}'?")
        if ok == QMessageBox.Yes:
            if self.default_template == t["name"]:
                self.default_template = ""
            self.templates.pop(row)
            self.save_templates()
            self.refresh_templates_list()

    def set_default_template(self):
        row = self.templates_list.currentRow()
        if row < 0: return
        t = self.templates[row]
        self.default_template = t["name"]
        self.save_templates()
        self.refresh_templates_list()

    def unset_default_template(self):
        self.default_template = ""
        self.save_templates()
        self.refresh_templates_list()

    def template_context_menu(self, point):
        menu = QMenu()
        row = self.templates_list.indexAt(point).row()
        setdef = menu.addAction("Sett som standard")
        if row >= 0:
            label = self.templates_list.item(row).text()
            if label.startswith("★"):
                unsetdef = menu.addAction("Fjern som standard")
        act = menu.exec_(self.templates_list.mapToGlobal(point))
        if act == setdef:
            self.templates_list.setCurrentRow(row)
            self.set_default_template()
        elif act and act.text() == "Fjern som standard":
            self.unset_default_template()

    def columns_dialog(self, selected):
        # Shows dynamically-updated columns!
        dlg = MultiColumnDialog(self._available_columns, selected, self)
        if dlg.exec_():
            cols = dlg.get_selected_columns()
            if cols:
                return cols
        return []

    def get_templates(self): return self.templates.copy()
    def get_default_template(self): return self.default_template
