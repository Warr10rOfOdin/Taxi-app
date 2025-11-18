// Client-side storage using localStorage

const STORAGE_KEYS = {
  DRIVERS: 'taxi_drivers',
  COMPANIES: 'taxi_companies',
  BANK_ACCOUNTS: 'taxi_bank_accounts',
  TEMPLATES: 'taxi_templates',
  SHIFT_REPORTS: 'taxi_shift_reports',
  SALARY_REPORTS: 'taxi_salary_reports',
};

// Helper functions
const getItem = (key, defaultValue = []) => {
  try {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : defaultValue;
  } catch (error) {
    console.error(`Error reading ${key}:`, error);
    return defaultValue;
  }
};

const setItem = (key, value) => {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (error) {
    console.error(`Error writing ${key}:`, error);
  }
};

const generateId = () => Date.now().toString();

// Initialize with default data if empty
const initializeDefaults = () => {
  // Only initialize if completely empty
  if (!localStorage.getItem(STORAGE_KEYS.DRIVERS)) {
    setItem(STORAGE_KEYS.DRIVERS, [
      { id: '1', name: 'Toni Kolve', driver_id: '1741', commission_percentage: 45.0, bank_account: '', is_default: true },
    ]);
  }

  if (!localStorage.getItem(STORAGE_KEYS.COMPANIES)) {
    setItem(STORAGE_KEYS.COMPANIES, [
      { id: '1', name: 'Kolve ST', org_number: '922900817', address: 'Kolvesvegen 181, 5706 Voss' },
    ]);
  }

  if (!localStorage.getItem(STORAGE_KEYS.TEMPLATES)) {
    setItem(STORAGE_KEYS.TEMPLATES, [
      {
        id: '1',
        name: 'Skift',
        template_type: 'shift',
        columns: ['Skiftnr', 'Løyve', 'Sjaafor', 'Start_Dato Tid', 'Slutt_Dato Tid', 'Turer', 'Total_Meter', 'Opptatt_Meter', 'Total_Kroner', 'Sub_Total', 'Bomtur_Kroner', 'Kreditt_Utlegg', 'Kreditt_Tips', 'Kontant', 'Kreditt', 'Lonn', 'Skatt', 'Totalt_Eier', 'Total Kreditt', 'Kontant_Eier', 'Total Mva', 'Rest Mva']
      },
      {
        id: '2',
        name: 'Lønn',
        template_type: 'salary',
        columns: ['Skiftnr', 'Løyve', 'Sjaafor', 'Start_Dato Tid', 'Slutt_Dato Tid', 'Turer', 'Total_Meter', 'Opptatt_Meter', 'Total_Kroner', 'Sub_Total', 'Bomtur_Kroner', 'Kreditt_Utlegg', 'Kreditt_Tips', 'Kontant', 'Kreditt', 'Lonn', 'Skatt', 'Totalt_Eier', 'Total Kreditt', 'Kontant_Eier']
      }
    ]);
  }
};

// Drivers
export const drivers = {
  getAll: () => getItem(STORAGE_KEYS.DRIVERS),
  getById: (id) => getItem(STORAGE_KEYS.DRIVERS).find(d => d.id === id),
  create: (driver) => {
    const drivers = getItem(STORAGE_KEYS.DRIVERS);
    const newDriver = { ...driver, id: generateId() };
    drivers.push(newDriver);
    setItem(STORAGE_KEYS.DRIVERS, drivers);
    return newDriver;
  },
  update: (id, driver) => {
    const drivers = getItem(STORAGE_KEYS.DRIVERS);
    const index = drivers.findIndex(d => d.id === id);
    if (index !== -1) {
      drivers[index] = { ...drivers[index], ...driver };
      setItem(STORAGE_KEYS.DRIVERS, drivers);
      return drivers[index];
    }
    return null;
  },
  delete: (id) => {
    const drivers = getItem(STORAGE_KEYS.DRIVERS).filter(d => d.id !== id);
    setItem(STORAGE_KEYS.DRIVERS, drivers);
  },
};

// Companies
export const companies = {
  getAll: () => getItem(STORAGE_KEYS.COMPANIES),
  getById: (id) => getItem(STORAGE_KEYS.COMPANIES).find(c => c.id === id),
  create: (company) => {
    const companies = getItem(STORAGE_KEYS.COMPANIES);
    const newCompany = { ...company, id: generateId() };
    companies.push(newCompany);
    setItem(STORAGE_KEYS.COMPANIES, companies);
    return newCompany;
  },
  update: (id, company) => {
    const companies = getItem(STORAGE_KEYS.COMPANIES);
    const index = companies.findIndex(c => c.id === id);
    if (index !== -1) {
      companies[index] = { ...companies[index], ...company };
      setItem(STORAGE_KEYS.COMPANIES, companies);
      return companies[index];
    }
    return null;
  },
  delete: (id) => {
    const companies = getItem(STORAGE_KEYS.COMPANIES).filter(c => c.id !== id);
    setItem(STORAGE_KEYS.COMPANIES, companies);
  },
};

// Bank Accounts
export const bankAccounts = {
  getAll: () => getItem(STORAGE_KEYS.BANK_ACCOUNTS),
  getById: (id) => getItem(STORAGE_KEYS.BANK_ACCOUNTS).find(b => b.id === id),
  create: (account) => {
    const accounts = getItem(STORAGE_KEYS.BANK_ACCOUNTS);
    const newAccount = { ...account, id: generateId() };
    accounts.push(newAccount);
    setItem(STORAGE_KEYS.BANK_ACCOUNTS, accounts);
    return newAccount;
  },
  update: (id, account) => {
    const accounts = getItem(STORAGE_KEYS.BANK_ACCOUNTS);
    const index = accounts.findIndex(b => b.id === id);
    if (index !== -1) {
      accounts[index] = { ...accounts[index], ...account };
      setItem(STORAGE_KEYS.BANK_ACCOUNTS, accounts);
      return accounts[index];
    }
    return null;
  },
  delete: (id) => {
    const accounts = getItem(STORAGE_KEYS.BANK_ACCOUNTS).filter(b => b.id !== id);
    setItem(STORAGE_KEYS.BANK_ACCOUNTS, accounts);
  },
};

// Templates
export const templates = {
  getAll: () => getItem(STORAGE_KEYS.TEMPLATES),
  getById: (id) => getItem(STORAGE_KEYS.TEMPLATES).find(t => t.id === id),
  create: (template) => {
    const templates = getItem(STORAGE_KEYS.TEMPLATES);
    const newTemplate = { ...template, id: generateId() };
    templates.push(newTemplate);
    setItem(STORAGE_KEYS.TEMPLATES, templates);
    return newTemplate;
  },
  update: (id, template) => {
    const templates = getItem(STORAGE_KEYS.TEMPLATES);
    const index = templates.findIndex(t => t.id === id);
    if (index !== -1) {
      templates[index] = { ...templates[index], ...template };
      setItem(STORAGE_KEYS.TEMPLATES, templates);
      return templates[index];
    }
    return null;
  },
  delete: (id) => {
    const templates = getItem(STORAGE_KEYS.TEMPLATES).filter(t => t.id !== id);
    setItem(STORAGE_KEYS.TEMPLATES, templates);
  },
};

// Shift Reports
export const shiftReports = {
  getAll: () => getItem(STORAGE_KEYS.SHIFT_REPORTS),
  getById: (id) => getItem(STORAGE_KEYS.SHIFT_REPORTS).find(r => r.id === id),
  create: (report) => {
    const reports = getItem(STORAGE_KEYS.SHIFT_REPORTS);
    const newReport = {
      ...report,
      id: generateId(),
      created_at: new Date().toISOString()
    };
    reports.push(newReport);
    setItem(STORAGE_KEYS.SHIFT_REPORTS, reports);
    return newReport;
  },
  update: (id, report) => {
    const reports = getItem(STORAGE_KEYS.SHIFT_REPORTS);
    const index = reports.findIndex(r => r.id === id);
    if (index !== -1) {
      reports[index] = { ...reports[index], ...report };
      setItem(STORAGE_KEYS.SHIFT_REPORTS, reports);
      return reports[index];
    }
    return null;
  },
  delete: (id) => {
    const reports = getItem(STORAGE_KEYS.SHIFT_REPORTS).filter(r => r.id !== id);
    setItem(STORAGE_KEYS.SHIFT_REPORTS, reports);
  },
};

// Salary Reports
export const salaryReports = {
  getAll: () => getItem(STORAGE_KEYS.SALARY_REPORTS),
  getById: (id) => getItem(STORAGE_KEYS.SALARY_REPORTS).find(r => r.id === id),
  create: (report) => {
    const reports = getItem(STORAGE_KEYS.SALARY_REPORTS);
    const newReport = {
      ...report,
      id: generateId(),
      created_at: new Date().toISOString()
    };
    reports.push(newReport);
    setItem(STORAGE_KEYS.SALARY_REPORTS, reports);
    return newReport;
  },
  update: (id, report) => {
    const reports = getItem(STORAGE_KEYS.SALARY_REPORTS);
    const index = reports.findIndex(r => r.id === id);
    if (index !== -1) {
      reports[index] = { ...reports[index], ...report };
      setItem(STORAGE_KEYS.SALARY_REPORTS, reports);
      return reports[index];
    }
    return null;
  },
  delete: (id) => {
    const reports = getItem(STORAGE_KEYS.SALARY_REPORTS).filter(r => r.id !== id);
    setItem(STORAGE_KEYS.SALARY_REPORTS, reports);
  },
};

// Initialize defaults on first run
initializeDefaults();
