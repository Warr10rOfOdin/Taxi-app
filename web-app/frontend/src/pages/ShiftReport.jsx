import { useState, useEffect } from 'react';
import { Upload, FileText, Download, Eye } from 'lucide-react';
import Papa from 'papaparse';
import jsPDF from 'jspdf';
import 'jspdf-autotable';
import { drivers as driverStorage, shiftReports } from '../storage/localStorage';

export default function ShiftReport() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [reports, setReports] = useState([]);
  const [selectedDriver, setSelectedDriver] = useState('');
  const [drivers, setDrivers] = useState([]);
  const [preview, setPreview] = useState(null);

  useEffect(() => {
    loadDrivers();
    loadReports();
  }, []);

  const loadDrivers = () => {
    try {
      setDrivers(driverStorage.getAll());
    } catch (error) {
      console.error('Error loading drivers:', error);
    }
  };

  const loadReports = () => {
    try {
      setReports(shiftReports.getAll());
    } catch (error) {
      console.error('Error loading reports:', error);
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;

    setFile(selectedFile);

    // Parse CSV file for preview
    Papa.parse(selectedFile, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        if (results.data && results.data.length > 0) {
          setPreview({
            row_count: results.data.length,
            columns: Object.keys(results.data[0]),
            preview: results.data.slice(0, 5), // Show first 5 rows
            fullData: results.data // Store full data for upload
          });
        }
      },
      error: (error) => {
        console.error('Error parsing file:', error);
        alert('Feil ved parsing av fil');
      }
    });
  };

  const handleUpload = () => {
    if (!file || !preview) {
      alert('Velg en fil først');
      return;
    }

    setUploading(true);
    try {
      // Calculate summary from the data
      const data = preview.fullData || [];

      // Try to find relevant columns for calculations
      const kontantCol = data.length > 0 ? Object.keys(data[0]).find(k => k.toLowerCase().includes('kontant')) : null;
      const kredittCol = data.length > 0 ? Object.keys(data[0]).find(k => k.toLowerCase().includes('kreditt') && !k.toLowerCase().includes('utlegg')) : null;
      const bomturCol = data.length > 0 ? Object.keys(data[0]).find(k => k.toLowerCase().includes('bomtur')) : null;
      const totalCol = data.length > 0 ? Object.keys(data[0]).find(k => k.toLowerCase().includes('total') && k.toLowerCase().includes('kroner')) : null;

      const summary = {
        total_kontant: kontantCol ? data.reduce((sum, row) => sum + (parseFloat(row[kontantCol]) || 0), 0) : 0,
        total_kreditt: kredittCol ? data.reduce((sum, row) => sum + (parseFloat(row[kredittCol]) || 0), 0) : 0,
        total_bomtur: bomturCol ? data.reduce((sum, row) => sum + (parseFloat(row[bomturCol]) || 0), 0) : 0,
        grand_total: totalCol ? data.reduce((sum, row) => sum + (parseFloat(row[totalCol]) || 0), 0) : 0,
      };

      // Create report
      const report = {
        file_name: file.name,
        driver_id: selectedDriver || null,
        data: preview.fullData,
        columns: preview.columns,
        summary: summary
      };

      shiftReports.create(report);
      alert('Rapport opprettet!');
      setFile(null);
      setPreview(null);
      setSelectedDriver('');
      loadReports();
    } catch (error) {
      console.error('Error uploading:', error);
      alert('Feil ved opplasting');
    } finally {
      setUploading(false);
    }
  };

  const handleGeneratePDF = (reportId) => {
    try {
      const report = shiftReports.getById(reportId);
      if (!report) {
        alert('Rapport ikke funnet');
        return;
      }

      // Create PDF
      const doc = new jsPDF('l', 'mm', 'a4'); // Landscape orientation

      // Add title
      doc.setFontSize(16);
      doc.text('Skiftrapport', 14, 15);

      // Add metadata
      doc.setFontSize(10);
      doc.text(`Fil: ${report.file_name}`, 14, 22);
      doc.text(`Opprettet: ${new Date(report.created_at).toLocaleDateString('no-NO')}`, 14, 27);

      // Add summary if available
      if (report.summary) {
        let yPos = 35;
        doc.setFontSize(12);
        doc.text('Sammendrag:', 14, yPos);
        yPos += 5;
        doc.setFontSize(10);
        doc.text(`Kontant: ${report.summary.total_kontant?.toFixed(2)} kr`, 14, yPos);
        yPos += 5;
        doc.text(`Kreditt: ${report.summary.total_kreditt?.toFixed(2)} kr`, 14, yPos);
        yPos += 5;
        doc.text(`Bomtur: ${report.summary.total_bomtur?.toFixed(2)} kr`, 14, yPos);
        yPos += 5;
        doc.text(`Totalt: ${report.summary.grand_total?.toFixed(2)} kr`, 14, yPos);
        yPos += 10;

        // Add table with data
        if (report.data && report.data.length > 0) {
          const tableColumns = report.columns.map(col => ({ header: col, dataKey: col }));
          doc.autoTable({
            startY: yPos,
            columns: tableColumns,
            body: report.data,
            styles: { fontSize: 8 },
            headStyles: { fillColor: [66, 139, 202] },
            margin: { left: 14 },
          });
        }
      }

      // Save PDF
      doc.save(`skiftrapport_${report.id}.pdf`);
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Feil ved PDF-generering');
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Upload Section */}
      <div className="card">
        <h2 className="text-2xl font-bold mb-6">Last opp skiftrapport</h2>

        <div className="space-y-4">
          {/* Driver Selection */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Sjåfør (valgfritt)
            </label>
            <select
              value={selectedDriver}
              onChange={(e) => setSelectedDriver(e.target.value)}
              className="input"
            >
              <option value="">Velg sjåfør...</option>
              {drivers.map((driver) => (
                <option key={driver.id} value={driver.id}>
                  {driver.name} ({driver.driver_id})
                </option>
              ))}
            </select>
          </div>

          {/* File Upload */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Excel/DAT fil
            </label>
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors">
                <Upload className="h-5 w-5" />
                <span>Velg fil</span>
                <input
                  type="file"
                  accept=".xlsx,.xls,.dat"
                  onChange={handleFileChange}
                  className="hidden"
                />
              </label>
              {file && (
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {file.name}
                </span>
              )}
            </div>
          </div>

          {/* Preview */}
          {preview && (
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-3">
                <Eye className="h-5 w-5 text-primary-600" />
                <h3 className="font-semibold">Forhåndsvisning</h3>
              </div>
              <div className="text-sm space-y-2">
                <p>
                  <strong>Rader:</strong> {preview.row_count}
                </p>
                <p>
                  <strong>Kolonner:</strong> {preview.columns.length}
                </p>
                <div className="overflow-x-auto mt-4">
                  <table className="table">
                    <thead>
                      <tr>
                        {preview.columns.slice(0, 5).map((col, i) => (
                          <th key={i}>{col}</th>
                        ))}
                        {preview.columns.length > 5 && <th>...</th>}
                      </tr>
                    </thead>
                    <tbody>
                      {preview.preview.slice(0, 3).map((row, i) => (
                        <tr key={i}>
                          {preview.columns.slice(0, 5).map((col, j) => (
                            <td key={j}>{row[col]}</td>
                          ))}
                          {preview.columns.length > 5 && <td>...</td>}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Upload Button */}
          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploading ? 'Laster opp...' : 'Last opp og opprett rapport'}
          </button>
        </div>
      </div>

      {/* Reports List */}
      <div className="card">
        <h2 className="text-2xl font-bold mb-6">Tidligere rapporter</h2>

        {reports.length === 0 ? (
          <p className="text-gray-500">Ingen rapporter ennå</p>
        ) : (
          <div className="space-y-4">
            {reports.map((report) => (
              <div
                key={report.id}
                className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <FileText className="h-5 w-5 text-primary-600" />
                      <h3 className="font-semibold">{report.file_name}</h3>
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                      <p>
                        Opprettet: {new Date(report.created_at).toLocaleDateString('no-NO')}
                      </p>
                      {report.summary && (
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-2">
                          <div>
                            <span className="font-medium">Kontant:</span> {report.summary.total_kontant?.toFixed(2)} kr
                          </div>
                          <div>
                            <span className="font-medium">Kreditt:</span> {report.summary.total_kreditt?.toFixed(2)} kr
                          </div>
                          <div>
                            <span className="font-medium">Bomtur:</span> {report.summary.total_bomtur?.toFixed(2)} kr
                          </div>
                          <div>
                            <span className="font-medium">Totalt:</span> {report.summary.grand_total?.toFixed(2)} kr
                          </div>
                        </div>
                      )}
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
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
