import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Bell, User, LogOut } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { alertsAPI } from '../api';
import { ComplianceAlert } from '../types';

const Header: React.FC = () => {
  const [query, setQuery] = useState('');
  const [showNotifications, setShowNotifications] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [alerts, setAlerts] = useState<ComplianceAlert[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    // Navigate to regulations page with search query
    navigate(`/regulations?search=${encodeURIComponent(query)}`);
    setQuery('');
  };
  
  const toggleNotifications = async () => {
    if (!showNotifications && alerts.length === 0) {
      setIsLoading(true);
      try {
        const data = await alertsAPI.getUpcoming();
        setAlerts(data);
      } catch (error) {
        console.error('Error fetching alerts:', error);
      } finally {
        setIsLoading(false);
      }
    }
    
    setShowNotifications(!showNotifications);
    if (showUserMenu) setShowUserMenu(false);
  };
  
  const toggleUserMenu = () => {
    setShowUserMenu(!showUserMenu);
    if (showNotifications) setShowNotifications(false);
  };
  
  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  
  return (
    <header className="bg-white border-b border-neutral-lighter px-6 py-4">
      <div className="flex items-center justify-between">
        <form onSubmit={handleSearch} className="w-1/2">
          <div className="relative">
            <input
              type="text"
              placeholder="Search regulations in plain English..."
              className="input pl-10"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-light" size={18} />
          </div>
        </form>
        
        <div className="flex items-center space-x-4">
          <div className="relative">
            <button 
              className="p-2 rounded-full hover:bg-neutral-lighter relative"
              onClick={toggleNotifications}
            >
              <Bell size={20} className="text-neutral" />
              {alerts.length > 0 && (
                <span className="absolute top-0 right-0 h-4 w-4 bg-primary rounded-full text-white text-xs flex items-center justify-center">
                  {alerts.length}
                </span>
              )}
            </button>
            
            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg z-10 py-2">
                <div className="px-4 py-2 border-b border-neutral-lighter">
                  <h3 className="font-semibold">Compliance Alerts</h3>
                </div>
                <div className="max-h-96 overflow-y-auto">
                  {isLoading ? (
                    <div className="px-4 py-8 text-center text-neutral-light">
                      Loading alerts...
                    </div>
                  ) : alerts.length === 0 ? (
                    <div className="px-4 py-8 text-center text-neutral-light">
                      No alerts to display
                    </div>
                  ) : (
                    alerts.map((alert) => (
                      <div key={alert.id} className="px-4 py-3 hover:bg-background border-b border-neutral-lighter last:border-0">
                        <div className="flex items-start">
                          <div className="flex-1">
                            <p className="font-medium text-sm">{alert.title}</p>
                            <p className="text-xs text-neutral-light mt-1">{alert.description}</p>
                            <div className="flex items-center mt-2">
                              <span className={`badge ${
                                alert.priority === 'High' ? 'badge-high' : 
                                alert.priority === 'Medium' ? 'badge-medium' : 'badge-low'
                              }`}>
                                {alert.priority}
                              </span>
                              <span className="text-xs text-neutral-light ml-2">Due: {new Date(alert.due_date).toLocaleDateString()}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>
          
          <div className="relative">
            <button 
              className="flex items-center hover:bg-neutral-lighter rounded-full"
              onClick={toggleUserMenu}
            >
              <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-white">
                <User size={16} />
              </div>
              <span className="ml-2 font-medium">{user?.username || 'User'}</span>
            </button>
            
            {showUserMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg z-10 py-2">
                <div className="px-4 py-2 border-b border-neutral-lighter">
                  <p className="font-semibold">{user?.username || 'User'}</p>
                  <p className="text-xs text-neutral-light">{user?.email || 'user@example.com'}</p>
                </div>
                <button 
                  className="w-full px-4 py-2 text-left hover:bg-background flex items-center text-neutral-light"
                  onClick={handleLogout}
                >
                  <LogOut size={16} className="mr-2" />
                  <span>Sign Out</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;