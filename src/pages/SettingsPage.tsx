import React, { useState } from 'react';
import { Settings, Upload, Database, RefreshCw, Bell, Shield } from 'lucide-react';
import DocumentUpload from '../components/Settings/DocumentUpload';

const SettingsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'upload' | 'knowledge' | 'training' | 'notifications' | 'security' | 'general'>('upload');
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-2">
        <h1 className="text-2xl font-bold">Settings</h1>
      </div>
      
      <div className="flex border-b border-neutral-lighter mb-6">
        <button
          className={`px-4 py-2 font-medium ${
            activeTab === 'upload' 
              ? 'text-primary border-b-2 border-primary' 
              : 'text-neutral-light hover:text-neutral'
          }`}
          onClick={() => setActiveTab('upload')}
        >
          <div className="flex items-center">
            <Upload size={18} className="mr-2" />
            Upload Documents
          </div>
        </button>
        <button
          className={`px-4 py-2 font-medium ${
            activeTab === 'knowledge' 
              ? 'text-primary border-b-2 border-primary' 
              : 'text-neutral-light hover:text-neutral'
          }`}
          onClick={() => setActiveTab('knowledge')}
        >
          <div className="flex items-center">
            <Database size={18} className="mr-2" />
            Knowledge Base
          </div>
        </button>
        <button
          className={`px-4 py-2 font-medium ${
            activeTab === 'training' 
              ? 'text-primary border-b-2 border-primary' 
              : 'text-neutral-light hover:text-neutral'
          }`}
          onClick={() => setActiveTab('training')}
        >
          <div className="flex items-center">
            <RefreshCw size={18} className="mr-2" />
            Train AI Model
          </div>
        </button>
        <button
          className={`px-4 py-2 font-medium ${
            activeTab === 'notifications' 
              ? 'text-primary border-b-2 border-primary' 
              : 'text-neutral-light hover:text-neutral'
          }`}
          onClick={() => setActiveTab('notifications')}
        >
          <div className="flex items-center">
            <Bell size={18} className="mr-2" />
            Notifications
          </div>
        </button>
        <button
          className={`px-4 py-2 font-medium ${
            activeTab === 'security' 
              ? 'text-primary border-b-2 border-primary' 
              : 'text-neutral-light hover:text-neutral'
          }`}
          onClick={() => setActiveTab('security')}
        >
          <div className="flex items-center">
            <Shield size={18} className="mr-2" />
            Security
          </div>
        </button>
        <button
          className={`px-4 py-2 font-medium ${
            activeTab === 'general' 
              ? 'text-primary border-b-2 border-primary' 
              : 'text-neutral-light hover:text-neutral'
          }`}
          onClick={() => setActiveTab('general')}
        >
          <div className="flex items-center">
            <Settings size={18} className="mr-2" />
            General
          </div>
        </button>
      </div>
      
      {activeTab === 'upload' && (
        <DocumentUpload />
      )}
      
      {activeTab === 'knowledge' && (
        <div className="card">
          <div className="flex items-center mb-6">
            <div className="p-3 rounded-full bg-neutral-lighter mr-4">
              <Database size={20} className="text-neutral" />
            </div>
            <div>
              <h2 className="text-xl font-semibold">Knowledge Base Management</h2>
              <p className="text-sm text-neutral-light">
                Manage the regulatory knowledge base and update existing regulations
              </p>
            </div>
          </div>
          
          <div className="space-y-4">
            <div className="border border-neutral-lighter rounded-lg p-4">
              <h3 className="font-medium mb-2">Regulatory Database</h3>
              <p className="text-neutral-light mb-4">
                The knowledge base currently contains information about various regulatory frameworks across multiple jurisdictions.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div className="bg-neutral-lighter rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold">152</div>
                  <div className="text-sm text-neutral-light">Regulations</div>
                </div>
                <div className="bg-neutral-lighter rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold">28</div>
                  <div className="text-sm text-neutral-light">Jurisdictions</div>
                </div>
                <div className="bg-neutral-lighter rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold">45</div>
                  <div className="text-sm text-neutral-light">Agencies</div>
                </div>
              </div>
              <div className="flex justify-end">
                <button className="btn btn-primary">Manage Database</button>
              </div>
            </div>
            
            <div className="border border-neutral-lighter rounded-lg p-4">
              <h3 className="font-medium mb-2">Data Synchronization</h3>
              <p className="text-neutral-light mb-4">
                Synchronize the knowledge base with external regulatory databases to ensure up-to-date information.
              </p>
              <div className="flex justify-end">
                <button className="btn btn-outline mr-2">Schedule Sync</button>
                <button className="btn btn-primary">Sync Now</button>
              </div>
            </div>
            
            <div className="border border-neutral-lighter rounded-lg p-4">
              <h3 className="font-medium mb-2">Export Knowledge Base</h3>
              <p className="text-neutral-light mb-4">
                Export the entire knowledge base or specific sections for backup or analysis.
              </p>
              <div className="flex justify-end">
                <button className="btn btn-outline">Export Data</button>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {activeTab === 'training' && (
        <div className="card">
          <div className="flex items-center mb-6">
            <div className="p-3 rounded-full bg-neutral-lighter mr-4">
              <RefreshCw size={20} className="text-neutral" />
            </div>
            <div>
              <h2 className="text-xl font-semibold">AI Model Training</h2>
              <p className="text-sm text-neutral-light">
                Fine-tune the Llama 3.2 6B model with the latest regulatory data
              </p>
            </div>
          </div>
          
          <div className="space-y-4">
            <div className="border border-neutral-lighter rounded-lg p-4">
              <h3 className="font-medium mb-2">Model Status</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div className="bg-neutral-lighter rounded-lg p-4">
                  <div className="text-sm text-neutral-light">Current Model</div>
                  <div className="font-medium">Llama 3.2 6B</div>
                </div>
                <div className="bg-neutral-lighter rounded-lg p-4">
                  <div className="text-sm text-neutral-light">Last Trained</div>
                  <div className="font-medium">May 15, 2024</div>
                </div>
                <div className="bg-neutral-lighter rounded-lg p-4">
                  <div className="text-sm text-neutral-light">Performance Score</div>
                  <div className="font-medium text-green-600">92%</div>
                </div>
              </div>
            </div>
            
            <div className="border border-neutral-lighter rounded-lg p-4">
              <h3 className="font-medium mb-2">Training Configuration</h3>
              <div className="space-y-3 mb-4">
                <div className="flex items-center justify-between">
                  <span>Include new regulations</span>
                  <input type="checkbox" defaultChecked />
                </div>
                <div className="flex items-center justify-between">
                  <span>Include chat history</span>
                  <input type="checkbox" defaultChecked />
                </div>
                <div className="flex items-center justify-between">
                  <span>Training epochs</span>
                  <select className="input w-24 py-1">
                    <option>1</option>
                    <option>2</option>
                    <option selected>3</option>
                    <option>4</option>
                    <option>5</option>
                  </select>
                </div>
                <div className="flex items-center justify-between">
                  <span>Learning rate</span>
                  <select className="input w-24 py-1">
                    <option>0.00001</option>
                    <option selected>0.00005</option>
                    <option>0.0001</option>
                    <option>0.0005</option>
                  </select>
                </div>
              </div>
              <div className="flex justify-end">
                <button className="btn btn-outline mr-2">Schedule Training</button>
                <button className="btn btn-primary">Start Training</button>
              </div>
            </div>
            
            <div className="border border-neutral-lighter rounded-lg p-4">
              <h3 className="font-medium mb-2">Training History</h3>
              <table className="min-w-full divide-y divide-neutral-lighter">
                <thead>
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-neutral-light uppercase tracking-wider">Date</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-neutral-light uppercase tracking-wider">Duration</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-neutral-light uppercase tracking-wider">Data Size</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-neutral-light uppercase tracking-wider">Performance</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-lighter">
                  <tr>
                    <td className="px-4 py-2">May 15, 2024</td>
                    <td className="px-4 py-2">3h 42m</td>
                    <td className="px-4 py-2">2.4 GB</td>
                    <td className="px-4 py-2 text-green-600">92%</td>
                  </tr>
                  <tr>
                    <td className="px-4 py-2">April 10, 2024</td>
                    <td className="px-4 py-2">3h 15m</td>
                    <td className="px-4 py-2">2.1 GB</td>
                    <td className="px-4 py-2 text-green-600">89%</td>
                  </tr>
                  <tr>
                    <td className="px-4 py-2">March 5, 2024</td>
                    <td className="px-4 py-2">2h 58m</td>
                    <td className="px-4 py-2">1.9 GB</td>
                    <td className="px-4 py-2 text-green-600">87%</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
      
      {activeTab === 'notifications' && (
        <div className="card">
          <div className="flex items-center mb-6">
            <div className="p-3 rounded-full bg-neutral-lighter mr-4">
              <Bell size={20} className="text-neutral" />
            </div>
            <h2 className="text-lg font-semibold">Notification Settings</h2>
          </div>
          <p className="text-neutral-light mb-4">
            Configure how and when you receive regulatory update notifications.
          </p>
          <div className="space-y-6">
            <div>
              <h3 className="font-medium mb-3">Delivery Methods</h3>
              <div className="space-y-3">
                <label className="flex items-center justify-between">
                  <span>Email Notifications</span>
                  <input type="checkbox" defaultChecked />
                </label>
                <label className="flex items-center justify-between">
                  <span>Push Notifications</span>
                  <input type="checkbox" defaultChecked />
                </label>
                <label className="flex items-center justify-between">
                  <span>Daily Digest</span>
                  <input type="checkbox" />
                </label>
              </div>
            </div>
            
            <div>
              <h3 className="font-medium mb-3">Notification Types</h3>
              <div className="space-y-3">
                <label className="flex items-center justify-between">
                  <span>New Regulations</span>
                  <input type="checkbox" defaultChecked />
                </label>
                <label className="flex items-center justify-between">
                  <span>Regulatory Updates</span>
                  <input type="checkbox" defaultChecked />
                </label>
                <label className="flex items-center justify-between">
                  <span>Compliance Alerts</span>
                  <input type="checkbox" defaultChecked />
                </label>
                <label className="flex items-center justify-between">
                  <span>System Announcements</span>
                  <input type="checkbox" defaultChecked />
                </label>
              </div>
            </div>
            
            <div>
              <h3 className="font-medium mb-3">Frequency</h3>
              <div className="space-y-3">
                <label className="flex items-center justify-between">
                  <span>Alert Frequency</span>
                  <select className="input w-40 py-1">
                    <option>Real-time</option>
                    <option>Hourly</option>
                    <option>Daily</option>
                    <option>Weekly</option>
                  </select>
                </label>
                <label className="flex items-center justify-between">
                  <span>Quiet Hours</span>
                  <div className="flex items-center space-x-2">
                    <select className="input w-24 py-1">
                      <option>10:00 PM</option>
                      <option>11:00 PM</option>
                      <option>12:00 AM</option>
                    </select>
                    <span>to</span>
                    <select className="input w-24 py-1">
                      <option>6:00 AM</option>
                      <option>7:00 AM</option>
                      <option>8:00 AM</option>
                    </select>
                  </div>
                </label>
              </div>
            </div>
          </div>
          
          <div className="mt-6 pt-6 border-t border-neutral-lighter flex justify-end">
            <button className="btn btn-outline mr-2">Reset to Default</button>
            <button className="btn btn-primary">Save Changes</button>
          </div>
        </div>
      )}
      
      {activeTab === 'security' && (
        <div className="card">
          <div className="flex items-center mb-6">
            <div className="p-3 rounded-full bg-neutral-lighter mr-4">
              <Shield size={20} className="text-neutral" />
            </div>
            <h2 className="text-lg font-semibold">Security Settings</h2>
          </div>
          <p className="text-neutral-light mb-4">
            Manage access controls and security settings for the platform.
          </p>
          <div className="space-y-6">
            <div>
              <h3 className="font-medium mb-3">Authentication</h3>
              <div className="space-y-3">
                <label className="flex items-center justify-between">
                  <span>Two-Factor Authentication</span>
                  <input type="checkbox" defaultChecked />
                </label>
                <label className="flex items-center justify-between">
                  <span>Remember Device (Days)</span>
                  <select className="input w-24 py-1">
                    <option>7</option>
                    <option>14</option>
                    <option>30</option>
                    <option>Never</option>
                  </select>
                </label>
                <label className="flex items-center justify-between">
                  <span>Password Expiry (Days)</span>
                  <select className="input w-24 py-1">
                    <option>30</option>
                    <option>60</option>
                    <option>90</option>
                    <option>Never</option>
                  </select>
                </label>
              </div>
            </div>
            
            <div>
              <h3 className="font-medium mb-3">Session Management</h3>
              <div className="space-y-3">
                <label className="flex items-center justify-between">
                  <span>Session Timeout (Minutes)</span>
                  <select className="input w-24 py-1">
                    <option>15</option>
                    <option>30</option>
                    <option>60</option>
                  </select>
                </label>
                <label className="flex items-center justify-between">
                  <span>Concurrent Sessions</span>
                  <select className="input w-24 py-1">
                    <option>1</option>
                    <option>2</option>
                    <option>3</option>
                    <option>Unlimited</option>
                  </select>
                </label>
              </div>
            </div>
            
            <div>
              <h3 className="font-medium mb-3">API Access</h3>
              <div className="space-y-3">
                <label className="flex items-center justify-between">
                  <span>Enable API Access</span>
                  <input type="checkbox" />
                </label>
                <label className="flex items-center justify-between">
                  <span>API Key Expiry (Days)</span>
                  <select className="input w-24 py-1" disabled>
                    <option>30</option>
                    <option>60</option>
                    <option>90</option>
                    <option>Never</option>
                  </select>
                </label>
                <label className="flex items-center justify-between">
                  <span>Rate Limiting (Requests/Min)</span>
                  <select className="input w-24 py-1" disabled>
                    <option>60</option>
                    <option>120</option>
                    <option>300</option>
                    <option>Unlimited</option>
                  </select>
                </label>
              </div>
            </div>
          </div>
          
          <div className="mt-6 pt-6 border-t border-neutral-lighter flex justify-end">
            <button className="btn btn-outline mr-2">Reset to Default</button>
            <button className="btn btn-primary">Save Changes</button>
          </div>
        </div>
      )}
      
      {activeTab === 'general' && (
        <div className="card">
          <div className="flex items-center mb-6">
            <div className="p-3 rounded-full bg-neutral-lighter mr-4">
              <Settings size={20} className="text-neutral" />
            </div>
            <h2 className="text-lg font-semibold">General Settings</h2>
          </div>
          <p className="text-neutral-light mb-4">
            Configure general platform settings and preferences.
          </p>
          <div className="space-y-6">
            <div>
              <h3 className="font-medium mb-3">Appearance</h3>
              <div className="space-y-3">
                <label className="flex items-center justify-between">
                  <span>Dark Mode</span>
                  <input type="checkbox" />
                </label>
                <label className="flex items-center justify-between">
                  <span>Compact View</span>
                  <input type="checkbox" />
                </label>
                <label className="flex items-center justify-between">
                  <span>Font Size</span>
                  <select className="input w-24 py-1">
                    <option>Small</option>
                    <option selected>Medium</option>
                    <option>Large</option>
                  </select>
                </label>
              </div>
            </div>
            
            <div>
              <h3 className="font-medium mb-3">Language & Region</h3>
              <div className="space-y-3">
                <label className="flex items-center justify-between">
                  <span>Language</span>
                  <select className="input w-40 py-1">
                    <option>English</option>
                    <option>Spanish</option>
                    <option>French</option>
                    <option>German</option>
                    <option>Japanese</option>
                  </select>
                </label>
                <label className="flex items-center justify-between">
                  <span>Date Format</span>
                  <select className="input w-40 py-1">
                    <option>MM/DD/YYYY</option>
                    <option>DD/MM/YYYY</option>
                    <option>YYYY-MM-DD</option>
                  </select>
                </label>
                <label className="flex items-center justify-between">
                  <span>Time Format</span>
                  <select className="input w-40 py-1">
                    <option>12-hour (AM/PM)</option>
                    <option>24-hour</option>
                  </select>
                </label>
              </div>
            </div>
            
            <div>
              <h3 className="font-medium mb-3">Data & Performance</h3>
              <div className="space-y-3">
                <label className="flex items-center justify-between">
                  <span>Auto-refresh Data</span>
                  <input type="checkbox" defaultChecked />
                </label>
                <label className="flex items-center justify-between">
                  <span>Refresh Interval (Minutes)</span>
                  <select className="input w-24 py-1">
                    <option>5</option>
                    <option>10</option>
                    <option>15</option>
                    <option>30</option>
                  </select>
                </label>
                <label className="flex items-center justify-between">
                  <span>Cache Size</span>
                  <select className="input w-24 py-1">
                    <option>Small</option>
                    <option selected>Medium</option>
                    <option>Large</option>
                  </select>
                </label>
              </div>
            </div>
          </div>
          
          <div className="mt-6 pt-6 border-t border-neutral-lighter flex justify-end">
            <button className="btn btn-outline mr-2">Reset to Default</button>
            <button className="btn btn-primary">Save Changes</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SettingsPage;