import { useState, useEffect } from 'react';
import { Upload, Download, FileText, Calendar, CreditCard } from 'lucide-react';
import * as XLSX from 'xlsx';
import jsPDF from 'jspdf';
import 'jspdf-autotable';
import { transactionReports, companies as companyStorage } from '../storage/localStorage';

export default function TransactionReport() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [transactions, setTransactions] = useState([]);
  const [groupedData, setGroupedData] = useState([]);
  const [reports, setReports] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [reportMonth, setReportMonth] = useState('');
  const [accountInfo, setAccountInfo] = useState({
    kontoId: '',
    inneholderId: '',
    fornavn: '',
    etternavn: '',
    firmanavn: '',
    markedsnavn: '',
    telefon: '',
    email: '',
    adresse: ''
  });

  useEffect(() => {
    loadReports();
    loadCompanies();
    // Set default month to current month
    const now = new Date();
    setReportMonth(`${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`);
  }, []);

  const loadReports = () => {
    try {
      setReports(transactionReports.getAll());
    } catch (error) {
      console.error('Error loading reports:', error);
    }
  };

  const loadCompanies = () => {
    try {
      const loadedCompanies = companyStorage.getAll();
      setCompanies(loadedCompanies);

      // Pre-fill account info from first company if available
      if (loadedCompanies.length > 0) {
        const company = loadedCompanies[0];
        setAccountInfo(prev => ({
          ...prev,
          firmanavn: company.name || '',
          markedsnavn: company.name || '',
          adresse: company.address || ''
        }));
      }
    } catch (error) {
      console.error('Error loading companies:', error);
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      parseExcelFile(selectedFile);
    }
  };

  const parseExcelFile = (file) => {
    setUploading(true);
    const reader = new FileReader();

    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, { type: 'array' });

        // Get the first sheet
        const sheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[sheetName];

        // Convert to JSON
        const jsonData = XLSX.utils.sheet_to_json(worksheet);

        setTransactions(jsonData);

        // Group by payout date
        const grouped = groupByPayoutDate(jsonData);
        setGroupedData(grouped);

        setUploading(false);
      } catch (error) {
        console.error('Error parsing Excel file:', error);
        alert('Feil ved parsing av Excel-fil: ' + error.message);
        setUploading(false);
      }
    };

    reader.onerror = (error) => {
      console.error('Error reading file:', error);
      alert('Feil ved lesing av fil');
      setUploading(false);
    };

    reader.readAsArrayBuffer(file);
  };

  const groupByPayoutDate = (data) => {
    const groups = {};

    data.forEach(row => {
      // Try to find payout date column (might be named differently)
      const payoutDate = row['Payout Date'] || row['PayoutDate'] || row['Utbetalingsdato'] || row['payout_date'];

      if (!payoutDate) return;

      const dateStr = formatDate(payoutDate);

      if (!groups[dateStr]) {
        groups[dateStr] = {
          payoutDate: dateStr,
          transactions: [],
          fromDate: null,
          toDate: null,
          brutto: 0,
          avgifter: 0,
          netto: 0,
          cardTypes: {}
        };
      }

      groups[dateStr].transactions.push(row);

      // Extract financial data
      const brutto = parseFloat(row['Brutto'] || row['Gross'] || row['brutto'] || 0);
      const avgifter = parseFloat(row['Avgifter'] || row['Fees'] || row['avgifter'] || 0);
      const netto = parseFloat(row['Netto'] || row['Net'] || row['Netto utbetalt'] || row['netto'] || 0);

      groups[dateStr].brutto += brutto;
      groups[dateStr].avgifter += avgifter;
      groups[dateStr].netto += netto;

      // Track card types
      const cardType = row['Kort type'] || row['CardType'] || row['card_type'] || 'UNKNOWN';
      if (!groups[dateStr].cardTypes[cardType]) {
        groups[dateStr].cardTypes[cardType] = 0;
      }
      groups[dateStr].cardTypes[cardType] += netto;

      // Track date range (Fra - Til)
      const transDate = row['Fra'] || row['From'] || row['fra'] || row['Dato'] || row['Date'];
      if (transDate) {
        const date = new Date(transDate);
        if (!groups[dateStr].fromDate || date < new Date(groups[dateStr].fromDate)) {
          groups[dateStr].fromDate = formatDateTime(transDate);
        }
        if (!groups[dateStr].toDate || date > new Date(groups[dateStr].toDate)) {
          groups[dateStr].toDate = formatDateTime(transDate);
        }
      }

      const toDate = row['Til'] || row['To'] || row['til'];
      if (toDate) {
        const date = new Date(toDate);
        if (!groups[dateStr].toDate || date > new Date(groups[dateStr].toDate)) {
          groups[dateStr].toDate = formatDateTime(toDate);
        }
      }
    });

    // Convert to array and sort by date
    return Object.values(groups).sort((a, b) =>
      new Date(a.payoutDate) - new Date(b.payoutDate)
    );
  };

  const formatDate = (dateValue) => {
    try {
      // Handle Excel date serial number
      if (typeof dateValue === 'number') {
        const date = new Date((dateValue - 25569) * 86400 * 1000);
        return date.toISOString().split('T')[0];
      }

      // Handle string date
      const date = new Date(dateValue);
      return date.toISOString().split('T')[0];
    } catch (error) {
      return dateValue;
    }
  };

  const formatDateTime = (dateValue) => {
    try {
      // Handle Excel date serial number
      if (typeof dateValue === 'number') {
        const date = new Date((dateValue - 25569) * 86400 * 1000);
        return date.toLocaleString('no-NO', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
      }

      // Handle string date
      const date = new Date(dateValue);
      return date.toLocaleString('no-NO', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (error) {
      return dateValue;
    }
  };

  const filterByMonth = (data, month) => {
    if (!month) return data;

    return data.filter(group => {
      const groupDate = new Date(group.payoutDate);
      const monthStr = `${groupDate.getFullYear()}-${String(groupDate.getMonth() + 1).padStart(2, '0')}`;
      return monthStr === month;
    });
  };

  const handleGeneratePDF = () => {
    if (groupedData.length === 0) {
      alert('Ingen transaksjoner å generere rapport for');
      return;
    }

    try {
      const filteredData = filterByMonth(groupedData, reportMonth);

      if (filteredData.length === 0) {
        alert('Ingen transaksjoner funnet for valgt måned');
        return;
      }

      const doc = new jsPDF('p', 'mm', 'a4');
      const pageWidth = doc.internal.pageSize.width;

      // Add header
      doc.setFontSize(18);
      doc.text('TDSPay Oppgjørsrapport', pageWidth / 2, 20, { align: 'center' });

      // Add account info
      doc.setFontSize(9);
      let yPos = 35;

      const leftCol = 14;
      const rightCol = 110;

      // Left column
      if (accountInfo.kontoId) {
        doc.text(`Konto ID`, leftCol, yPos);
        doc.text(accountInfo.kontoId, leftCol + 30, yPos);
      }

      // Right column
      if (accountInfo.fornavn) {
        doc.text(`Fornavn`, rightCol, yPos);
        doc.text(accountInfo.fornavn, rightCol + 25, yPos);
      }
      yPos += 5;

      // Left column
      if (accountInfo.inneholderId) {
        doc.text(`Innehaver ID`, leftCol, yPos);
        doc.text(accountInfo.inneholderId, leftCol + 30, yPos);
      }

      // Right column
      if (accountInfo.etternavn) {
        doc.text(`Etternavn`, rightCol, yPos);
        doc.text(accountInfo.etternavn, rightCol + 25, yPos);
      }
      yPos += 5;

      // Left column
      if (accountInfo.firmanavn) {
        doc.text(`Firmanavn`, leftCol, yPos);
        doc.text(accountInfo.firmanavn, leftCol + 30, yPos);
      }

      // Right column
      if (accountInfo.telefon) {
        doc.text(`Telefon`, rightCol, yPos);
        doc.text(accountInfo.telefon, rightCol + 25, yPos);
      }
      yPos += 5;

      // Left column
      if (accountInfo.markedsnavn) {
        doc.text(`Markedsnavn`, leftCol, yPos);
        doc.text(accountInfo.markedsnavn, leftCol + 30, yPos);
      }

      // Right column
      if (accountInfo.email) {
        doc.text(`Email`, rightCol, yPos);
        doc.text(accountInfo.email, rightCol + 25, yPos);
      }
      yPos += 5;

      // Address (full width)
      if (accountInfo.adresse) {
        doc.text(`Adresse`, leftCol, yPos);
        doc.text(accountInfo.adresse, leftCol + 30, yPos);
        yPos += 5;
      }

      yPos += 5;

      // Add table for each payout period
      filteredData.forEach((group, index) => {
        if (index > 0) {
          yPos += 10;
        }

        // Check if we need a new page
        if (yPos > 250) {
          doc.addPage();
          yPos = 20;
        }

        // Payout date header row
        const payoutDateFormatted = new Date(group.payoutDate).toLocaleDateString('no-NO');
        const tableData = [[
          payoutDateFormatted,
          group.fromDate || '-',
          group.toDate || '-',
          'NOK',
          group.brutto.toFixed(2),
          group.avgifter.toFixed(2),
          group.netto.toFixed(2)
        ]];

        doc.autoTable({
          startY: yPos,
          head: [['Payout Date', 'Fra', 'Til', 'Val', 'Brutto', 'Avgifter', 'Netto utbetalt']],
          body: tableData,
          theme: 'grid',
          styles: {
            fontSize: 8,
            cellPadding: 2
          },
          headStyles: {
            fillColor: [240, 240, 240],
            textColor: [0, 0, 0],
            fontStyle: 'bold'
          },
          columnStyles: {
            4: { halign: 'right' },
            5: { halign: 'right' },
            6: { halign: 'right' }
          }
        });

        yPos = doc.lastAutoTable.finalY + 2;

        // Card type breakdown
        const cardData = Object.entries(group.cardTypes).map(([type, amount]) => [
          type,
          amount.toFixed(2)
        ]);

        if (cardData.length > 0) {
          doc.autoTable({
            startY: yPos,
            head: [['Kort typer', 'Netto']],
            body: cardData,
            theme: 'plain',
            styles: {
              fontSize: 8,
              cellPadding: 2
            },
            headStyles: {
              fontStyle: 'bold'
            },
            columnStyles: {
              1: { halign: 'right' }
            },
            margin: { left: 20 }
          });

          yPos = doc.lastAutoTable.finalY;
        }
      });

      // Add footer
      const monthName = new Date(reportMonth + '-01').toLocaleDateString('no-NO', { month: 'long', year: 'numeric' });
      const fileName = `Oppgjorsrapport_${monthName.replace(' ', '_')}_${new Date().toISOString().split('T')[0]}.pdf`;

      doc.save(fileName);

      // Save report to storage
      const report = {
        report_month: reportMonth,
        account_info: accountInfo,
        summary_data: filteredData,
        total_brutto: filteredData.reduce((sum, g) => sum + g.brutto, 0),
        total_avgifter: filteredData.reduce((sum, g) => sum + g.avgifter, 0),
        total_netto: filteredData.reduce((sum, g) => sum + g.netto, 0),
        file_name: file?.name
      };

      transactionReports.create(report);
      loadReports();

    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Feil ved PDF-generering: ' + error.message);
    }
  };

  const handleGeneratePDFFromReport = (reportId) => {
    try {
      const report = transactionReports.getById(reportId);
      if (!report) {
        alert('Rapport ikke funnet');
        return;
      }

      const doc = new jsPDF('p', 'mm', 'a4');
      const pageWidth = doc.internal.pageSize.width;

      // Add header
      doc.setFontSize(18);
      doc.text('TDSPay Oppgjørsrapport', pageWidth / 2, 20, { align: 'center' });

      // Add account info
      doc.setFontSize(9);
      let yPos = 35;

      const leftCol = 14;
      const rightCol = 110;
      const info = report.account_info || {};

      // Left column
      if (info.kontoId) {
        doc.text(`Konto ID`, leftCol, yPos);
        doc.text(info.kontoId, leftCol + 30, yPos);
      }

      // Right column
      if (info.fornavn) {
        doc.text(`Fornavn`, rightCol, yPos);
        doc.text(info.fornavn, rightCol + 25, yPos);
      }
      yPos += 5;

      // Add remaining info fields...
      if (info.inneholderId) {
        doc.text(`Innehaver ID`, leftCol, yPos);
        doc.text(info.inneholderId, leftCol + 30, yPos);
      }

      if (info.etternavn) {
        doc.text(`Etternavn`, rightCol, yPos);
        doc.text(info.etternavn, rightCol + 25, yPos);
      }
      yPos += 5;

      if (info.firmanavn) {
        doc.text(`Firmanavn`, leftCol, yPos);
        doc.text(info.firmanavn, leftCol + 30, yPos);
      }

      if (info.telefon) {
        doc.text(`Telefon`, rightCol, yPos);
        doc.text(info.telefon, rightCol + 25, yPos);
      }
      yPos += 5;

      if (info.markedsnavn) {
        doc.text(`Markedsnavn`, leftCol, yPos);
        doc.text(info.markedsnavn, leftCol + 30, yPos);
      }

      if (info.email) {
        doc.text(`Email`, rightCol, yPos);
        doc.text(info.email, rightCol + 25, yPos);
      }
      yPos += 5;

      if (info.adresse) {
        doc.text(`Adresse`, leftCol, yPos);
        doc.text(info.adresse, leftCol + 30, yPos);
        yPos += 5;
      }

      yPos += 5;

      // Add table data
      report.summary_data.forEach((group, index) => {
        if (index > 0) {
          yPos += 10;
        }

        if (yPos > 250) {
          doc.addPage();
          yPos = 20;
        }

        const payoutDateFormatted = new Date(group.payoutDate).toLocaleDateString('no-NO');
        const tableData = [[
          payoutDateFormatted,
          group.fromDate || '-',
          group.toDate || '-',
          'NOK',
          group.brutto.toFixed(2),
          group.avgifter.toFixed(2),
          group.netto.toFixed(2)
        ]];

        doc.autoTable({
          startY: yPos,
          head: [['Payout Date', 'Fra', 'Til', 'Val', 'Brutto', 'Avgifter', 'Netto utbetalt']],
          body: tableData,
          theme: 'grid',
          styles: {
            fontSize: 8,
            cellPadding: 2
          },
          headStyles: {
            fillColor: [240, 240, 240],
            textColor: [0, 0, 0],
            fontStyle: 'bold'
          },
          columnStyles: {
            4: { halign: 'right' },
            5: { halign: 'right' },
            6: { halign: 'right' }
          }
        });

        yPos = doc.lastAutoTable.finalY + 2;

        const cardData = Object.entries(group.cardTypes).map(([type, amount]) => [
          type,
          amount.toFixed(2)
        ]);

        if (cardData.length > 0) {
          doc.autoTable({
            startY: yPos,
            head: [['Kort typer', 'Netto']],
            body: cardData,
            theme: 'plain',
            styles: {
              fontSize: 8,
              cellPadding: 2
            },
            headStyles: {
              fontStyle: 'bold'
            },
            columnStyles: {
              1: { halign: 'right' }
            },
            margin: { left: 20 }
          });

          yPos = doc.lastAutoTable.finalY;
        }
      });

      const monthName = new Date(report.report_month + '-01').toLocaleDateString('no-NO', { month: 'long', year: 'numeric' });
      const fileName = `Oppgjorsrapport_${monthName.replace(' ', '_')}.pdf`;

      doc.save(fileName);
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Feil ved PDF-generering: ' + error.message);
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Upload Section */}
      <div className="card">
        <h2 className="text-2xl font-bold mb-6">Transaksjon Oppgjørsrapport</h2>

        <div className="space-y-4">
          {/* Account Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Konto ID</label>
              <input
                type="text"
                value={accountInfo.kontoId}
                onChange={(e) => setAccountInfo({ ...accountInfo, kontoId: e.target.value })}
                placeholder="AH32DHB22322845LBZLX2C9XB"
                className="input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Innehaver ID</label>
              <input
                type="text"
                value={accountInfo.inneholderId}
                onChange={(e) => setAccountInfo({ ...accountInfo, inneholderId: e.target.value })}
                placeholder="1DD9DE14-5D4F-40D1-9EDC-201"
                className="input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Fornavn</label>
              <input
                type="text"
                value={accountInfo.fornavn}
                onChange={(e) => setAccountInfo({ ...accountInfo, fornavn: e.target.value })}
                placeholder="Toni Reime"
                className="input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Etternavn</label>
              <input
                type="text"
                value={accountInfo.etternavn}
                onChange={(e) => setAccountInfo({ ...accountInfo, etternavn: e.target.value })}
                placeholder="Kolve"
                className="input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Firmanavn</label>
              <input
                type="text"
                value={accountInfo.firmanavn}
                onChange={(e) => setAccountInfo({ ...accountInfo, firmanavn: e.target.value })}
                placeholder="Kolve ST"
                className="input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Markedsnavn</label>
              <input
                type="text"
                value={accountInfo.markedsnavn}
                onChange={(e) => setAccountInfo({ ...accountInfo, markedsnavn: e.target.value })}
                placeholder="Kolve ST"
                className="input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Telefon</label>
              <input
                type="text"
                value={accountInfo.telefon}
                onChange={(e) => setAccountInfo({ ...accountInfo, telefon: e.target.value })}
                placeholder="+4747747174"
                className="input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Email</label>
              <input
                type="email"
                value={accountInfo.email}
                onChange={(e) => setAccountInfo({ ...accountInfo, email: e.target.value })}
                placeholder="kolvetaxi@gmail.com"
                className="input"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium mb-2">Adresse</label>
              <input
                type="text"
                value={accountInfo.adresse}
                onChange={(e) => setAccountInfo({ ...accountInfo, adresse: e.target.value })}
                placeholder="Kolvesvegen 181, 5706, Voss, Norway"
                className="input"
              />
            </div>
          </div>

          {/* Month Selection */}
          <div>
            <label className="block text-sm font-medium mb-2">
              <Calendar className="inline h-4 w-4 mr-1" />
              Rapportmåned
            </label>
            <input
              type="month"
              value={reportMonth}
              onChange={(e) => setReportMonth(e.target.value)}
              className="input"
            />
          </div>

          {/* File Upload */}
          <div>
            <label className="block text-sm font-medium mb-2">
              <FileText className="inline h-4 w-4 mr-1" />
              Transaksjonsfil (Excel)
            </label>
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors">
                <Upload className="h-5 w-5" />
                <span>Velg Excel-fil</span>
                <input
                  type="file"
                  accept=".xlsx,.xls"
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

          {uploading && (
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Laster og prosesserer fil...
            </div>
          )}
        </div>
      </div>

      {/* Data Preview */}
      {groupedData.length > 0 && (
        <div className="card">
          <h2 className="text-2xl font-bold mb-4">Transaksjonssammendrag</h2>

          <div className="mb-4 p-4 bg-primary-50 dark:bg-primary-900/20 rounded-lg">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Brutto</p>
                <p className="text-2xl font-bold">
                  {filterByMonth(groupedData, reportMonth).reduce((sum, g) => sum + g.brutto, 0).toFixed(2)} kr
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Avgifter</p>
                <p className="text-2xl font-bold">
                  {filterByMonth(groupedData, reportMonth).reduce((sum, g) => sum + g.avgifter, 0).toFixed(2)} kr
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Netto</p>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {filterByMonth(groupedData, reportMonth).reduce((sum, g) => sum + g.netto, 0).toFixed(2)} kr
                </p>
              </div>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th>Utbetalingsdato</th>
                  <th>Fra</th>
                  <th>Til</th>
                  <th className="text-right">Brutto</th>
                  <th className="text-right">Avgifter</th>
                  <th className="text-right">Netto</th>
                  <th>Korttyper</th>
                </tr>
              </thead>
              <tbody>
                {filterByMonth(groupedData, reportMonth).map((group, index) => (
                  <tr key={index}>
                    <td>{new Date(group.payoutDate).toLocaleDateString('no-NO')}</td>
                    <td className="text-sm">{group.fromDate || '-'}</td>
                    <td className="text-sm">{group.toDate || '-'}</td>
                    <td className="text-right">{group.brutto.toFixed(2)} kr</td>
                    <td className="text-right">{group.avgifter.toFixed(2)} kr</td>
                    <td className="text-right font-semibold">{group.netto.toFixed(2)} kr</td>
                    <td>
                      <div className="flex flex-wrap gap-1">
                        {Object.entries(group.cardTypes).map(([type, amount]) => (
                          <span key={type} className="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs">
                            <CreditCard className="h-3 w-3" />
                            {type}: {amount.toFixed(2)}
                          </span>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="mt-6">
            <button
              onClick={handleGeneratePDF}
              disabled={groupedData.length === 0}
              className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Download className="h-4 w-4" />
              Generer PDF-rapport
            </button>
          </div>
        </div>
      )}

      {/* Previously Generated Reports */}
      <div className="card">
        <h2 className="text-2xl font-bold mb-6">Tidligere rapporter</h2>

        {reports.length === 0 ? (
          <p className="text-gray-500">Ingen rapporter ennå</p>
        ) : (
          <div className="space-y-4">
            {reports.map((report) => {
              const monthName = new Date(report.report_month + '-01').toLocaleDateString('no-NO', {
                month: 'long',
                year: 'numeric'
              });

              return (
                <div
                  key={report.id}
                  className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <FileText className="h-5 w-5 text-primary-600" />
                        <h3 className="font-semibold">
                          Oppgjørsrapport - {monthName}
                        </h3>
                      </div>
                      <div className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                        <p>
                          Opprettet: {new Date(report.created_at).toLocaleDateString('no-NO')}
                        </p>
                        <p>Firma: {report.account_info?.firmanavn || 'N/A'}</p>
                        <div className="grid grid-cols-3 gap-4 mt-2 p-3 bg-gray-50 dark:bg-gray-700 rounded">
                          <div>
                            <span className="font-medium">Brutto:</span>
                            <br />
                            {report.total_brutto?.toFixed(2) || '0.00'} kr
                          </div>
                          <div>
                            <span className="font-medium">Avgifter:</span>
                            <br />
                            {report.total_avgifter?.toFixed(2) || '0.00'} kr
                          </div>
                          <div>
                            <span className="font-medium">Netto:</span>
                            <br />
                            <span className="text-green-600 dark:text-green-400 font-semibold">
                              {report.total_netto?.toFixed(2) || '0.00'} kr
                            </span>
                          </div>
                        </div>
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
