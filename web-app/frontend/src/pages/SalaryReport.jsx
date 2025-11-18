import { useState, useEffect } from 'react';
import { Upload, DollarSign, Download, FileText, Save, FolderOpen, Trash2, CheckSquare, Square } from 'lucide-react';
import Papa from 'papaparse';
import jsPDF from 'jspdf';
import 'jspdf-autotable';
import { drivers as driverStorage, salaryReports, companies as companyStorage } from '../storage/localStorage';

export default function SalaryReport() {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [reports, setReports] = useState([]);
  const [selectedDriver, setSelectedDriver] = useState('');
  const [reportPeriod, setReportPeriod] = useState('');
  const [drivers, setDrivers] = useState([]);
  const [allData, setAllData] = useState([]);
  const [selectedRows, setSelectedRows] = useState(new Set());
  const [showDataTable, setShowDataTable] = useState(false);
  const [columns, setColumns] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [showTemplateSave, setShowTemplateSave] = useState(false);
  const [templateName, setTemplateName] = useState('');
  const [companies, setCompanies] = useState([]);

  useEffect(() => {
    loadDrivers();
    loadReports();
    loadTemplates();
    loadCompanies();
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
      setReports(salaryReports.getAll());
    } catch (error) {
      console.error('Error loading reports:', error);
    }
  };

  const loadTemplates = () => {
    try {
      const saved = localStorage.getItem('salary_selection_templates');
      setTemplates(saved ? JSON.parse(saved) : []);
    } catch (error) {
      console.error('Error loading templates:', error);
    }
  };

  const loadCompanies = () => {
    try {
      setCompanies(companyStorage.getAll());
    } catch (error) {
      console.error('Error loading companies:', error);
    }
  };

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    if (selectedFiles.length === 0) return;

    setFiles(selectedFiles);
    parseAndCombineFiles(selectedFiles);
  };

  const parseAndCombineFiles = (fileList) => {
    let combinedData = [];
    let processedCount = 0;

    setUploading(true);

    fileList.forEach((file, fileIndex) => {
      Papa.parse(file, {
        header: true,
        skipEmptyLines: true,
        complete: (results) => {
          if (results.data && results.data.length > 0) {
            const dataWithSource = results.data.map((row, rowIndex) => ({
              ...row,
              _file_source: file.name,
              _original_index: `${fileIndex}_${rowIndex}`
            }));
            combinedData = combinedData.concat(dataWithSource);
          }

          processedCount++;

          if (processedCount === fileList.length) {
            if (combinedData.length > 0) {
              setAllData(combinedData);
              const cols = Object.keys(combinedData[0]).filter(k => !k.startsWith('_'));
              setColumns(cols);
              setShowDataTable(true);
              setSelectedRows(new Set());
            } else {
              alert('Ingen data funnet i filene');
            }
            setUploading(false);
          }
        },
        error: (error) => {
          console.error('Error parsing file:', error);
          processedCount++;
          if (processedCount === fileList.length) {
            setUploading(false);
            alert('Feil ved parsing av filer');
          }
        }
      });
    });
  };

  const toggleRowSelection = (index) => {
    const newSelection = new Set(selectedRows);
    if (newSelection.has(index)) {
      newSelection.delete(index);
    } else {
      newSelection.add(index);
    }
    setSelectedRows(newSelection);
  };

  const toggleSelectAll = () => {
    if (selectedRows.size === allData.length) {
      setSelectedRows(new Set());
    } else {
      setSelectedRows(new Set(allData.map((_, i) => i)));
    }
  };

  const handleSaveTemplate = () => {
    if (!templateName.trim()) {
      alert('Vennligst skriv inn et navn for malen');
      return;
    }

    const template = {
      id: Date.now().toString(),
      name: templateName,
      selectedIndices: Array.from(selectedRows),
      created_at: new Date().toISOString()
    };

    const updatedTemplates = [...templates, template];
    localStorage.setItem('salary_selection_templates', JSON.stringify(updatedTemplates));
    setTemplates(updatedTemplates);
    setTemplateName('');
    setShowTemplateSave(false);
    alert('Mal lagret!');
  };

  const handleLoadTemplate = (template) => {
    setSelectedRows(new Set(template.selectedIndices));
    alert(`Mal "${template.name}" lastet (${template.selectedIndices.length} rader)`);
  };

  const handleDeleteTemplate = (templateId) => {
    if (!confirm('Er du sikker på at du vil slette denne malen?')) return;

    const updatedTemplates = templates.filter(t => t.id !== templateId);
    localStorage.setItem('salary_selection_templates', JSON.stringify(updatedTemplates));
    setTemplates(updatedTemplates);
  };

  const handleGeneratePDF = () => {
    if (selectedRows.size === 0) {
      alert('Velg minst én rad for å generere PDF');
      return;
    }

    if (!selectedDriver) {
      alert('Velg en sjåfør');
      return;
    }

    try {
      const selectedData = allData.filter((_, index) => selectedRows.has(index));
      const driver = driverStorage.getById(selectedDriver);
      const company = companies.length > 0 ? companies[0] : null;

      // Calculate salary data from selected rows
      const lonnCol = columns.find(k => k.toLowerCase().includes('lonn') || k.toLowerCase() === 'lønn');
      const skattCol = columns.find(k => k.toLowerCase().includes('skatt'));
      const tipsCol = columns.find(k => k.toLowerCase().includes('tips'));

      const summary = {
        total_lonn: lonnCol ? selectedData.reduce((sum, row) => sum + (parseFloat(row[lonnCol]) || 0), 0) : 0,
        total_skatt: skattCol ? selectedData.reduce((sum, row) => sum + (parseFloat(row[skattCol]) || 0), 0) : 0,
        total_tips: tipsCol ? selectedData.reduce((sum, row) => sum + (parseFloat(row[tipsCol]) || 0), 0) : 0,
      };

      const nettoLonn = summary.total_lonn - summary.total_skatt;
      const totalUtbetaling = nettoLonn + summary.total_tips;

      // Create PDF
      const doc = new jsPDF('l', 'mm', 'a4');

      // Add title
      doc.setFontSize(16);
      doc.text('Lønnsrapport', 14, 15);

      // Add metadata
      doc.setFontSize(10);
      if (company) {
        doc.text(`${company.name}`, 14, 22);
        if (company.org_number) {
          doc.text(`Org.nr: ${company.org_number}`, 14, 27);
        }
      }
      doc.text(`Sjåfør: ${driver?.name || 'Ukjent'} (${driver?.driver_id || ''})`, 14, company ? 32 : 22);
      doc.text(`Periode: ${reportPeriod || new Date().toLocaleDateString('no-NO', { month: 'long', year: 'numeric' })}`, 14, company ? 37 : 27);
      doc.text(`Generert: ${new Date().toLocaleDateString('no-NO')}`, 14, company ? 42 : 32);
      doc.text(`Provisjon: ${driver?.commission_percentage || 0}%`, 14, company ? 47 : 37);

      let yPos = company ? 55 : 45;

      // Add summary
      doc.setFontSize(12);
      doc.text('Sammendrag:', 14, yPos);
      yPos += 6;
      doc.setFontSize(10);
      doc.text(`Total lønn: ${summary.total_lonn.toFixed(2)} kr`, 14, yPos);
      yPos += 5;
      doc.text(`Total skatt: ${summary.total_skatt.toFixed(2)} kr`, 14, yPos);
      yPos += 5;
      doc.text(`Netto lønn: ${nettoLonn.toFixed(2)} kr`, 14, yPos);
      yPos += 5;
      if (summary.total_tips > 0) {
        doc.text(`Tips: ${summary.total_tips.toFixed(2)} kr`, 14, yPos);
        yPos += 5;
      }
      doc.setFontSize(12);
      doc.text(`Total utbetaling: ${totalUtbetaling.toFixed(2)} kr`, 14, yPos);
      yPos += 10;

      // Add table with selected data
      const importantColumns = columns.slice(0, 10);

      const cleanedData = selectedData.map(row => {
        const cleanRow = {};
        importantColumns.forEach(col => {
          const value = row[col];
          if (typeof value === 'string' && value.length > 50) {
            cleanRow[col] = value.substring(0, 47) + '...';
          } else {
            cleanRow[col] = value || '';
          }
        });
        return cleanRow;
      });

      const tableColumns = importantColumns.map(col => ({
        header: col.length > 20 ? col.substring(0, 17) + '...' : col,
        dataKey: col
      }));

      doc.autoTable({
        startY: yPos,
        columns: tableColumns,
        body: cleanedData,
        styles: {
          fontSize: 7,
          cellPadding: 2,
          overflow: 'linebreak',
          cellWidth: 'wrap'
        },
        headStyles: {
          fillColor: [66, 139, 202],
          fontSize: 8,
          fontStyle: 'bold'
        },
        margin: { left: 10, right: 10 },
        tableWidth: 'auto',
        showHead: 'everyPage',
        didDrawPage: (data) => {
          const pageCount = doc.internal.getNumberOfPages();
          doc.setFontSize(8);
          doc.text(
            `Side ${data.pageNumber} av ${pageCount}`,
            doc.internal.pageSize.width / 2,
            doc.internal.pageSize.height - 10,
            { align: 'center' }
          );
        }
      });

      // Save PDF
      const timestamp = new Date().toISOString().split('T')[0];
      doc.save(`lonnsrapport_${driver?.name || 'ukjent'}_${timestamp}.pdf`);

      // Also save to reports for record keeping
      const report = {
        driver_id: selectedDriver,
        report_period: reportPeriod || new Date().toLocaleDateString('no-NO', { month: 'long', year: 'numeric' }),
        data: selectedData,
        columns: columns,
        summary: summary,
        gross_salary: summary.total_lonn,
        commission_percentage: driver?.commission_percentage || 0,
        net_salary: nettoLonn,
        tips: summary.total_tips,
        file_names: files.map(f => f.name).join(', ')
      };
      salaryReports.create(report);
      loadReports();

    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Feil ved PDF-generering: ' + error.message);
    }
  };

  const handleGeneratePDFFromReport = (reportId) => {
    try {
      const report = salaryReports.getById(reportId);
      if (!report) {
        alert('Rapport ikke funnet');
        return;
      }

      const driver = driverStorage.getById(report.driver_id);
      const company = companies.length > 0 ? companies[0] : null;

      // Create PDF
      const doc = new jsPDF('l', 'mm', 'a4');

      // Add title
      doc.setFontSize(16);
      doc.text('Lønnsrapport', 14, 15);

      // Add metadata
      doc.setFontSize(10);
      if (company) {
        doc.text(`${company.name}`, 14, 22);
        if (company.org_number) {
          doc.text(`Org.nr: ${company.org_number}`, 14, 27);
        }
      }
      doc.text(`Sjåfør: ${driver?.name || 'Ukjent'} (${driver?.driver_id || ''})`, 14, company ? 32 : 22);
      doc.text(`Periode: ${report.report_period}`, 14, company ? 37 : 27);
      doc.text(`Opprettet: ${new Date(report.created_at).toLocaleDateString('no-NO')}`, 14, company ? 42 : 32);

      let yPos = company ? 50 : 40;

      // Add summary
      doc.setFontSize(12);
      doc.text('Sammendrag:', 14, yPos);
      yPos += 6;
      doc.setFontSize(10);
      doc.text(`Total lønn: ${report.summary?.total_lonn?.toFixed(2) || '0.00'} kr`, 14, yPos);
      yPos += 5;
      doc.text(`Total skatt: ${report.summary?.total_skatt?.toFixed(2) || '0.00'} kr`, 14, yPos);
      yPos += 5;
      const nettoLonn = (report.summary?.total_lonn || 0) - (report.summary?.total_skatt || 0);
      doc.text(`Netto lønn: ${nettoLonn.toFixed(2)} kr`, 14, yPos);
      yPos += 5;
      if (report.tips && report.tips > 0) {
        doc.text(`Tips: ${report.tips.toFixed(2)} kr`, 14, yPos);
        yPos += 5;
      }
      doc.setFontSize(12);
      const totalUtbetaling = nettoLonn + (report.tips || 0);
      doc.text(`Total utbetaling: ${totalUtbetaling.toFixed(2)} kr`, 14, yPos);
      yPos += 10;

      // Add table with data
      if (report.data && report.data.length > 0) {
        const importantColumns = report.columns.slice(0, 10);

        const cleanedData = report.data.map(row => {
          const cleanRow = {};
          importantColumns.forEach(col => {
            const value = row[col];
            if (typeof value === 'string' && value.length > 50) {
              cleanRow[col] = value.substring(0, 47) + '...';
            } else {
              cleanRow[col] = value || '';
            }
          });
          return cleanRow;
        });

        const tableColumns = importantColumns.map(col => ({
          header: col.length > 20 ? col.substring(0, 17) + '...' : col,
          dataKey: col
        }));

        doc.autoTable({
          startY: yPos,
          columns: tableColumns,
          body: cleanedData,
          styles: {
            fontSize: 7,
            cellPadding: 2,
            overflow: 'linebreak',
            cellWidth: 'wrap'
          },
          headStyles: {
            fillColor: [66, 139, 202],
            fontSize: 8,
            fontStyle: 'bold'
          },
          margin: { left: 10, right: 10 },
          tableWidth: 'auto',
          showHead: 'everyPage',
          didDrawPage: (data) => {
            const pageCount = doc.internal.getNumberOfPages();
            doc.setFontSize(8);
            doc.text(
              `Side ${data.pageNumber} av ${pageCount}`,
              doc.internal.pageSize.width / 2,
              doc.internal.pageSize.height - 10,
              { align: 'center' }
            );
          }
        });
      }

      // Save PDF
      doc.save(`lonnsrapport_${driver?.name || report.id}_${report.report_period}.pdf`);
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Feil ved PDF-generering: ' + error.message);
    }
  };

  const selectedDriverObj = drivers.find((d) => d.id === selectedDriver);

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
              DAT filer (velg én eller flere)
            </label>
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors">
                <Upload className="h-5 w-5" />
                <span>Velg filer</span>
                <input
                  type="file"
                  accept=".dat,.csv"
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

          {uploading && (
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Laster og kombinerer filer...
            </div>
          )}
        </div>
      </div>

      {/* Data Table with Selection */}
      {showDataTable && allData.length > 0 && (
        <div className="card">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">
              Velg rader for rapport ({selectedRows.size} av {allData.length} valgt)
            </h2>
            <div className="flex gap-2">
              <button
                onClick={toggleSelectAll}
                className="btn-secondary flex items-center gap-2"
              >
                {selectedRows.size === allData.length ? <Square className="h-4 w-4" /> : <CheckSquare className="h-4 w-4" />}
                {selectedRows.size === allData.length ? 'Fjern alle' : 'Velg alle'}
              </button>
            </div>
          </div>

          {/* Data Table */}
          <div className="overflow-x-auto mb-4 max-h-96 overflow-y-auto border border-gray-200 dark:border-gray-700 rounded-lg">
            <table className="table">
              <thead className="sticky top-0 bg-white dark:bg-gray-800 z-10">
                <tr>
                  <th className="w-12">Velg</th>
                  <th>Fil</th>
                  {columns.slice(0, 8).map((col, i) => (
                    <th key={i}>{col}</th>
                  ))}
                  {columns.length > 8 && <th>...</th>}
                </tr>
              </thead>
              <tbody>
                {allData.map((row, index) => (
                  <tr key={index} className={selectedRows.has(index) ? 'bg-primary-50 dark:bg-primary-900/20' : ''}>
                    <td>
                      <input
                        type="checkbox"
                        checked={selectedRows.has(index)}
                        onChange={() => toggleRowSelection(index)}
                        className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                      />
                    </td>
                    <td className="text-xs text-gray-500">{row._file_source}</td>
                    {columns.slice(0, 8).map((col, j) => (
                      <td key={j} className="text-sm">
                        {typeof row[col] === 'string' && row[col].length > 30
                          ? row[col].substring(0, 27) + '...'
                          : row[col]}
                      </td>
                    ))}
                    {columns.length > 8 && <td className="text-xs text-gray-400">...</td>}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-3">
            <button
              onClick={handleGeneratePDF}
              disabled={selectedRows.size === 0 || !selectedDriver}
              className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Download className="h-4 w-4" />
              Generer PDF fra valgte rader
            </button>

            <button
              onClick={() => setShowTemplateSave(true)}
              disabled={selectedRows.size === 0}
              className="btn-secondary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Save className="h-4 w-4" />
              Lagre valg som mal
            </button>
          </div>

          {/* Template Save Modal */}
          {showTemplateSave && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
              <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
                <h3 className="text-xl font-bold mb-4">Lagre mal</h3>
                <input
                  type="text"
                  value={templateName}
                  onChange={(e) => setTemplateName(e.target.value)}
                  placeholder="Navn på mal..."
                  className="input mb-4"
                />
                <div className="flex justify-end gap-2">
                  <button
                    onClick={() => {
                      setShowTemplateSave(false);
                      setTemplateName('');
                    }}
                    className="btn-secondary"
                  >
                    Avbryt
                  </button>
                  <button onClick={handleSaveTemplate} className="btn-primary">
                    Lagre
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Saved Templates */}
      {templates.length > 0 && showDataTable && (
        <div className="card">
          <h2 className="text-2xl font-bold mb-4">Lagrede maler</h2>
          <div className="space-y-2">
            {templates.map((template) => (
              <div
                key={template.id}
                className="flex items-center justify-between p-3 border border-gray-200 dark:border-gray-700 rounded-lg"
              >
                <div>
                  <h3 className="font-semibold">{template.name}</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {template.selectedIndices.length} rader - Opprettet {new Date(template.created_at).toLocaleDateString('no-NO')}
                  </p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleLoadTemplate(template)}
                    className="btn-secondary flex items-center gap-2"
                  >
                    <FolderOpen className="h-4 w-4" />
                    Last
                  </button>
                  <button
                    onClick={() => handleDeleteTemplate(template.id)}
                    className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded text-red-600"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Previously Saved Reports */}
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
                            {report.gross_salary?.toFixed(2) || '0.00'} kr
                          </div>
                          <div>
                            <span className="font-medium">Provisjon:</span>
                            <br />
                            {report.commission_percentage || 0}%
                          </div>
                          <div>
                            <span className="font-medium">Nettolønn:</span>
                            <br />
                            {report.net_salary?.toFixed(2) || '0.00'} kr
                          </div>
                          <div>
                            <span className="font-medium">Tips:</span>
                            <br />
                            {report.tips?.toFixed(2) || '0.00'} kr
                          </div>
                        </div>
                        <p className="text-lg font-semibold text-green-600 dark:text-green-400 mt-2">
                          Total utbetaling: {((report.net_salary || 0) + (report.tips || 0)).toFixed(2)} kr
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => handleGeneratePDFFromReport(report.id)}
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
