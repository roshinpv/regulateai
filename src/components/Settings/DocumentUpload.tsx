import React, { useState, useEffect, useRef } from 'react';
import { Upload, Link, FileText, X, Check, AlertCircle } from 'lucide-react';
import { documentsAPI, jurisdictionsAPI, regulationsAPI } from '../../api';
import { Jurisdiction, Regulation } from '../../types';
import { useAuth } from '../../context/AuthContext';

interface UploadedDocument {
  id: string;
  name: string;
  size?: string;
  source: 'file' | 'url';
  url?: string;
  status: 'uploading' | 'success' | 'error' | 'processing';
  progress?: number;
  error?: string;
  regulation_id?: string;
  jurisdiction_id?: string;
}

const DocumentUpload: React.FC = () => {
  const [uploadMethod, setUploadMethod] = useState<'file' | 'url'>('file');
  const [url, setUrl] = useState('');
  const [documents, setDocuments] = useState<UploadedDocument[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [selectedRegulation, setSelectedRegulation] = useState<string>('');
  const [selectedJurisdiction, setSelectedJurisdiction] = useState<string>('');
  const [regulations, setRegulations] = useState<Regulation[]>([]);
  const [jurisdictions, setJurisdictions] = useState<Jurisdiction[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { user } = useAuth();

  useEffect(() => {
    // Fetch regulations and jurisdictions
    const fetchData = async () => {
      try {
        const regsData = await regulationsAPI.getAll();
        setRegulations(regsData);
        
        const jurisData = await jurisdictionsAPI.getAll();
        setJurisdictions(jurisData);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };
    
    fetchData();
  }, []);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setIsUploading(true);
      
      for (const file of Array.from(e.target.files)) {
        const newDoc: UploadedDocument = {
          id: `file-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          name: file.name,
          size: formatFileSize(file.size),
          source: 'file',
          status: 'uploading',
          progress: 0,
          regulation_id: selectedRegulation || undefined,
          jurisdiction_id: selectedJurisdiction || undefined
        };
        
        setDocuments(prev => [...prev, newDoc]);
        
        try {
          // Create form data
          const formData = new FormData();
          formData.append('file', file);
          formData.append('title', title || file.name);
          formData.append('description', description || '');
          
          if (selectedRegulation) {
            formData.append('regulation_id', selectedRegulation);
          }
          
          if (selectedJurisdiction) {
            formData.append('jurisdiction_id', selectedJurisdiction);
          }
          
          // Upload file
          const response = await documentsAPI.uploadFile(formData);
          
          // Update document status
          setDocuments(prev => 
            prev.map(doc => 
              doc.id === newDoc.id 
                ? { ...doc, id: response.id, status: 'success' } 
                : doc
            )
          );
        } catch (error) {
          console.error('Error uploading file:', error);
          
          // Update document status to error
          setDocuments(prev => 
            prev.map(doc => 
              doc.id === newDoc.id 
                ? { ...doc, status: 'error', error: 'Upload failed' } 
                : doc
            )
          );
        }
      }
      
      setIsUploading(false);
      
      // Clear file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleUrlSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!url.trim() || !title.trim()) return;
    
    const newDocument: UploadedDocument = {
      id: `url-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name: title || getFileNameFromUrl(url),
      source: 'url',
      url: url,
      status: 'uploading',
      progress: 0,
      regulation_id: selectedRegulation || undefined,
      jurisdiction_id: selectedJurisdiction || undefined
    };
    
    setDocuments(prev => [...prev, newDocument]);
    setIsUploading(true);
    
    try {
      // Upload URL
      const response = await documentsAPI.uploadUrl({
        title: title,
        description: description || '',
        url: url,
        content_type: guessContentType(url),
        regulation_id: selectedRegulation || undefined,
        jurisdiction_id: selectedJurisdiction || undefined
      });
      
      // Update document status
      setDocuments(prev => 
        prev.map(doc => 
          doc.id === newDocument.id 
            ? { ...doc, id: response.id, status: 'success' } 
            : doc
        )
      );
      
      // Clear form
      setUrl('');
      
    } catch (error) {
      console.error('Error uploading URL:', error);
      
      // Update document status to error
      setDocuments(prev => 
        prev.map(doc => 
          doc.id === newDocument.id 
            ? { ...doc, status: 'error', error: 'Upload failed' } 
            : doc
        )
      );
    } finally {
      setIsUploading(false);
    }
  };

  const guessContentType = (url: string): string => {
    const extension = url.split('.').pop()?.toLowerCase();
    
    switch (extension) {
      case 'pdf':
        return 'application/pdf';
      case 'doc':
        return 'application/msword';
      case 'docx':
        return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
      case 'txt':
        return 'text/plain';
      case 'html':
      case 'htm':
        return 'text/html';
      default:
        return 'application/octet-stream';
    }
  };

  const handleRemoveDocument = async (id: string) => {
    // If document is already uploaded to server (has a UUID format id)
    if (id.match(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/)) {
      try {
        await documentsAPI.delete(id);
      } catch (error) {
        console.error('Error deleting document:', error);
      }
    }
    
    setDocuments(prev => prev.filter(doc => doc.id !== id));
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' bytes';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const getFileNameFromUrl = (url: string): string => {
    try {
      const urlObj = new URL(url);
      const pathname = urlObj.pathname;
      const filename = pathname.split('/').pop() || 'document';
      return filename;
    } catch (e) {
      return 'document';
    }
  };

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  const handleProcessDocuments = async () => {
    if (documents.length === 0) return;
    
    setIsProcessing(true);
    
    // Get IDs of documents with status 'success'
    const documentIds = documents
      .filter(doc => doc.status === 'success')
      .map(doc => doc.id);
    
    if (documentIds.length === 0) {
      setIsProcessing(false);
      return;
    }
    
    // Update all documents to processing status
    setDocuments(prev => 
      prev.map(doc => 
        documentIds.includes(doc.id)
          ? { ...doc, status: 'processing' }
          : doc
      )
    );
    
    try {
      // Process documents
      await documentsAPI.processBatch(documentIds);
      
      // Update all processed documents to success status
      setDocuments(prev => 
        prev.map(doc => 
          documentIds.includes(doc.id)
            ? { ...doc, status: 'success' }
            : doc
        )
      );
      
      // Show success message
      alert('Documents processed successfully!');
    } catch (error) {
      console.error('Error processing documents:', error);
      
      // Update all processed documents to error status
      setDocuments(prev => 
        prev.map(doc => 
          documentIds.includes(doc.id) && doc.status === 'processing'
            ? { ...doc, status: 'error', error: 'Processing failed' }
            : doc
        )
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      // Create a new event with the dropped files
      const event = {
        target: {
          files: e.dataTransfer.files
        }
      } as unknown as React.ChangeEvent<HTMLInputElement>;
      
      // Call the file change handler
      handleFileChange(event);
    }
  };

  return (
    <div className="card">
      <div className="flex items-center mb-6">
        <div className="p-3 rounded-full bg-neutral-lighter mr-4">
          <Upload size={20} className="text-neutral" />
        </div>
        <div>
          <h2 className="text-xl font-semibold">Upload Regulatory Documents</h2>
          <p className="text-sm text-neutral-light">
            Upload new regulatory documents to be processed and added to the knowledge base
          </p>
        </div>
      </div>
      
      <div className="mb-6">
        <div className="flex border-b border-neutral-lighter">
          <button
            className={`px-4 py-2 font-medium ${
              uploadMethod === 'file' 
                ? 'text-primary border-b-2 border-primary' 
                : 'text-neutral-light hover:text-neutral'
            }`}
            onClick={() => setUploadMethod('file')}
          >
            <div className="flex items-center">
              <FileText size={18} className="mr-2" />
              Upload Files
            </div>
          </button>
          <button
            className={`px-4 py-2 font-medium ${
              uploadMethod === 'url' 
                ? 'text-primary border-b-2 border-primary' 
                : 'text-neutral-light hover:text-neutral'
            }`}
            onClick={() => setUploadMethod('url')}
          >
            <div className="flex items-center">
              <Link size={18} className="mr-2" />
              URL Import
            </div>
          </button>
        </div>
      </div>
      
      <div className="mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label htmlFor="document-title" className="block text-sm font-medium text-neutral mb-1">
              Document Title
            </label>
            <input
              id="document-title"
              type="text"
              className="input"
              placeholder="Enter document title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>
          <div>
            <label htmlFor="document-description" className="block text-sm font-medium text-neutral mb-1">
              Description (Optional)
            </label>
            <input
              id="document-description"
              type="text"
              className="input"
              placeholder="Enter a brief description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="regulation" className="block text-sm font-medium text-neutral mb-1">
              Related Regulation (Optional)
            </label>
            <select
              id="regulation"
              className="input"
              value={selectedRegulation}
              onChange={(e) => setSelectedRegulation(e.target.value)}
            >
              <option value="">-- Select Regulation --</option>
              {regulations.map(reg => (
                <option key={reg.id} value={reg.id}>{reg.title}</option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="jurisdiction" className="block text-sm font-medium text-neutral mb-1">
              Jurisdiction (Optional)
            </label>
            <select
              id="jurisdiction"
              className="input"
              value={selectedJurisdiction}
              onChange={(e) => setSelectedJurisdiction(e.target.value)}
            >
              <option value="">-- Select Jurisdiction --</option>
              {jurisdictions.map(jur => (
                <option key={jur.id} value={jur.id}>{jur.name}</option>
              ))}
            </select>
          </div>
        </div>
      </div>
      
      {uploadMethod === 'file' ? (
        <div 
          className="border-2 border-dashed border-neutral-lighter rounded-lg p-8 text-center"
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          <input
            type="file"
            multiple
            className="hidden"
            onChange={handleFileChange}
            ref={fileInputRef}
            accept=".pdf,.doc,.docx,.txt,.rtf"
          />
          <FileText size={48} className="mx-auto text-neutral-light mb-4" />
          <p className="text-neutral mb-2">Drag and drop your files here</p>
          <p className="text-neutral-light text-sm mb-4">
            Supported formats: PDF, DOC, DOCX, TXT, RTF
          </p>
          <button 
            className="btn btn-primary"
            onClick={handleBrowseClick}
            disabled={isUploading}
          >
            {isUploading ? 'Uploading...' : 'Browse Files'}
          </button>
        </div>
      ) : (
        <form onSubmit={handleUrlSubmit} className="mb-6">
          <div className="mb-4">
            <label htmlFor="document-url" className="block text-sm font-medium text-neutral mb-1">
              Document URL
            </label>
            <div className="flex">
              <input
                id="document-url"
                type="url"
                className="input flex-1 rounded-r-none"
                placeholder="https://example.com/document.pdf"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                required
              />
              <button 
                type="submit" 
                className="btn btn-primary rounded-l-none"
                disabled={!url.trim() || !title.trim() || isUploading}
              >
                {isUploading ? 'Importing...' : 'Import'}
              </button>
            </div>
            <p className="text-xs text-neutral-light mt-1">
              Enter the URL of a regulatory document to import
            </p>
          </div>
        </form>
      )}
      
      {documents.length > 0 && (
        <div className="mt-6">
          <h3 className="font-medium mb-3">Uploaded Documents</h3>
          <div className="space-y-3">
            {documents.map((doc) => (
              <div key={doc.id} className="border border-neutral-lighter rounded-md p-3">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center">
                    <FileText size={16} className="text-neutral-light mr-2" />
                    <span className="font-medium">{doc.name}</span>
                    {doc.size && (
                      <span className="text-xs text-neutral-light ml-2">
                        {doc.size}
                      </span>
                    )}
                    {doc.source === 'url' && (
                      <span className="text-xs bg-neutral-lighter text-neutral-light px-2 py-0.5 rounded ml-2">
                        URL
                      </span>
                    )}
                  </div>
                  <button 
                    className="text-neutral-light hover:text-neutral"
                    onClick={() => handleRemoveDocument(doc.id)}
                    disabled={doc.status === 'processing'}
                  >
                    <X size={16} />
                  </button>
                </div>
                
                {doc.status === 'uploading' && (
                  <div>
                    <div className="w-full bg-neutral-lighter rounded-full h-2 mb-1">
                      <div 
                        className="bg-primary h-2 rounded-full" 
                        style={{ width: `${doc.progress || 50}%` }}
                      ></div>
                    </div>
                    <div className="text-xs text-neutral-light">
                      Uploading...
                    </div>
                  </div>
                )}
                
                {doc.status === 'processing' && (
                  <div className="flex items-center text-primary text-sm">
                    <div className="animate-spin mr-1">
                      <Upload size={16} />
                    </div>
                    <span>Processing document...</span>
                  </div>
                )}
                
                {doc.status === 'success' && (
                  <div className="flex items-center text-green-600 text-sm">
                    <Check size={16} className="mr-1" />
                    <span>Ready</span>
                  </div>
                )}
                
                {doc.status === 'error' && (
                  <div className="flex items-center text-red-600 text-sm">
                    <AlertCircle size={16} className="mr-1" />
                    <span>{doc.error || 'Upload failed'}</span>
                  </div>
                )}
                
                {doc.source === 'url' && doc.url && (
                  <div className="mt-1 text-xs text-neutral-light truncate">
                    <span className="font-medium">Source:</span> {doc.url}
                  </div>
                )}
                
                {(doc.regulation_id || doc.jurisdiction_id) && (
                  <div className="mt-1 flex flex-wrap gap-2">
                    {doc.regulation_id && (
                      <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded">
                        {regulations.find(r => r.id === doc.regulation_id)?.title || 'Regulation'}
                      </span>
                    )}
                    {doc.jurisdiction_id && (
                      <span className="text-xs bg-secondary/20 text-neutral-dark px-2 py-0.5 rounded">
                        {jurisdictions.find(j => j.id === doc.jurisdiction_id)?.name || 'Jurisdiction'}
                      </span>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
      
      <div className="mt-6 pt-6 border-t border-neutral-lighter flex justify-between">
        <div className="text-sm text-neutral-light">
          {documents.length > 0 ? (
            <span>{documents.length} document{documents.length !== 1 ? 's' : ''} ready to process</span>
          ) : (
            <span>No documents uploaded yet</span>
          )}
        </div>
        <div className="flex space-x-3">
          <button 
            className="btn btn-outline"
            onClick={() => {
              setDocuments([]);
              setTitle('');
              setDescription('');
              setUrl('');
              setSelectedRegulation('');
              setSelectedJurisdiction('');
            }}
            disabled={documents.length === 0 || isProcessing}
          >
            Clear All
          </button>
          <button 
            className="btn btn-primary"
            onClick={handleProcessDocuments}
            disabled={documents.length === 0 || isUploading || isProcessing || !documents.some(doc => doc.status === 'success')}
          >
            {isProcessing ? 'Processing...' : 'Process Documents'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default DocumentUpload;