import { useState, useEffect } from 'react';
import { Upload, DollarSign, Download, FileText } from 'lucide-react';
import { api } from '../api/client';

export default function SalaryReport() {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [reports, setReports] = useState([]);
  const [selectedDriver, setSelectedDriver] = useState('');
  const [reportPeriod, setReportPeriod] = useState('');
  const [drivers, setDrivers] = useState([]);

  useEffect(() => {
    loadDrivers();
    loadReports();
  }, []);

  const loadDrivers = async () => {
    try {
      const { data } = await api.getDrivers();
      setDrivers(data);
    } catch (error) {
      console.error('Error loading drivers:', error);
    }
  };

  const loadReports = async () => {
    try {
      const { data } = await api.getSalaryReports();
      setReports(data);
    } catch (error) {
      console.error('Error loading reports:', error);
    }
  };

  const handleFileChange = (e) => {
    setFiles(Array.from(e.target.files));
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      alert('Velg minst én fil');
      return;
    }

    if (!selectedDriver) {
      alert('Velg en sjåfør');
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      files.forEach((file) => {
        formData.append('files', file);
      });
      formData.append('driver_id', selectedDriver);
      if (reportPeriod) {
        formData.append('report_period', reportPeriod);
      }

      await api.createSalaryReport(formData);
      alert('Lønnsrapport opprettet!');
      setFiles([]);
      setReportPeriod('');
      loadReports();
    } catch (error) {
      console.error('Error uploading:', error);
      alert('Feil ved opplasting');
    } finally {
      setUploading(false);
    }
  };

  const handleGeneratePDF = async (reportId) => {
    try {
      const response = await api.generateSalaryPDF(reportId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `lonnsrapport_${reportId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Feil ved PDF-generering');
    }
  };

  const selectedDriverObj = drivers.find((d) => d.id === parseInt(selectedDriver));

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Upload Section */}
      <div className="card">
        <h2 className="text-2xl font-bold mb-6">Opprett lønnsrapport</h2>

        <div className="space-y-4">
          {/* Driver Selection */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Sjåfør <span className="text-red-500">*</span>
            </label>
            <select
              value={selectedDriver}
              onChange={(e) => setSelectedDriver(e.target.value)}
              className="input"
              required
            >
              <option value="">Velg sjåfør...</option>
              {drivers.map((driver) => (
                <option key={driver.id} value={driver.id}>
                  {driver.name} ({driver.driver_id}) - {driver.commission_percentage}% provisjon
                </option>
              ))}
            </select>
          </div>

          {/* Report Period */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Periode (valgfritt)
            </label>
            <input
              type="text"
              value={reportPeriod}
              onChange={(e) => setReportPeriod(e.target.value)}
              placeholder="f.eks. Januar 2024"
              className="input"
            />
          </div>

          {/* File Upload */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Excel/DAT filer (kan velge flere)
            </label>
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors">
                <Upload className="h-5 w-5" />
                <span>Velg filer</span>
                <input
                  type="file"
                  accept=".xlsx,.xls,.dat"
                  multiple
                  onChange={handleFileChange}
                  className="hidden"
                />
              </label>
              {files.length > 0 && (
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {files.length} fil(er) valgt
                </span>
              )}
            </div>
            {files.length > 0 && (
              <ul className="mt-2 text-sm text-gray-600 dark:text-gray-400 space-y-1">
                {files.map((file, i) => (
                  <li key={i} className="flex items-center gap-2">
                    <FileText className="h-4 w-4" />
                    {file.name}
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Commission Info */}
          {selectedDriverObj && (
            <div className="p-4 bg-primary-50 dark:bg-primary-900/20 rounded-lg">
              <p className="text-sm">
                <strong>Provisjon:</strong> {selectedDriverObj.commission_percentage}%
                <br />
                <span className="text-gray-600 dark:text-gray-400">
                  Lønn beregnes som bruttolønn × {selectedDriverObj.commission_percentage}%
                </span>
              </p>
            </div>
          )}

          {/* Upload Button */}
          <button
            onClick={handleUpload}
            disabled={files.length === 0 || !selectedDriver || uploading}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploading ? 'Laster opp...' : 'Last opp og beregn lønn'}
          </button>
        </div>
      </div>

      {/* Reports List */}
      <div className="card">
        <h2 className="text-2xl font-bold mb-6">Tidligere lønnsrapporter</h2>

        {reports.length === 0 ? (
          <p className="text-gray-500">Ingen rapporter ennå</p>
        ) : (
          <div className="space-y-4">
            {reports.map((report) => {
              const driver = drivers.find((d) => d.id === report.driver_id);
              return (
                <div
                  key={report.id}
                  className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <DollarSign className="h-5 w-5 text-green-600" />
                        <h3 className="font-semibold">
                          {driver?.name || 'Ukjent sjåfør'}
                          {report.report_period && ` - ${report.report_period}`}
                        </h3>
                      </div>
                      <div className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                        <p>
                          Opprettet: {new Date(report.created_at).toLocaleDateString('no-NO')}
                        </p>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-2 p-3 bg-gray-50 dark:bg-gray-700 rounded">
                          <div>
                            <span className="font-medium">Bruttolønn:</span>
                            <br />
                            {report.gross_salary?.toFixed(2)} kr
                          </div>
                          <div>
                            <span className="font-medium">Provisjon:</span>
                            <br />
                            {report.commission_percentage}%
                          </div>
                          <div>
                            <span className="font-medium">Nettolønn:</span>
                            <br />
                            {report.net_salary?.toFixed(2)} kr
                          </div>
                          <div>
                            <span className="font-medium">Tips:</span>
                            <br />
                            {report.tips?.toFixed(2)} kr
                          </div>
                        </div>
                        <p className="text-lg font-semibold text-green-600 dark:text-green-400 mt-2">
                          Total utbetaling: {((report.net_salary || 0) + (report.tips || 0)).toFixed(2)} kr
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => handleGeneratePDF(report.id)}
                      className="btn-secondary flex items-center gap-2"
                    >
                      <Download className="h-4 w-4" />
                      PDF
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
