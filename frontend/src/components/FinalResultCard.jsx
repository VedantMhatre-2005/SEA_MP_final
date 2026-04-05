import { jsPDF } from "jspdf";

function formatInr(value) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value || 0);
}

export default function FinalResultCard({ finalEffort, converged, rounds, riskAssessment, jiraIssueKey }) {
  const riskLevel = riskAssessment?.risk_level || "MEDIUM";
  const mlRiskScore = riskAssessment?.ml_risk_score ?? 0.5;
  const budgetAnalysis = riskAssessment?.budget_analysis;
  const explainability = riskAssessment?.explainability;

  const riskTheme = {
    LOW: { box: "border-green-200 bg-green-50", text: "text-green-700", icon: "Low" },
    MEDIUM: { box: "border-amber-200 bg-amber-50", text: "text-amber-700", icon: "Medium" },
    HIGH: { box: "border-red-200 bg-red-50", text: "text-red-700", icon: "High" },
  }[riskLevel] || { box: "border-amber-200 bg-amber-50", text: "text-amber-700", icon: "Medium" };

  const downloadPdfReport = () => {
    const doc = new jsPDF({ unit: "pt", format: "a4" });
    const marginX = 48;
    const lineHeight = 18;
    const pageHeight = doc.internal.pageSize.getHeight();
    const maxWidth = doc.internal.pageSize.getWidth() - marginX * 2;
    let y = 56;

    const ensureSpace = (required = lineHeight) => {
      if (y + required > pageHeight - 48) {
        doc.addPage();
        y = 56;
      }
    };

    const addHeading = (text) => {
      ensureSpace(26);
      doc.setFont("helvetica", "bold");
      doc.setFontSize(16);
      doc.text(text, marginX, y);
      y += 24;
    };

    const addBody = (text) => {
      if (!text) return;
      doc.setFont("helvetica", "normal");
      doc.setFontSize(11);
      const lines = doc.splitTextToSize(String(text), maxWidth);
      lines.forEach((line) => {
        ensureSpace();
        doc.text(line, marginX, y);
        y += lineHeight;
      });
    };

    const addLabelValue = (label, value) => {
      addBody(`${label}: ${value}`);
    };

    addHeading("ASPRAMS Risk Analysis Report");
    addLabelValue("Generated On", new Date().toLocaleString("en-IN"));
    addLabelValue("Final Effort", `${finalEffort.toFixed(1)} person-weeks`);
    addLabelValue("Negotiation Status", converged ? "Consensus reached" : "Maximum rounds reached");
    addLabelValue("Rounds", rounds);
    addLabelValue("Jira Issue", jiraIssueKey || "N/A");

    if (riskAssessment) {
      y += 6;
      addHeading("Risk Assessment");
      addLabelValue("Risk Level", riskLevel);
      addLabelValue("ML Risk Score", `${(mlRiskScore * 100).toFixed(0)}%`);
      addLabelValue("Budget Risk", riskAssessment.budget_risk ? "Yes" : "No");

      if (explainability?.executive_summary) {
        y += 4;
        addBody("Executive Summary");
        addBody(explainability.executive_summary);
      }

      if (explainability?.risk_drivers?.length > 0) {
        y += 4;
        addBody("Top Risk Drivers");
        explainability.risk_drivers.forEach((driver, idx) => addBody(`${idx + 1}. ${driver}`));
      }

      if (explainability?.mitigation_recommendations?.length > 0) {
        y += 4;
        addBody("Recommended Mitigations");
        explainability.mitigation_recommendations.forEach((rec, idx) => addBody(`${idx + 1}. ${rec}`));
      }
    }

    if (budgetAnalysis) {
      y += 6;
      addHeading("Budget Analysis");
      addLabelValue("Available Budget", formatInr(budgetAnalysis.available_budget));
      addLabelValue("Required Budget", formatInr(budgetAnalysis.required_budget));
      addLabelValue("Cost Per Person-Week", formatInr(budgetAnalysis.cost_per_personweek));
      addLabelValue("Budget Status", budgetAnalysis.is_affordable ? "Affordable" : "Over budget");
      addLabelValue("Budget Variance", `${(budgetAnalysis.budget_variance * 100).toFixed(0)}%`);
    }

    doc.save(`asprams-report-${Date.now()}.pdf`);
  };

  return (
    <div className="relative overflow-hidden rounded-2xl border border-slate-200 bg-white p-6 sm:p-8 animate-slide-up space-y-6 shadow-sm">
      <div className="space-y-6">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <p className="text-xs uppercase font-bold tracking-widest text-slate-500 mb-1">Final Result</p>
            <h2 className="text-2xl font-bold text-slate-900">{converged ? "Consensus Reached" : "Max Rounds"}</h2>
            <p className="text-sm text-slate-600 mt-1">
              {converged
                ? `Both agents agreed after ${rounds} round${rounds > 1 ? "s" : ""}.`
                : `Agents did not converge in ${rounds} rounds. Using the final risk-adjusted estimate.`}
            </p>
          </div>
          <button
            type="button"
            onClick={downloadPdfReport}
            className="px-4 py-2 rounded-lg text-sm font-semibold bg-slate-100 hover:bg-slate-200 text-slate-800"
          >
            Download PDF
          </button>
        </div>

        <div className="flex items-end gap-3 pb-4 border-b border-slate-200">
          <span className="text-5xl sm:text-6xl font-extrabold tabular-nums text-slate-900">{finalEffort.toFixed(1)}</span>
          <div className="pb-2">
            <p className="text-lg font-semibold text-slate-800">person-weeks</p>
            <p className="text-sm text-slate-500">Total effort estimate</p>
          </div>
        </div>

        {riskAssessment && (
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wider">Risk Assessment</h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className={`border rounded-xl p-4 ${riskTheme.box}`}>
                <p className="text-xs text-slate-500 mb-2 uppercase font-bold">Risk Level</p>
                <span className={`text-2xl font-bold ${riskTheme.text}`}>{riskTheme.icon}</span>
              </div>

              <div className="border border-slate-200 rounded-xl p-4 bg-slate-50">
                <p className="text-xs text-slate-500 mb-2 uppercase font-bold">ML Risk Score</p>
                <div className="flex items-center gap-3">
                  <div className="flex-1 h-2 bg-slate-200 rounded-full overflow-hidden">
                    <div
                      className={mlRiskScore < 0.33 ? "h-full bg-green-500" : mlRiskScore < 0.66 ? "h-full bg-amber-500" : "h-full bg-red-500"}
                      style={{ width: `${mlRiskScore * 100}%` }}
                    />
                  </div>
                  <span className="font-bold text-slate-700 w-12 text-right">{(mlRiskScore * 100).toFixed(0)}%</span>
                </div>
              </div>
            </div>

            {explainability?.executive_summary && (
              <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
                <p className="text-xs text-slate-500 mb-2 uppercase font-bold">Executive Summary</p>
                <p className="text-sm text-slate-700 leading-relaxed">{explainability.executive_summary}</p>
              </div>
            )}

            {explainability?.risk_drivers?.length > 0 && (
              <div>
                <p className="text-xs text-slate-500 mb-2 uppercase font-bold">Top Risk Drivers</p>
                <ul className="space-y-2">
                  {explainability.risk_drivers.map((driver, idx) => (
                    <li key={idx} className="flex gap-3 text-sm text-slate-700">
                      <span className="text-slate-500 font-bold">{idx + 1}.</span>
                      <span>{driver}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {explainability?.mitigation_recommendations?.length > 0 && (
              <div>
                <p className="text-xs text-slate-500 mb-2 uppercase font-bold">Recommended Mitigations</p>
                <ul className="space-y-2">
                  {explainability.mitigation_recommendations.map((rec, idx) => (
                    <li key={idx} className="flex gap-3 text-sm text-slate-700">
                      <span className="text-brand-600 font-bold">-</span>
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {budgetAnalysis && (
          <div className="space-y-4 border-t border-slate-200 pt-4">
            <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wider">Budget Analysis (INR)</h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm">
              <StatPill label="Available" value={formatInr(budgetAnalysis.available_budget)} />
              <StatPill label="Required" value={formatInr(budgetAnalysis.required_budget)} />
              <StatPill label="Cost / Person-Week" value={formatInr(budgetAnalysis.cost_per_personweek)} />
            </div>
            <div className={`border rounded-xl p-4 ${budgetAnalysis.is_affordable ? "border-green-200 bg-green-50" : "border-red-200 bg-red-50"}`}>
              <p className="text-xs text-slate-500 mb-2 uppercase font-bold">Budget Status</p>
              <div className="flex items-center justify-between">
                <span className={`text-lg font-bold ${budgetAnalysis.is_affordable ? "text-green-700" : "text-red-700"}`}>
                  {budgetAnalysis.is_affordable ? "Affordable" : "Over Budget"}
                </span>
                <span className={`text-sm font-semibold ${budgetAnalysis.budget_variance > 0 ? "text-green-700" : "text-red-700"}`}>
                  {budgetAnalysis.budget_variance > 0 ? "+" : ""}{(budgetAnalysis.budget_variance * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-3 gap-3 border-t border-slate-200 pt-4">
          <StatPill label="Rounds" value={rounds} />
          <StatPill label="Status" value={converged ? "Agreed" : "Capped"} />
          <StatPill label="Jira" value={jiraIssueKey || "N/A"} highlight={!!jiraIssueKey} />
        </div>
      </div>
    </div>
  );
}

function StatPill({ label, value, highlight = false }) {
  return (
    <div className="bg-slate-50 border border-slate-200 rounded-xl p-3 text-center">
      <p className="text-xs text-slate-500 mb-1">{label}</p>
      <p className={`text-sm font-bold truncate ${highlight ? "text-brand-700" : "text-slate-800"}`}>{value}</p>
    </div>
  );
}
