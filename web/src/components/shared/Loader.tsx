export default function Loader({ label = 'Loading...' }: { label?: string }) {
  return (
    <div role="status" aria-live="polite" className="flex items-center gap-2 text-gray-600">
      <span className="animate-pulse">●</span>
      <span>{label}</span>
    </div>
  );
}