import { useEffect, useState } from "react";
import ProjectForm from "../components/ProjectForm";
import NegotiationTimeline from "../components/NegotiationTimeline";
import FinalResultCard from "../components/FinalResultCard";
import AuthPanel from "../components/AuthPanel";
import HistoryPanel from "../components/HistoryPanel";
import { analyzeProject, getHistory } from "../services/api";

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [user, setUser] = useState(null);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [historyItems, setHistoryItems] = useState([]);

  useEffect(() => {
    const cached = localStorage.getItem("asprams_user");
    if (cached) {
      try {
        setUser(JSON.parse(cached));
      } catch {
        localStorage.removeItem("asprams_user");
        localStorage.removeItem("asprams_token");
      }
    }
  }, []);

  const handleSubmit = async (formData) => {
    setLoading(true);
    setResult(null);
    setError("");

    try {
      const data = await analyzeProject(formData);
      setResult(data);
      setTimeout(() => {
        document.getElementById("results")?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 200);
    } catch (err) {
      setError(err.message || "Unexpected error. Check backend logs.");
    } finally {
      setLoading(false);
    }
  };

  const loadHistory = async () => {
    setError("");
    try {
      const data = await getHistory();
      setHistoryItems(data);
      setHistoryOpen(true);
    } catch (err) {
      setError(err.message || "Failed to load history");
    }
  };

  const logout = () => {
    localStorage.removeItem("asprams_token");
    localStorage.removeItem("asprams_user");
    setUser(null);
    setResult(null);
    setHistoryItems([]);
    setHistoryOpen(false);
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-white via-slate-50 to-brand-50/40 p-4 sm:p-8">
        <div className="max-w-2xl mx-auto pt-8">
          <header className="text-center mb-8">
            <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-slate-900">ASPRAMS</h1>
            <p className="mt-2 text-slate-600">Agent-Based Software Project Risk Assessment and Mitigation System</p>
          </header>
          <AuthPanel onAuthenticated={setUser} />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-white via-slate-50 to-brand-50/40">
      <nav className="sticky top-0 z-50 border-b border-slate-200 bg-white/85 backdrop-blur-md">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center shadow-sm">
              <span className="text-white text-sm font-bold">A</span>
            </div>
            <span className="font-bold text-lg tracking-tight text-slate-900">ASPRAMS</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-slate-600 hidden sm:block">Hi, {user.name}</span>
            <button type="button" onClick={loadHistory} className="px-3 py-1.5 rounded-lg text-sm bg-slate-100 hover:bg-slate-200 text-slate-800">
              History
            </button>
            <button type="button" onClick={logout} className="px-3 py-1.5 rounded-lg text-sm bg-red-50 hover:bg-red-100 text-red-700 border border-red-200">
              Logout
            </button>
          </div>
        </div>
      </nav>

      <header className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-12 pb-8 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-50 border border-brand-200 text-brand-700 text-xs font-semibold mb-6">
          Powered by Gemini + ML Risk Scoring
        </div>
        <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-slate-900 mb-3">Project Risk Intelligence Dashboard</h1>
        <p className="max-w-3xl mx-auto text-slate-600 text-lg leading-relaxed">
          Run multi-agent simulation, estimate risk with machine learning, and persist your analysis history in MongoDB.
        </p>
      </header>

      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
          <div className="lg:col-span-2 space-y-4">
            <div className="card p-6 sticky top-24">
              <h2 className="text-lg font-bold text-slate-900 mb-1">Project Details</h2>
              <p className="text-sm text-slate-600 mb-6">Enter input data to run risk analysis.</p>
              <ProjectForm onSubmit={handleSubmit} loading={loading} />
            </div>
            {historyOpen && <HistoryPanel items={historyItems} onLoadItem={(r) => setResult(r)} />}
          </div>

          <div className="lg:col-span-3 space-y-8" id="results">
            {loading && (
              <div className="card p-8 flex flex-col items-center justify-center gap-4 min-h-[280px] animate-fade-in">
                <div className="relative w-14 h-14">
                  <div className="absolute inset-0 rounded-full border-4 border-brand-200" />
                  <div className="absolute inset-0 rounded-full border-4 border-brand-500 border-t-transparent animate-spin" />
                  <span className="absolute inset-0 flex items-center justify-center text-xl">AI</span>
                </div>
                <p className="font-semibold text-slate-800">Agents are negotiating...</p>
                <p className="text-sm text-slate-600">This may take a few seconds depending on model response time.</p>
              </div>
            )}

            {error && !loading && (
              <div className="card border-red-200 bg-red-50 p-6 animate-fade-in">
                <p className="font-semibold text-red-700 mb-1">Simulation Error</p>
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            {result && !loading && (
              <>
                <FinalResultCard
                  finalEffort={result.final_effort}
                  converged={result.converged}
                  rounds={result.rounds.length}
                  riskAssessment={result.risk_assessment}
                  jiraIssueKey={result.jira_issue_key}
                />
                <NegotiationTimeline rounds={result.rounds} />
              </>
            )}

            {!result && !loading && !error && (
              <div className="card p-8 text-center min-h-[280px] flex flex-col justify-center">
                <p className="text-slate-800 font-semibold">No simulation yet</p>
                <p className="text-sm text-slate-600 mt-1">Submit project details to run the analysis.</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
