/**
 * NegotiationTimeline.jsx
 * Renders the full negotiation history as an animated vertical timeline.
 * Each round shows both the Estimation Agent and Risk Agent responses.
 */

/** @param {{ decision: "ACCEPT"|"COUNTER" }} props */
function DecisionBadge({ decision }) {
  return decision === "ACCEPT" ? (
    <span className="badge-accept">✅ ACCEPT</span>
  ) : (
    <span className="badge-counter">🔄 COUNTER</span>
  );
}

/** @param {{ label: string, effort: number, decision: string, reason: string, side: "left"|"right" }} props */
function AgentCard({ label, effort, decision, reason, side }) {
  const isLeft = side === "left";
  return (
    <div
      className={`rounded-xl border p-4 flex-1 min-w-0 animate-fade-in
      ${isLeft
        ? "border-brand-700/50 bg-brand-950/40"
        : "border-amber-800/40 bg-amber-950/20"
      }`}
    >
      <div className="flex items-center justify-between gap-2 mb-2 flex-wrap">
        <span className={`text-xs font-bold uppercase tracking-wider ${isLeft ? "text-brand-400" : "text-amber-400"}`}>
          {label}
        </span>
        <DecisionBadge decision={decision} />
      </div>

      <p className={`text-2xl font-bold mb-2 ${isLeft ? "text-brand-300" : "text-amber-300"}`}>
        {effort.toFixed(1)}
        <span className="text-sm font-normal text-slate-400 ml-1">person-wks</span>
      </p>

      <p className="text-xs text-slate-400 leading-relaxed line-clamp-4" title={reason}>
        {reason}
      </p>
    </div>
  );
}

/**
 * @param {{ rounds: Array<object> }} props
 */
export default function NegotiationTimeline({ rounds }) {
  if (!rounds || rounds.length === 0) return null;

  return (
    <div className="space-y-8">
      <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
        <span className="w-7 h-7 rounded-lg bg-brand-600/30 flex items-center justify-center text-brand-300 text-sm">🤝</span>
        Negotiation Timeline
      </h2>

      <div className="relative">
        {rounds.map((round, index) => (
          <div
            key={round.round_number}
            className="relative flex gap-4 mb-8 animate-slide-up"
            style={{ animationDelay: `${index * 0.1}s` }}
          >
            {/* Round number bubble */}
            <div className="relative flex-shrink-0 flex flex-col items-center">
              <div className="w-10 h-10 rounded-xl bg-brand-600 flex items-center justify-center z-10 shadow-lg shadow-brand-900/50">
                <span className="text-white text-sm font-bold">{round.round_number}</span>
              </div>
              {/* Connector line */}
              {index < rounds.length - 1 && (
                <div className="w-px flex-1 bg-gradient-to-b from-brand-600/50 to-transparent mt-1" style={{ minHeight: "2rem" }} />
              )}
            </div>

            {/* Cards */}
            <div className="flex-1 flex flex-col sm:flex-row gap-3 pb-2">
              <AgentCard
                label="⚡ Estimation Agent"
                effort={round.estimation_agent.effort}
                decision={round.estimation_agent.decision}
                reason={round.estimation_agent.reason}
                side="left"
              />
              <AgentCard
                label="🛡️ Risk Agent"
                effort={round.risk_agent.effort}
                decision={round.risk_agent.decision}
                reason={round.risk_agent.reason}
                side="right"
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
