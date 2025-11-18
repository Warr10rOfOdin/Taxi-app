import { useState, useEffect } from 'react';
import { Upload, FileText, Download, Eye, Save, FolderOpen, Trash2, CheckSquare, Square } from 'lucide-react';
import Papa from 'papaparse';
import jsPDF from 'jspdf';
import 'jspdf-autotable';
import { drivers as driverStorage, shiftReports, companies as companyStorage } from '../storage/localStorage';

export default function ShiftReport() {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [reports, setReports] = useState([]);
  const [selectedDriver, setSelectedDriver] = useState('');
  const [drivers, setDrivers] = useState([]);
  const [allData, setAllData] = useState([]); // Combined data from all files
  const [selectedRows, setSelectedRows] = useState(new Set()); // Selected row indices
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
      setReports(shiftReports.getAll());
    } catch (error) {
      console.error('Error loading reports:', error);
    }
  };

  const loadTemplates = () => {
    try {
      const saved = localStorage.getItem('shift_selection_templates');
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
            // Add file source to each row for tracking
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
              // Get columns excluding our internal tracking fields
              const cols = Object.keys(combinedData[0]).filter(k => !k.startsWith('_'));
              setColumns(cols);
              setShowDataTable(true);
              setSelectedRows(new Set()); // Reset selections
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
    localStorage.setItem('shift_selection_templates', JSON.stringify(updatedTemplates));
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
    localStorage.setItem('shift_selection_templates', JSON.stringify(updatedTemplates));
    setTemplates(updatedTemplates);
  };

  const handleGeneratePDF = () => {
    if (selectedRows.size === 0) {
      alert('Velg minst én rad for å generere PDF');
      return;
    }

    try {
      // Get only selected rows
      const selectedData = allData.filter((_, index) => selectedRows.has(index));

      // Create PDF
      const doc = new jsPDF('l', 'mm', 'a4'); // Landscape orientation

      // Get company info for header
      const company = companies.length > 0 ? companies[0] : null;

      // Add title
      doc.setFontSize(16);
      doc.text('Skiftrapport', 14, 15);

      // Add metadata
      doc.setFontSize(10);
      if (company) {
        doc.text(`${company.name}`, 14, 22);
        if (company.org_number) {
          doc.text(`Org.nr: ${company.org_number}`, 14, 27);
        }
      }
      doc.text(`Generert: ${new Date().toLocaleDateString('no-NO')}`, 14, company ? 32 : 27);
      doc.text(`Antall rader: ${selectedData.length}`, 14, company ? 37 : 32);

      let yPos = company ? 45 : 40;

      // Calculate summary from selected data
      const kontantCol = columns.find(k => k.toLowerCase().includes('kontant'));
      const kredittCol = columns.find(k => k.toLowerCase().includes('kreditt') && !k.toLowerCase().includes('utlegg'));
      const bomturCol = columns.find(k => k.toLowerCase().includes('bomtur'));
      const totalCol = columns.find(k => k.toLowerCase().includes('total') && k.toLowerCase().includes('kroner'));

      const summary = {
        total_kontant: kontantCol ? selectedData.reduce((sum, row) => sum + (parseFloat(row[kontantCol]) || 0), 0) : 0,
        total_kreditt: kredittCol ? selectedData.reduce((sum, row) => sum + (parseFloat(row[kredittCol]) || 0), 0) : 0,
        total_bomtur: bomturCol ? selectedData.reduce((sum, row) => sum + (parseFloat(row[bomturCol]) || 0), 0) : 0,
        grand_total: totalCol ? selectedData.reduce((sum, row) => sum + (parseFloat(row[totalCol]) || 0), 0) : 0,
      };

      // Add summary
      doc.setFontSize(12);
      doc.text('Sammendrag:', 14, yPos);
      yPos += 6;
      doc.setFontSize(10);
      doc.text(`Kontant: ${summary.total_kontant.toFixed(2)} kr`, 14, yPos);
      yPos += 5;
      doc.text(`Kreditt: ${summary.total_kreditt.toFixed(2)} kr`, 14, yPos);
      yPos += 5;
      doc.text(`Bomtur: ${summary.total_bomtur.toFixed(2)} kr`, 14, yPos);
      yPos += 5;
      doc.text(`Totalt: ${summary.grand_total.toFixed(2)} kr`, 14, yPos);
      yPos += 10;

      // Add table with selected data - limit columns for readability
      const importantColumns = columns.slice(0, 10);

      // Clean and prepare data
      const cleanedData = selectedData.map(row => {
        const cleanRow = {};
        importantColumns.forEach(col => {
          const value = row[col];
          // Truncate long text to prevent overflow
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
          // Add page numbers
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
      doc.save(`skiftrapport_${timestamp}.pdf`);

      // Also save to reports for record keeping
      const report = {
        file_name: `Valgte rader fra ${files.length} fil(er)`,
        driver_id: selectedDriver || null,
        data: selectedData,
        columns: columns,
        summary: summary
      };
      shiftReports.create(report);
      loadReports();

    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Feil ved PDF-generering: ' + error.message);
    }
  };

  const handleGeneratePDFFromReport = (reportId) => {
    try {
      const report = shiftReports.getById(reportId);
      if (!report) {
        alert('Rapport ikke funnet');
        return;
      }

      // Create PDF
      const doc = new jsPDF('l', 'mm', 'a4');

      // Get company info
      const company = companies.length > 0 ? companies[0] : null;

      // Add title
      doc.setFontSize(16);
      doc.text('Skiftrapport', 14, 15);

      // Add metadata
      doc.setFontSize(10);
      if (company) {
        doc.text(`${company.name}`, 14, 22);
        if (company.org_number) {
          doc.text(`Org.nr: ${company.org_number}`, 14, 27);
        }
      }
      doc.text(`Fil: ${report.file_name}`, 14, company ? 32 : 22);
      doc.text(`Opprettet: ${new Date(report.created_at).toLocaleDateString('no-NO')}`, 14, company ? 37 : 27);

      let yPos = company ? 45 : 35;

      // Add summary if available
      if (report.summary) {
        doc.setFontSize(12);
        doc.text('Sammendrag:', 14, yPos);
        yPos += 6;
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
      }

      // Save PDF
      doc.save(`skiftrapport_${report.id}.pdf`);
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Feil ved PDF-generering: ' + error.message);
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Upload Section */}
      <div className="card">
        <h2 className="text-2xl font-bold mb-6">Last opp skiftrapporter</h2>

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
              DAT filer (velg én eller flere)
            </label>
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors">
                <Upload className="h-5 w-5" />
                <span>Velg filer</span>
                <input
                  type="file"
                  accept=".dat,.csv"
                  onChange={handleFileChange}
                  className="hidden"
                  multiple
                />
              </label>
              {files.length > 0 && (
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {files.length} fil(er) valgt
                </span>
              )}
            </div>
          </div>

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
              disabled={selectedRows.size === 0}
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
                    onClick={() => handleGeneratePDFFromReport(report.id)}
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
