import React, { useEffect, useState } from "react";
export default function AdminScrapers() {
  const [jobs, setJobs] = useState<any[]>([]);
  const [scope, setScope] = useState("");
  useEffect(() => { fetch("/api/v1/scrapers/jobs").then(r=>r.json()).then(setJobs) }, []);
  const runNow = async () => {
    await fetch("/api/v1/scrapers/run-now", { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({ scope }) });
    alert("Queued: "+scope);
  };
  return (
    <div className="p-6">
      <h1>Scrapers</h1>
      <ul>{jobs.map(j=><li key={j.id}>{j.id} — enabled: {String(j.enabled)} — last_run: {j.last_run||"—"}</li>)}</ul>
      <div style={{marginTop:16}}>
        <input placeholder="scope (e.g., federal:*)" value={scope} onChange={e=>setScope(e.target.value)} />
        <button onClick={runNow}>Run Now</button>
      </div>
    </div>
  );
}
