import React, { useEffect, useState } from 'react';

export default function AdminAudit() {
  const [events, setEvents] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [limit, setLimit] = useState(50);

  const load = async (o = 0) => {
    const r = await fetch(`/api/v1/admin/audit?limit=${limit}&offset=${o}`);
    if (r.ok) {
      const data = await r.json();
      setEvents(data.events || []);
      setTotal(data.total || 0);
      setOffset(o);
    }
  };

  useEffect(() => { load(0); }, [limit]);

  return (
    <div className="p-6">
      <h1>Admin Audit</h1>
      <div className="text-sm text-gray-600">Total: {total}</div>
      <div className="my-2 flex gap-2 items-center">
        <label>Limit:</label>
        <input type="number" value={limit} min={10} max={500} onChange={e=>setLimit(parseInt(e.target.value||'50',10))} />
        <button disabled={offset<=0} onClick={()=>load(Math.max(offset-limit, 0))}>Prev</button>
        <button disabled={offset+limit>=total} onClick={()=>load(offset+limit)}>Next</button>
        <button onClick={()=>load(0)}>Refresh</button>
      </div>
      <pre className="bg-gray-50 p-2 rounded overflow-auto" style={{maxHeight: 400}}>
        {events.map((e, i)=> <div key={i}>{JSON.stringify(e)}</div>)}
      </pre>
    </div>
  );
}