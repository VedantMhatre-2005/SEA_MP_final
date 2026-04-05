/**
 * api.js - Axios API service layer.
 * Provides typed wrappers around ASPRAMS backend endpoints.
 */

import axios from "axios";

// Base URL can be overridden via VITE_API_URL environment variable.
// Default to localhost:8000 for local development.
const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
});

// ─── Request interceptor: log outgoing requests in dev ────────────────────────
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("asprams_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  if (import.meta.env.DEV) {
    console.debug(`[API] ${config.method?.toUpperCase()} ${config.url}`, config.data);
  }
  return config;
});

// ─── Response interceptor: normalize errors ───────────────────────────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      "An unexpected error occurred";
    return Promise.reject(new Error(message));
  }
);

/**
 * Run the ASPRAMS multi-agent simulation.
 *
 * @param {{ description: string, team_size: number, duration: number, complexity: string }} data
 * @returns {Promise<import('../types').NegotiationResult>}
 */
export const analyzeProject = (data) => api.post("/analyze", data).then((r) => r.data);

export const registerUser = (data) => api.post("/auth/register", data).then((r) => r.data);

export const loginUser = (data) => api.post("/auth/login", data).then((r) => r.data);

export const getCurrentUser = () => api.get("/auth/me").then((r) => r.data);

export const getHistory = () => api.get("/history").then((r) => r.data);

/**
 * Check API health.
 * @returns {Promise<{ status: string, timestamp: string }>}
 */
export const checkHealth = () => api.get("/health").then((r) => r.data);
