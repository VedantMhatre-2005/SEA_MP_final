/**
 * Home.jsx - Main dashboard page.
 * Combines the ProjectForm, NegotiationTimeline, and FinalResultCard.
 */

import { useState } from "react";
import ProjectForm from "../components/ProjectForm";
import NegotiationTimeline from "../components/NegotiationTimeline";
import FinalResultCard from "../components/FinalResultCard";
import { analyzeProject } from "../services/api";

export default function Home() {
  const [loading, setLoading]   = useState(false);
  const [result, setResult]     = useState(null);
  const [error, setError]       = useState("");

  const handleSubmit = async (formData) => {
    setLoading(true);
    setResult(null);
    setError("");

    try {
      const data = await analyzeProject(formData);
      setResult(data);
      // Scroll to results after render
      setTimeout(() => {
        document.getElementById("results")?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 200);
    } catch (err) {
      setError(err.message || "An unexpected error occurred. Check the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen">

      {/* ── Nav ──────────────────────────────────────────────────────────── */}
      <nav className="sticky top-0 z-50 border-b border-surface-border bg-surface/80 backdrop-blur-md">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center shadow-lg">
              <span className="text-white text-sm font-bold">A</span>
            </div>
            <span className="font-bold text-lg tracking-tight text-slate-100">ASPRAMS</span>
          </div>
          <span className="text-xs text-slate-500 hidden sm:block">
            Agent-Based Software Project Risk Assessment &amp; Mitigation System
          </span>
        </div>
      </nav>

      {/* ── Hero ─────────────────────────────────────────────────────────── */}
      <header className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-10 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-600/20 border border-brand-600/30 text-brand-300 text-xs font-semibold mb-6">
          ⚡ Powered by Google Gemini
        </div>

        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight bg-gradient-to-br from-slate-100 via-brand-200 to-brand-400 bg-clip-text text-transparent mb-4">
          AI-Driven Project<br className="hidden sm:block" /> Risk Estimation
        </h1>

        <p className="max-w-2xl mx-auto text-slate-400 text-lg leading-relaxed">
          Two AI agents negotiate the true effort of your software project —
          an optimistic Estimator meets a skeptical Risk Analyst,
          powered by multi-round Gemini reasoning.
        </p>
      </header>

      {/* ── Main Content ─────────────────────────────────────────────────── */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pb-24">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">

          {/* Left: Form panel */}
          <div className="lg:col-span-2">
            <div className="card p-6 sticky top-24">
              <h2 className="text-lg font-bold text-slate-100 mb-1">Project Details</h2>
              <p className="text-sm text-slate-500 mb-6">
                Fill in your project parameters and run the multi-agent simulation.
              </p>
              <ProjectForm onSubmit={handleSubmit} loading={loading} />
            </div>
          </div>

          {/* Right: Results panel */}
          <div className="lg:col-span-3 space-y-8" id="results">

            {/* Loading overlay */}
            {loading && (
              <div className="card p-8 flex flex-col items-center justify-center gap-4 min-h-[300px] animate-fade-in">
                <div className="relative w-16 h-16">
                  <div className="absolute inset-0 rounded-full border-4 border-brand-600/20" />
                  <div className="absolute inset-0 rounded-full border-4 border-brand-500 border-t-transparent animate-spin" />
                  <span className="absolute inset-0 flex items-center justify-center text-2xl">🤖</span>
                </div>
                <div className="text-center">
                  <p className="font-semibold text-slate-200">Agents in session…</p>
                  <p className="text-sm text-slate-500 mt-1">The Estimation and Risk agents are negotiating via Gemini</p>
                </div>
              </div>
            )}

            {/* Error */}
            {error && !loading && (
              <div className="card border-red-500/30 bg-red-950/20 p-6 animate-fade-in">
                <div className="flex items-start gap-3">
                  <span className="text-2xl">⚠️</span>
                  <div>
                    <p className="font-semibold text-red-300 mb-1">Simulation Error</p>
                    <p className="text-sm text-red-400">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Results */}
            {result && !loading && (
              <>
                <FinalResultCard
                  finalEffort={result.final_effort}
                  converged={result.converged}
                  rounds={result.rounds.length}
                  jiraIssueKey={result.jira_issue_key}
                />
                <NegotiationTimeline rounds={result.rounds} />
              </>
            )}

            {/* Empty state */}
            {!result && !loading && !error && (
              <div className="card p-8 flex flex-col items-center justify-center gap-4 min-h-[300px] border-dashed">
                <div className="w-16 h-16 rounded-2xl bg-brand-600/10 flex items-center justify-center text-3xl">
                  📊
                </div>
                <div className="text-center">
                  <p className="font-semibold text-slate-400">No simulation run yet</p>
                  <p className="text-sm text-slate-600 mt-1">Fill in the project details and click "Run Simulation"</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* ── Footer ───────────────────────────────────────────────────────── */}
      <footer className="border-t border-surface-border py-6 text-center text-xs text-slate-600">
        ASPRAMS v1.0 — Agent-Based Software Project Risk Assessment &amp; Mitigation System
      </footer>
    </div>
  );
}
