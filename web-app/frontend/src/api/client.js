import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API methods
export const api = {
  // Companies
  getCompanies: () => apiClient.get('/api/companies'),
  getCompany: (id) => apiClient.get(`/api/companies/${id}`),
  createCompany: (data) => apiClient.post('/api/companies', data),
  updateCompany: (id, data) => apiClient.put(`/api/companies/${id}`, data),
  deleteCompany: (id) => apiClient.delete(`/api/companies/${id}`),

  // Drivers
  getDrivers: () => apiClient.get('/api/drivers'),
  getDriver: (id) => apiClient.get(`/api/drivers/${id}`),
  createDriver: (data) => apiClient.post('/api/drivers', data),
  updateDriver: (id, data) => apiClient.put(`/api/drivers/${id}`, data),
  deleteDriver: (id) => apiClient.delete(`/api/drivers/${id}`),

  // Bank Accounts
  getBankAccounts: () => apiClient.get('/api/bank-accounts'),
  getBankAccount: (id) => apiClient.get(`/api/bank-accounts/${id}`),
  createBankAccount: (data) => apiClient.post('/api/bank-accounts', data),
  updateBankAccount: (id, data) => apiClient.put(`/api/bank-accounts/${id}`, data),
  deleteBankAccount: (id) => apiClient.delete(`/api/bank-accounts/${id}`),

  // Templates
  getTemplates: (type) => apiClient.get('/api/templates', { params: { template_type: type } }),
  getTemplate: (id) => apiClient.get(`/api/templates/${id}`),
  createTemplate: (data) => apiClient.post('/api/templates', data),
  updateTemplate: (id, data) => apiClient.put(`/api/templates/${id}`, data),
  deleteTemplate: (id) => apiClient.delete(`/api/templates/${id}`),

  // Shift Reports
  getShiftReports: (driverId) => apiClient.get('/api/reports/shift', { params: { driver_id: driverId } }),
  getShiftReport: (id) => apiClient.get(`/api/reports/shift/${id}`),
  createShiftReport: (formData) => apiClient.post('/api/reports/shift', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  createShiftEdit: (reportId, data) => apiClient.post(`/api/reports/shift/${reportId}/edits`, data),
  deleteShiftReport: (id) => apiClient.delete(`/api/reports/shift/${id}`),
  generateShiftPDF: (id) => apiClient.post(`/api/reports/shift/${id}/pdf`, {}, { responseType: 'blob' }),

  // Salary Reports
  getSalaryReports: (driverId) => apiClient.get('/api/reports/salary', { params: { driver_id: driverId } }),
  getSalaryReport: (id) => apiClient.get(`/api/reports/salary/${id}`),
  createSalaryReport: (formData) => apiClient.post('/api/reports/salary', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  deleteSalaryReport: (id) => apiClient.delete(`/api/reports/salary/${id}`),
  generateSalaryPDF: (id) => apiClient.post(`/api/reports/salary/${id}/pdf`, {}, { responseType: 'blob' }),

  // File Upload
  parseFile: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post('/api/upload/parse', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

export default apiClient;
