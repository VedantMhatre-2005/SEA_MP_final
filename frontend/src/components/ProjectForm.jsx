/**
 * ProjectForm.jsx
 * Controlled form for collecting project details before running a simulation.
 */

import { useState } from "react";

const COMPLEXITY_OPTIONS = [
  { value: "low",      label: "🟢 Low",      desc: "Well-understood domain, small scope" },
  { value: "medium",   label: "🟡 Medium",   desc: "Some unknowns, moderate integrations" },
  { value: "high",     label: "🟠 High",     desc: "Complex domain, many moving parts" },
  { value: "critical", label: "🔴 Critical", desc: "Mission-critical, high ambiguity" },
];

const INITIAL_FORM = {
  description: "",
  team_size: "",
  duration: "",
  complexity: "medium",
};

/**
 * @param {{ onSubmit: (data: object) => void, loading: boolean }} props
 */
export default function ProjectForm({ onSubmit, loading }) {
  const [form, setForm] = useState(INITIAL_FORM);
  const [errors, setErrors] = useState({});

  const validate = () => {
    const errs = {};
    if (form.description.trim().length < 10)
      errs.description = "Description must be at least 10 characters.";
    if (!form.team_size || form.team_size < 1 || form.team_size > 100)
      errs.team_size = "Team size must be between 1 and 100.";
    if (!form.duration || form.duration < 1 || form.duration > 365)
      errs.duration = "Duration must be between 1 and 365 weeks.";
    return errs;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: "" }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length > 0) { setErrors(errs); return; }
    onSubmit({
      description: form.description.trim(),
      team_size:   parseInt(form.team_size, 10),
      duration:    parseInt(form.duration, 10),
      complexity:  form.complexity,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6" noValidate>

      {/* Description */}
      <div>
        <label className="block text-sm font-medium text-slate-300 mb-1.5">
          Project Description <span className="text-brand-400">*</span>
        </label>
        <textarea
          name="description"
          rows={4}
          value={form.description}
          onChange={handleChange}
          placeholder="Describe your software project — scope, technologies, goals..."
          className={`form-input resize-none ${errors.description ? "border-red-500 focus:ring-red-500" : ""}`}
        />
        {errors.description && (
          <p className="mt-1.5 text-xs text-red-400">{errors.description}</p>
        )}
      </div>

      {/* Team size + Duration */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1.5">
            Team Size <span className="text-brand-400">*</span>
          </label>
          <div className="relative">
            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-surface-muted text-sm">👥</span>
            <input
              type="number"
              name="team_size"
              min="1" max="100"
              value={form.team_size}
              onChange={handleChange}
              placeholder="e.g. 5"
              className={`form-input pl-9 ${errors.team_size ? "border-red-500 focus:ring-red-500" : ""}`}
            />
          </div>
          {errors.team_size && (
            <p className="mt-1.5 text-xs text-red-400">{errors.team_size}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1.5">
            Duration <span className="text-slate-500 font-normal">(weeks)</span> <span className="text-brand-400">*</span>
          </label>
          <div className="relative">
            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-surface-muted text-sm">📅</span>
            <input
              type="number"
              name="duration"
              min="1" max="365"
              value={form.duration}
              onChange={handleChange}
              placeholder="e.g. 12"
              className={`form-input pl-9 ${errors.duration ? "border-red-500 focus:ring-red-500" : ""}`}
            />
          </div>
          {errors.duration && (
            <p className="mt-1.5 text-xs text-red-400">{errors.duration}</p>
          )}
        </div>
      </div>

      {/* Complexity */}
      <div>
        <label className="block text-sm font-medium text-slate-300 mb-2">
          Complexity Level <span className="text-brand-400">*</span>
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {COMPLEXITY_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              type="button"
              onClick={() => setForm((p) => ({ ...p, complexity: opt.value }))}
              title={opt.desc}
              className={`relative rounded-xl px-3 py-3 text-sm font-medium border transition-all duration-200 text-center
                ${form.complexity === opt.value
                  ? "bg-brand-600/30 border-brand-500 text-brand-300 shadow-md shadow-brand-900/30"
                  : "bg-surface border-surface-border text-slate-400 hover:border-surface-muted hover:text-slate-300"
                }`}
            >
              {opt.label}
              {form.complexity === opt.value && (
                <span className="absolute top-1 right-1.5 w-1.5 h-1.5 rounded-full bg-brand-400" />
              )}
            </button>
          ))}
        </div>
        <p className="mt-1.5 text-xs text-slate-500">
          {COMPLEXITY_OPTIONS.find((o) => o.value === form.complexity)?.desc}
        </p>
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={loading}
        className="btn-primary w-full text-base"
      >
        {loading ? (
          <>
            <span className="w-5 h-5 rounded-full border-2 border-white/30 border-t-white animate-spin" />
            Agents Negotiating…
          </>
        ) : (
          <>
            <span>⚡</span> Run Simulation
          </>
        )}
      </button>
    </form>
  );
}
