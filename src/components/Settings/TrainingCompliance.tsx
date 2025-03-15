import React, { useState } from 'react';
import { Upload, FileSpreadsheet, Mail, AlertCircle, Check, X, Download } from 'lucide-react';
import Papa from 'papaparse';
import * as XLSX from 'xlsx';

interface EmployeeTraining {
  employeeName: string;
  employeeEmail: string;
  managerName: string;
  managerEmail: string;
  trainingName: string;
  dueDate: string;
  status: string;
}

const TrainingCompliance: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [parsedData, setParsedData] = useState<EmployeeTraining[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setFile(file);
    setError(null);
    setSuccessMessage(null);
    setIsLoading(true);

    const fileExtension = file.name.split('.').pop()?.toLowerCase();

    if (fileExtension === 'csv') {
      Papa.parse(file, {
        complete: (results) => {
          processFileData(results.data);
        },
        header: true,
        skipEmptyLines: true,
        error: (error) => {
          setError(`Error parsing CSV file: ${error}`);
          setIsLoading(false);
        }
      });
    } else if (fileExtension === 'xlsx' || fileExtension === 'xls') {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const data = e.target?.result;
          const workbook = XLSX.read(data, { type: 'binary' });
          const sheetName = workbook.SheetNames[0];
          const worksheet = workbook.Sheets[sheetName];
          const jsonData = XLSX.utils.sheet_to_json(worksheet);
          processFileData(jsonData);
        } catch (error) {
          setError(`Error parsing Excel file: ${error}`);
          setIsLoading(false);
        }
      };
      reader.onerror = () => {
        setError('Error reading file');
        setIsLoading(false);
      };
      reader.readAsBinaryString(file);
    } else {
      setError('Unsupported file format. Please upload a CSV or Excel file.');
      setIsLoading(false);
    }
  };

  const processFileData = (data: any[]) => {
    try {
      const processedData = data.map((row: any) => ({
        employeeName: row.employeeName || row['Employee Name'] || '',
        employeeEmail: row.employeeEmail || row['Employee Email'] || '',
        managerName: row.managerName || row['Manager Name'] || '',
        managerEmail: row.managerEmail || row['Manager Email'] || '',
        trainingName: row.trainingName || row['Training Name'] || '',
        dueDate: row.dueDate || row['Due Date'] || '',
        status: row.status || row['Status'] || 'Pending'
      }));

      // Validate data
      const invalidRows = processedData.filter(row => 
        !row.employeeName || 
        !row.employeeEmail || 
        !row.managerName || 
        !row.managerEmail ||
        !row.trainingName ||
        !row.dueDate
      );

      if (invalidRows.length > 0) {
        setError(`Found ${invalidRows.length} invalid rows. Please ensure all required fields are filled.`);
        return;
      }

      setParsedData(processedData);
      setSuccessMessage(`Successfully processed ${processedData.length} records`);
    } catch (error) {
      setError(`Error processing file data: ${error}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendEmails = async () => {
    setIsSending(true);
    setError(null);
    setSuccessMessage(null);

    try {
      // Group employees by manager
      const managerGroups = parsedData.reduce((groups: Record<string, EmployeeTraining[]>, employee) => {
        const key = employee.managerEmail;
        if (!groups[key]) {
          groups[key] = [];
        }
        groups[key].push(employee);
        return groups;
      }, {});

      // Send emails to each manager
      const response = await fetch('/api/training/send-notifications', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ managerGroups }),
      });

      if (!response.ok) {
        throw new Error('Failed to send notifications');
      }

      setSuccessMessage('Successfully sent notifications to all managers');
    } catch (error) {
      setError(`Error sending notifications: ${error}`);
    } finally {
      setIsSending(false);
    }
  };

  const downloadTemplate = () => {
    const template = [
      {
        'Employee Name': 'John Doe',
        'Employee Email': 'john.doe@example.com',
        'Manager Name': 'Jane Smith',
        'Manager Email': 'jane.smith@example.com',
        'Training Name': 'Compliance Training 2024',
        'Due Date': '2024-06-30',
        'Status': 'Pending'
      }
    ];

    const worksheet = XLSX.utils.json_to_sheet(template);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Template');
    XLSX.writeFile(workbook, 'training_compliance_template.xlsx');
  };

  return (
    <div className="card">
      <div className="flex items-center mb-6">
        <div className="p-3 rounded-full bg-neutral-lighter mr-4">
          <FileSpreadsheet size={20} className="text-neutral" />
        </div>
        <div>
          <h2 className="text-xl font-semibold">Training Compliance Management</h2>
          <p className="text-sm text-neutral-light">
            Upload employee training data and send notifications to managers
          </p>
        </div>
      </div>

      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-medium">Upload Training Data</h3>
          <button 
            className="btn btn-outline text-sm flex items-center"
            onClick={downloadTemplate}
          >
            <Download size={16} className="mr-2" />
            Download Template
          </button>
        </div>

        <div 
          className="border-2 border-dashed border-neutral-lighter rounded-lg p-8 text-center"
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault();
            const droppedFile = e.dataTransfer.files[0];
            if (droppedFile) {
              const input = document.createElement('input');
              input.type = 'file';
              input.files = e.dataTransfer.files;
              handleFileUpload({ target: input } as any);
            }
          }}
        >
          <input
            type="file"
            id="file-upload"
            className="hidden"
            accept=".csv,.xlsx,.xls"
            onChange={handleFileUpload}
          />
          <Upload size={48} className="mx-auto text-neutral-light mb-4" />
          <p className="text-neutral mb-2">
            {file ? file.name : 'Drag and drop your file here'}
          </p>
          <p className="text-neutral-light text-sm mb-4">
            Supported formats: CSV, Excel (XLSX, XLS)
          </p>
          <button 
            className="btn btn-primary"
            onClick={() => document.getElementById('file-upload')?.click()}
            disabled={isLoading}
          >
            {isLoading ? 'Processing...' : 'Browse Files'}
          </button>
        </div>

        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start">
            <AlertCircle size={20} className="text-red-500 mr-2 flex-shrink-0 mt-0.5" />
            <p className="text-red-600 text-sm">{error}</p>
          </div>
        )}

        {successMessage && (
          <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg flex items-start">
            <Check size={20} className="text-green-500 mr-2 flex-shrink-0 mt-0.5" />
            <p className="text-green-600 text-sm">{successMessage}</p>
          </div>
        )}
      </div>

      {parsedData.length > 0 && (
        <>
          <div className="mb-6">
            <h3 className="font-medium mb-4">Preview Data</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-neutral-lighter">
                <thead>
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-neutral-light uppercase tracking-wider">Employee</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-neutral-light uppercase tracking-wider">Manager</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-neutral-light uppercase tracking-wider">Training</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-neutral-light uppercase tracking-wider">Due Date</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-neutral-light uppercase tracking-wider">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-lighter">
                  {parsedData.slice(0, 5).map((row, index) => (
                    <tr key={index}>
                      <td className="px-4 py-2">
                        <div className="font-medium">{row.employeeName}</div>
                        <div className="text-sm text-neutral-light">{row.employeeEmail}</div>
                      </td>
                      <td className="px-4 py-2">
                        <div className="font-medium">{row.managerName}</div>
                        <div className="text-sm text-neutral-light">{row.managerEmail}</div>
                      </td>
                      <td className="px-4 py-2">{row.trainingName}</td>
                      <td className="px-4 py-2">{row.dueDate}</td>
                      <td className="px-4 py-2">
                        <span className={`badge ${
                          row.status.toLowerCase() === 'completed' ? 'badge-high' :
                          row.status.toLowerCase() === 'in progress' ? 'badge-medium' :
                          'badge-low'
                        }`}>
                          {row.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {parsedData.length > 5 && (
                <p className="text-sm text-neutral-light mt-2 text-center">
                  Showing 5 of {parsedData.length} records
                </p>
              )}
            </div>
          </div>

          <div className="flex items-center justify-between pt-6 border-t border-neutral-lighter">
            <div className="text-sm text-neutral-light">
              {parsedData.length} records ready to process
            </div>
            <div className="flex space-x-3">
              <button 
                className="btn btn-outline"
                onClick={() => {
                  setFile(null);
                  setParsedData([]);
                  setError(null);
                  setSuccessMessage(null);
                }}
                disabled={isSending}
              >
                Clear Data
              </button>
              <button 
                className="btn btn-primary flex items-center"
                onClick={handleSendEmails}
                disabled={isSending || parsedData.length === 0}
              >
                <Mail size={16} className="mr-2" />
                {isSending ? 'Sending...' : 'Send Notifications'}
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default TrainingCompliance;