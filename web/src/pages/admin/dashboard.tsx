import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';

interface DashboardStats {
  totalPolicies: number;
  totalScrapers: number;
  activeScrapers: number;
  lastUpdate: string;
}

const AdminDashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const [stats, setStats] = useState<DashboardStats>({
    totalPolicies: 0,
    totalScrapers: 3,
    activeScrapers: 2,
    lastUpdate: new Date().toISOString()
  });
  const [unified, setUnified] = useState<any>(null);
  const [system, setSystem] = useState<any>(null);
  const [scrapers, setScrapers] = useState<any>(null);
  const [database, setDatabase] = useState<any>(null);

  useEffect(() => {
    fetchDashboardStats();
    fetch('/api/v1/admin/status/unified').then(r=>r.json()).then(setUnified).catch(()=>{});
    fetch('/api/v1/dashboard/system').then(r=>r.json()).then(setSystem).catch(()=>{});
    fetch('/api/v1/dashboard/scrapers').then(r=>r.json()).then(setScrapers).catch(()=>{});
    fetch('/api/v1/dashboard/database').then(r=>r.json()).then(setDatabase).catch(()=>{});
  }, []);

  const fetchDashboardStats = async () => {
    try {
      const response = await fetch('/api/v1/admin/dashboard');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Failed to fetch dashboard stats:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">
                Admin Dashboard
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                Welcome, {user?.username}
              </span>
              <button
                onClick={logout}
                className="text-sm text-red-600 hover:text-red-800"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {/* Stats Cards */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Total Policies
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {stats.totalPolicies}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Active Scrapers
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {stats.activeScrapers}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Last Update
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {new Date(stats.lastUpdate).toLocaleDateString()}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        System Status
                      </dt>
                      <dd className="text-lg font-medium text-green-600">
                        Healthy
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Scraper Service and Links */}
          <div className="mt-8 grid grid-cols-1 gap-4 lg:grid-cols-2">
            <div className="bg-white p-4 rounded shadow">
              <h2 className="font-semibold mb-2">Scraper Service</h2>
              <div>Enabled: {unified?.scraper_service?.enabled ? 'true' : 'false'}</div>
              <div className="mt-2">
                <h3 className="font-medium">Endpoints</h3>
                <ul className="list-disc list-inside text-sm text-blue-700">
                  {unified?.links?.scrapers?.map((p:string)=>(<li key={p}><a href={p}>{p}</a></li>))}
                </ul>
              </div>
              {scrapers && (
                <div className="mt-2 text-sm">
                  <div>Total scrapers: {scrapers.total_scrapers}</div>
                  <div>Active: {scrapers.active_scrapers}</div>
                  <div>Success rate: {scrapers.success_rate}</div>
                  <div>Last run: {scrapers.last_run}</div>
                </div>
              )}
            </div>
            <div className="bg-white p-4 rounded shadow">
              <h2 className="font-semibold mb-2">System</h2>
              {system ? (
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>CPU: {system.cpu_usage}%</div>
                  <div>Memory: {system.memory_usage}%</div>
                  <div>Disk: {system.disk_usage}%</div>
                  <div>Processes: {system.active_processes}</div>
                  <div>Uptime: {system.uptime}</div>
                </div>
              ) : (<div>Loading…</div>)}
            </div>
          </div>

          <div className="mt-4 grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="bg-white p-4 rounded shadow">
              <h2 className="font-semibold mb-2">Database</h2>
              {database ? (
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>Size: {database.total_size}</div>
                  <div>Tables: {database.total_tables}</div>
                  <div>Records: {database.total_records}</div>
                  <div>Largest: {database.largest_table}</div>
                  <div>Last backup: {database.last_backup}</div>
                </div>
              ) : (<div>Loading…</div>)}
            </div>
            <div />
          </div>

          {/* Quick Actions */}
          <div className="mt-8">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              <a className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 text-center" href="/admin/scrapers">
                Manage Scrapers
              </a>
              <a className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 text-center" href="/api/v1/dashboard/overview">
                View API Dashboard JSON
              </a>
              <a className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 text-center" href="/metrics">
                View Metrics
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
