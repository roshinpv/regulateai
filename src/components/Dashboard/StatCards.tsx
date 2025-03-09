import React, { useState, useEffect } from 'react';
import { AlertTriangle, BookOpen, Clock, BarChart3 } from 'lucide-react';
import { dashboardAPI } from '../../api';

interface DashboardStats {
  pendingAlerts: number;
  highPriorityAlerts: number;
  activeRegulations: number;
  newRegulations: number;
  recentUpdates: number;
  complianceScore: number;
  complianceScoreChange: number;
}

const StatCards: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await dashboardAPI.getStats();
        setStats(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching dashboard stats:', err);
        setError('Failed to load dashboard statistics');
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="card">
            <div className="animate-pulse flex items-start">
              <div className="rounded-full bg-neutral-lighter h-12 w-12 mr-4"></div>
              <div className="flex-1">
                <div className="h-4 bg-neutral-lighter rounded w-3/4 mb-2"></div>
                <div className="h-6 bg-neutral-lighter rounded w-1/4 mb-2"></div>
                <div className="h-3 bg-neutral-lighter rounded w-1/2"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="card p-6 text-red-500 text-center">
        {error || 'Failed to load dashboard statistics'}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div className="card">
        <div className="flex items-start">
          <div className="p-3 rounded-full bg-primary/10 mr-4">
            <AlertTriangle size={20} className="text-primary" />
          </div>
          <div>
            <p className="text-neutral-light text-sm">Pending Alerts</p>
            <h3 className="text-2xl font-bold mt-1">{stats.pendingAlerts}</h3>
            <p className="text-xs text-primary mt-1">{stats.highPriorityAlerts} high priority</p>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="flex items-start">
          <div className="p-3 rounded-full bg-secondary/20 mr-4">
            <BookOpen size={20} className="text-secondary-dark" />
          </div>
          <div>
            <p className="text-neutral-light text-sm">Active Regulations</p>
            <h3 className="text-2xl font-bold mt-1">{stats.activeRegulations}</h3>
            <p className="text-xs text-neutral-light mt-1">+{stats.newRegulations} from last month</p>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="flex items-start">
          <div className="p-3 rounded-full bg-neutral-lighter mr-4">
            <Clock size={20} className="text-neutral" />
          </div>
          <div>
            <p className="text-neutral-light text-sm">Recent Updates</p>
            <h3 className="text-2xl font-bold mt-1">{stats.recentUpdates}</h3>
            <p className="text-xs text-neutral-light mt-1">Last 30 days</p>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="flex items-start">
          <div className="p-3 rounded-full bg-primary/10 mr-4">
            <BarChart3 size={20} className="text-primary" />
          </div>
          <div>
            <p className="text-neutral-light text-sm">Compliance Score</p>
            <h3 className="text-2xl font-bold mt-1">{stats.complianceScore}%</h3>
            <p className={`text-xs ${stats.complianceScoreChange >= 0 ? 'text-green-600' : 'text-red-600'} mt-1`}>
              {stats.complianceScoreChange >= 0 ? '↑' : '↓'} {Math.abs(stats.complianceScoreChange)}% from last quarter
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatCards;