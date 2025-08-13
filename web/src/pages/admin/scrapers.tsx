import React, { useEffect, useState } from "react";

type Job = { id: string; enabled: boolean; last_run: string | null };

export default function AdminScrapers() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [scope, setScope] = useState("");
  const [mode, setMode] = useState("daily");
  const [since, setSince] = useState("");
  const [enabled, setEnabled] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");

  const refresh = async () => {
    setError("");
    try {
      const s = await fetch("/api/v1/scrapers/status");
      const sv = await s.json();
      setEnabled(!!sv.enabled);
      if (sv.enabled) {
        const r = await fetch("/api/v1/scrapers/jobs");
        if (!r.ok) throw new Error(await r.text());
        setJobs(await r.json());
      } else {
        setJobs([]);
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
    <div className="p-6 space-y-4">
      <h1>Scrapers</h1>
      {error && <div style={{color:'red'}}>{error}</div>}
      <div>Service enabled: {enabled === null ? '…' : String(enabled)}</div>
      {enabled ? (
        <>
          <ul>
            {jobs.map(j=>
              <li key={j.id} className="flex items-center gap-2">
                <span>{j.id}</span>
                <span>— enabled: {String(j.enabled)}</span>
                <span>— last_run: {j.last_run||"—"}</span>
                <button disabled={loading || j.enabled} onClick={()=>toggleJob(j, true)}>Enable</button>
                <button disabled={loading || !j.enabled} onClick={()=>toggleJob(j, false)}>Disable</button>
              </li>
            )}
          </ul>
          <div style={{marginTop:16}} className="flex flex-col gap-2">
            <div className="flex gap-2 items-center">
              <select value={mode} onChange={e=>setMode(e.target.value)}>
                <option value="daily">daily</option>
                <option value="bootstrap">bootstrap</option>
                <option value="special">special</option>
              </select>
              <input placeholder="scope (e.g., federal:*)" value={scope} onChange={e=>setScope(e.target.value)} />
              {mode === 'bootstrap' && (
                <input type="date" placeholder="since (YYYY-MM-DD)" value={since} onChange={e=>setSince(e.target.value)} />
              )}
              <button disabled={loading || !scope} onClick={runNow}>Run Now</button>
            </div>
          </div>
        </>
      ) : (
        <div>Feature flag off. Enable SCRAPER_SERVICE_ENABLED to use.</div>
      )}
    </div>
  );
}
