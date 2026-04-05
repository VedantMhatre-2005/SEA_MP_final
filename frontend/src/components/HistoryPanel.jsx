export default function HistoryPanel({ items, onLoadItem }) {
  if (!items?.length) {
    return (
      <div className="card p-4">
        <p className="text-sm text-slate-600">No history yet. Run your first simulation.</p>
      </div>
    );
  }

  return (
    <div className="card p-4">
      <h3 className="text-sm font-semibold text-slate-800 mb-3">Past Analyses</h3>
      <div className="space-y-3 max-h-80 overflow-auto">
        {items.map((item) => (
          <button
            key={item.id}
            onClick={() => onLoadItem(item.result)}
            className="w-full text-left border border-slate-200 rounded-xl p-3 hover:bg-slate-50 transition"
            type="button"
          >
            <p className="text-xs text-slate-500">{new Date(item.created_at).toLocaleString()}</p>
            <p className="text-sm text-slate-800 font-medium mt-1 line-clamp-2">{item.project_input.description}</p>
            <p className="text-xs text-slate-600 mt-1">
              Risk: {item.result?.risk_assessment?.risk_level || "N/A"} | Effort: {item.result?.final_effort?.toFixed?.(1) ?? item.result?.final_effort}
            </p>
          </button>
        ))}
      </div>
    </div>
  );
}
