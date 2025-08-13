import React from 'react';

type ToastProps = { message: string; type?: 'success'|'error'|'info'; onClose?: ()=>void };

export default function Toast({ message, type='info', onClose }: ToastProps) {
  const color = type==='success' ? 'bg-green-600' : type==='error' ? 'bg-red-600' : 'bg-gray-800';
  return (
    <div className={`fixed bottom-4 right-4 text-white px-4 py-2 rounded shadow ${color}`}
         role="status" aria-live="polite">
      <span>{message}</span>
      {onClose && <button className="ml-3 underline" onClick={onClose}>Close</button>}
    </div>
  );
}