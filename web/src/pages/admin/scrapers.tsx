import React, { useEffect, useState } from "react";

type Job = { id: string; enabled: boolean; last_run: string | null };

type ScraperStatus = { name: string; category: string; status: string; last_run?: string; success_rate?: number; records_collected?: number; error_count?: number };

type LogLine = { file: string; line: string; timestamp: string };

export default function AdminScrapers() {
  const [tab, setTab] = useState<'jobs'|'status'|'logs'|'failures'>('jobs');
  const [jobs, setJobs] = useState<Job[]>([]);
  const [scope, setScope] = useState("");
  const [mode, setMode] = useState("daily");
  const [since, setSince] = useState("");
  const [enabled, setEnabled] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");
  const [status, setStatus] = useState<ScraperStatus[]>([]);
  const [logs, setLogs] = useState<LogLine[]>([]);
  const [failures, setFailures] = useState<any>(null);

  const refresh = async () => {
    setError("");
    try {
      const s = await fetch("/api/v1/scrapers/service-status");
      const sv = await s.json();
      setEnabled(!!sv.enabled);
      if (sv.enabled) {
        const [rj, rs, rl, rf] = await Promise.all([
          fetch("/api/v1/scrapers/jobs"),
          fetch("/api/v1/scrapers/status"),
          fetch("/api/v1/scrapers/logs?limit=100"),
          fetch("/api/v1/scrapers/failures"),
        ]);
        if (!rj.ok) throw new Error(await rj.text());
        const jobsData = await rj.json();
        setJobs(jobsData);
        try { setStatus(((await rs.json())||[]) as any); } catch {}
        try { const jl = await rl.json(); setLogs(jl.logs||[]); } catch {}
        try { setFailures(await rf.json()); } catch {}
      } else {
        setJobs([]); setStatus([]); setLogs([]); setFailures(null);
      }
    } catch (e: any) {
      setError(e?.message || "Failed to load");
    }
  };

  useEffect(() => { refresh(); }, []);

  const runNow = async () => {
    setLoading(true);
    try {
      await fetch("/api/v1/scrapers/run-now", { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({ scope, mode, since: since || undefined }) });
      alert(`Queued: ${scope} (${mode}${since?`, since ${since}`:''})`);
    } finally { setLoading(false); }
  };

  const toggleJob = async (job: Job, next: boolean) => {
    setLoading(true);
    try {
      await fetch("/api/v1/scrapers/jobs/toggle", { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({ job_id: job.id, enabled: next }) });
      await refresh();
    } finally { setLoading(false); }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-4">
        <h1 className="text-xl font-semibold">Scrapers</h1>
        <div className="text-sm text-gray-600">Service enabled: {enabled === null ? '…' : String(enabled)}</div>
      </div>
      {error && <div style={{color:'red'}}>{error}</div>}

      <div className="flex gap-2 border-b">
        {(['jobs','status','logs','failures'] as const).map(t=>
          <button key={t} className={`px-3 py-2 ${tab===t?'border-b-2 border-black':''}`} onClick={()=>setTab(t)}>{t.toUpperCase()}</button>
        )}
      </div>

      {enabled ? (
        <>
          {tab==='jobs' && (
            <div className="space-y-4">
              <ul>
                {jobs.map(j=>
                  <li key={j.id} className="flex items-center gap-2 py-1">
                    <span className="font-mono text-sm">{j.id}</span>
                    <span>— enabled: {String(j.enabled)}</span>
                    <span>— last_run: {j.last_run||"—"}</span>
                    <button disabled={loading || j.enabled} onClick={()=>toggleJob(j, true)} className="px-2 py-1 bg-gray-100 rounded">Enable</button>
                    <button disabled={loading || !j.enabled} onClick={()=>toggleJob(j, false)} className="px-2 py-1 bg-gray-100 rounded">Disable</button>
                  </li>
                )}
              </ul>
              <div className="flex gap-2 items-center">
                <select value={mode} onChange={e=>setMode(e.target.value)} className="border px-2 py-1">
                  <option value="daily">daily</option>
                  <option value="bootstrap">bootstrap</option>
                  <option value="special">special</option>
                </select>
                <input className="border px-2 py-1" placeholder="scope (e.g., federal:*)" value={scope} onChange={e=>setScope(e.target.value)} />
                {mode === 'bootstrap' && (
                  <input className="border px-2 py-1" type="date" placeholder="since (YYYY-MM-DD)" value={since} onChange={e=>setSince(e.target.value)} />
                )}
                <button className="px-3 py-1 bg-black text-white rounded" disabled={loading || !scope} onClick={runNow}>Run Now</button>
                <button className="px-3 py-1 bg-indigo-600 text-white rounded" disabled={loading} onClick={async()=>{
                  setLoading(true);
                  try {
                    await fetch("/api/v1/scrapers/run-now", { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({ scope: "*:*", mode: "daily" }) });
                    alert("Queued all daily scrapers");
                  } finally { setLoading(false); }
                }}>Run All Daily</button>
              </div>
            </div>
          )}
          {tab==='status' && (
            <div className="bg-white rounded shadow">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="px-2 py-1 text-left">Name</th>
                    <th className="px-2 py-1 text-left">Category</th>
                    <th className="px-2 py-1 text-left">Status</th>
                    <th className="px-2 py-1 text-left">Last Run</th>
                    <th className="px-2 py-1 text-left">Success Rate</th>
                    <th className="px-2 py-1 text-left">Records</th>
                    <th className="px-2 py-1 text-left">Errors</th>
                  </tr>
                </thead>
                <tbody>
                  {status.map((s,i)=> (
                    <tr key={i} className="border-t">
                      <td className="px-2 py-1">{s.name}</td>
                      <td className="px-2 py-1">{s.category}</td>
                      <td className="px-2 py-1">{s.status}</td>
                      <td className="px-2 py-1">{s.last_run||'—'}</td>
                      <td className="px-2 py-1">{s.success_rate ?? '—'}</td>
                      <td className="px-2 py-1">{s.records_collected ?? '—'}</td>
                      <td className="px-2 py-1">{s.error_count ?? '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {tab==='logs' && (
            <div className="bg-white rounded shadow p-2">
              <div className="text-sm text-gray-600 mb-2">Most recent logs</div>
              <pre className="bg-gray-50 p-2 rounded overflow-auto" style={{maxHeight: 400}}>
                {logs.map((l,i)=> <div key={i}><span className="text-gray-400">[{l.timestamp}]</span> <span className="text-gray-500">{l.file}</span>: {l.line}</div>)}
              </pre>
            </div>
          )}
          {tab==='failures' && (
            <div className="bg-white rounded shadow p-2 text-sm">
              <pre className="bg-gray-50 p-2 rounded overflow-auto" style={{maxHeight: 400}}>
                {JSON.stringify(failures, null, 2)}
              </pre>
            </div>
          )}
        </>
      ) : (
        <div>Feature flag off. Enable SCRAPER_SERVICE_ENABLED to use.</div>
      )}
    </div>
  );
}
