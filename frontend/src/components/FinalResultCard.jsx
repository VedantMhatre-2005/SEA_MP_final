/**
 * FinalResultCard.jsx
 * Prominent summary card showing the final agreed effort and simulation status.
 */

/**
 * @param {{
 *   finalEffort: number,
 *   converged: boolean,
 *   rounds: number,
 *   jiraIssueKey?: string
 * }} props
 */
export default function FinalResultCard({ finalEffort, converged, rounds, jiraIssueKey }) {
  return (
    <div className={`relative overflow-hidden rounded-2xl border p-6 sm:p-8 animate-slide-up
      ${converged
        ? "border-emerald-500/30 bg-emerald-950/20"
        : "border-amber-500/30 bg-amber-950/20"
      }`}
    >
      {/* Background glow */}
      <div
        className={`absolute inset-0 opacity-20 pointer-events-none
          ${converged
            ? "bg-gradient-to-br from-emerald-600/30 to-transparent"
            : "bg-gradient-to-br from-amber-600/30 to-transparent"
          }`}
      />

      <div className="relative">
        {/* Header */}
        <div className="flex items-start justify-between gap-4 mb-6 flex-wrap">
          <div>
            <p className="text-xs uppercase font-bold tracking-widest text-slate-500 mb-1">
              Final Result
            </p>
            <h2 className="text-2xl font-bold text-slate-100">
              {converged ? "✅ Consensus Reached" : "⚠️ Max Rounds — Estimate Provided"}
            </h2>
            <p className="text-sm text-slate-400 mt-1">
              {converged
                ? `Both agents agreed after ${rounds} round${rounds > 1 ? "s" : ""} of negotiation.`
                : `Agents did not fully converge in ${rounds} rounds. Using final risk-adjusted figure.`}
            </p>
          </div>
        </div>

        {/* Effort Metric */}
        <div className="flex items-end gap-3 mb-6">
          <span className={`text-6xl sm:text-7xl font-extrabold tabular-nums
            ${converged ? "text-emerald-300" : "text-amber-300"}`}
          >
            {finalEffort.toFixed(1)}
          </span>
          <div className="pb-2">
            <p className="text-lg font-semibold text-slate-300">person-weeks</p>
            <p className="text-sm text-slate-500">Total effort estimate</p>
          </div>
        </div>

        {/* Stats row */}
        <div className="grid grid-cols-3 gap-4">
          <StatPill label="Rounds" value={rounds} />
          <StatPill label="Status" value={converged ? "Accepted" : "Capped"} />
          <StatPill
            label="Jira Issue"
            value={jiraIssueKey || "—"}
            highlight={!!jiraIssueKey}
          />
        </div>
      </div>
    </div>
  );
}

function StatPill({ label, value, highlight = false }) {
  return (
    <div className="bg-surface/60 border border-surface-border rounded-xl p-3 text-center">
      <p className="text-xs text-slate-500 mb-1">{label}</p>
      <p className={`text-sm font-bold truncate ${highlight ? "text-blue-400" : "text-slate-200"}`}>
        {value}
      </p>
    </div>
  );
}
