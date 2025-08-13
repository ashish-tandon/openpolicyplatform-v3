import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import StatCard from '../../components/shared/StatCard';

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
  const [scraperConfig, setScraperConfig] = useState<any>(null);

  useEffect(() => {
    fetchDashboardStats();
    fetch('/api/v1/admin/status/unified').then(r=>r.json()).then(setUnified).catch(()=>{});
    fetch('/api/v1/dashboard/system').then(r=>r.json()).then(setSystem).catch(()=>{});
    fetch('/api/v1/dashboard/scrapers').then(r=>r.json()).then(setScrapers).catch(()=>{});
    fetch('/api/v1/dashboard/database').then(r=>r.json()).then(setDatabase).catch(()=>{});
    fetch('/api/v1/admin/config/scraper').then(r=>r.json()).then(setScraperConfig).catch(()=>{});
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
    <div className="min-h-screen bg-gray-50">
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
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard title="Total Policies" value={stats.totalPolicies} color="blue" />
          <StatCard title="Active Scrapers" value={stats.activeScrapers} color="green" />
          <StatCard title="Last Update" value={new Date(stats.lastUpdate).toLocaleString()} color="yellow" />
          <StatCard title="System" value={system ? `${system.cpu_usage}% CPU / ${system.memory_usage}% MEM` : 'Loading…'} color="purple" />
        </div>

        <div className="mt-8 grid grid-cols-1 gap-4 lg:grid-cols-2">
          <div className="bg-white p-4 rounded shadow">
            <h2 className="font-semibold mb-2">Scraper Service</h2>
            <div className="text-sm">Enabled: {unified?.scraper_service?.enabled ? 'true' : 'false'}</div>
            <div className="mt-2 grid grid-cols-2 gap-2 text-sm">
              {scrapers && (
                <>
                  <div>Total scrapers: {scrapers.total_scrapers}</div>
                  <div>Active: {scrapers.active_scrapers}</div>
                  <div>Success rate: {scrapers.success_rate}</div>
                  <div>Last run: {scrapers.last_run}</div>
                </>
              )}
              {scraperConfig && (
                <>
                  <div>DB: {scraperConfig.scrapers_database_url || 'inherit'}</div>
                  <div>Concurrency: {scraperConfig.scraper_concurrency}</div>
                  <div>Rate limit: {scraperConfig.scraper_rate_limit_per_domain}</div>
                  <div>User-Agent: {scraperConfig.scraper_user_agent}</div>
                  <div>Timeouts: {scraperConfig.scraper_timeouts}s</div>
                  <div>Retries: {scraperConfig.scraper_retries}</div>
                  <div>Scheduler: {String(scraperConfig.scheduler_enabled)}</div>
                  <div>Default scope: {scraperConfig.scheduler_default_scope}</div>
                </>
              )}
            </div>
            <div className="mt-2">
              <h3 className="font-medium">Endpoints</h3>
              <ul className="list-disc list-inside text-sm text-blue-700">
                {unified?.links?.scrapers?.map((p:string)=>(<li key={p}><a href={p}>{p}</a></li>))}
              </ul>
            </div>
            <div className="mt-2 flex gap-2">
              <a className="px-3 py-1 bg-gray-100 rounded" href="/admin/scrapers">Manage Scrapers</a>
              <button className="px-3 py-1 bg-indigo-600 text-white rounded" onClick={async()=>{
                await fetch('/api/v1/scrapers/run-now', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({scope: '*:*', mode: 'daily'})});
                alert('Queued all daily scrapers');
              }}>Run All Daily</button>
            </div>
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
          <div className="bg-white p-4 rounded shadow">
            <h2 className="font-semibold mb-2">Quick Links</h2>
            <ul className="list-disc list-inside text-sm text-blue-700">
              {(unified?.links?.health||[]).map((p:string)=>(<li key={p}><a href={p}>{p}</a></li>))}
              {(unified?.links?.dashboard||[]).map((p:string)=>(<li key={p}><a href={p}>{p}</a></li>))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
