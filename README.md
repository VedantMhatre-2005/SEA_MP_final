# ASPRAMS — Agent-Based Software Project Risk Assessment and Mitigation System

> A full-stack AI-powered system that simulates negotiation between an **Estimation Agent** and a **Risk Analysis Agent** to arrive at a realistic software project effort estimate — powered by **Google Gemini** and **Machine Learning**.

---

## 💡 Why ASPRAMS?

Software projects frequently fail due to:
- ❌ Unrealistic effort estimates (overoptimism bias)
- ❌ Unidentified technical risks
- ❌ Budget overruns
- ❌ Unclear reasoning behind decisions

**ASPRAMS addresses this by**:
- ✅ Simulating agent negotiation to balance optimism with skepticism
- ✅ Using ML to predict risk based on project characteristics
- ✅ Providing explainable reasoning from AI agents + ML models
- ✅ Identifying specific mitigation strategies
- ✅ Tracking budget feasibility against effort estimates
- ✅ Generating Jira stories automatically for integration with project management

**Ideal for:**
- Project managers planning sprints and releases
- Software architects estimating technical scope
- Organizations improving estimation accuracy
- Teams seeking transparent, data-driven decision support
- Academic study of software engineering practices

---

## 📖 Table of Contents

1. [Architecture](#-architecture)
2. [Quick Start](#-quick-start)
3. [How It Works](#-how-the-multi-agent-system-works)
4. [Key Features](#-key-features)
5. [Configuration](#️-configuration)
6. [ML Risk Model](#-machine-learning-risk-model)
7. [User Interface](#-user-interface)
8. [API Reference](#-api-reference)
9. [Jira Integration](#-jira-integration)
10. [Docker / Deployment](#️-docker-production)
11. [Example Workflow](#-example-workflow)
12. [Troubleshooting](#-troubleshooting)
13. [License](#-license)

---

## 📐 Architecture

```
asprams/
├── backend/                  # FastAPI + multi-agent + ML system
│   ├── main.py               # App entry point
│   ├── agents/
│   │   ├── estimation_agent.py       # Optimistic estimate via Gemini
│   │   ├── risk_agent.py             # Risk-adjusted counter via Gemini
│   │   └── explainability_agent.py   # Natural language synthesis & recommendations
│   ├── ml/                   # Machine Learning risk scoring
│   │   ├── model.py                  # Linear Regression risk model
│   │   ├── feature_engine.py         # 14-feature extraction pipeline
│   │   └── synthetic_data.py         # Synthetic project dataset generator
│   ├── core/
│   │   ├── negotiation_engine.py     # Iterative negotiation loop
│   │   └── schemas.py                # Pydantic request/response models
│   ├── config/
│   │   └── settings.py               # Environment variable management
│   ├── integrations/
│   │   └── jira_service.py           # Jira REST API integration
│   ├── routes/
│   │   ├── analyze.py                # POST /analyze (full pipeline)
│   │   └── health.py                 # GET /health
│   ├── tests/
│   │   └── test_api.py               # Integration tests
│   └── requirements.txt
├── frontend/                 # Vite + React + Tailwind CSS
│   └── src/
│       ├── components/               # Form, Timeline, ResultCard
│       ├── pages/                    # Home dashboard
│       └── services/                 # Axios API client
├── .github/workflows/ci.yml  # GitHub Actions pipeline
├── .env.example              # Environment variable template
├── Dockerfile                # Multi-stage production build
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- A Google Gemini API key ([get one here](https://aistudio.google.com/app/apikey))

### 1. Clone and configure

```bash
git clone <your-repo-url>
cd asprams

# Copy environment template
cp .env.example .env
# Edit .env with your actual Gemini API key (and optional Jira credentials)
```

### 2. Start the Backend

```bash
cd backend

# Create a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# Install dependencies (includes scikit-learn, numpy, pandas for ML)
pip install -r requirements.txt

# Start the API server
python main.py
# OR: uvicorn main:app --reload
```

**On first startup**, the ML model will:
- Generate 1000 synthetic projects
- Train Linear Regression on risk correlations
- Cache model to disk (`ml/pretrained/`)
- Ready for inference within ~30 seconds

The API will be available at **http://localhost:8000**
- Swagger UI: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### 3. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

The UI will be available at **http://localhost:5173**

---

## Selenium Test Design

The Selenium suite is best used for black-box validation of the user journey, including equivalence partitioning and boundary value analysis for:
- registration and login inputs
- project form fields such as team size, duration, budget, and description length
- MongoDB-backed history loading
- PDF export from the result card

White-box basis-path testing is not a good fit for Selenium alone because it depends on internal control-flow knowledge. For that, use backend unit/integration tests alongside the browser tests.

To run the Selenium suite in Edge headless mode:

```bash
Set-Location backend; $env:ASPRAMS_EDGE_DRIVER_PATH="C:\Users\vedan\Downloads\edgedriver_win64\msedgedriver.exe"; pytest -m slow tests/test_ui_edge.py -rs
```

## ✨ Key Features

- **🤖 Multi-Agent Negotiation** — Estimation Agent vs. Risk Analysis Agent engage in 1-5 rounds of negotiation via Gemini API
- **🧠 ML-Powered Risk Scoring** — Linear Regression model trained on 1000 synthetic projects predicts risk [0.0-1.0]
- **📊 14 Engineered Features** — Intelligent feature extraction from user inputs + agent outputs:
  - Effort density, schedule slack, team experience estimation
  - Scope change rate, requirement clarity, technical debt
  - Budget variance and affordability assessment
- **💬 Explainability Agent** — Gemini-powered synthesis of:
  - Executive summary for stakeholders
  - Top 3 risk drivers identified by agents
  - Specific, actionable mitigation recommendations
  - Confidence scoring of assessment
- **💰 Budget Analysis** — Track available vs. required budget, flag budget risk
- **📈 Comprehensive Results** — Single dashboard view showing:
  - Negotiation rounds with agent reasoning
  - ML risk level (LOW/MEDIUM/HIGH) with score
  - Risk drivers and mitigation strategies
  - Budget feasibility with variance
- **🔗 Jira Integration** — Auto-create Stories with risk assessment (optional)
- **🧪 Synthetic Data Training** — 1000+ realistic project scenarios with risk correlations

---

## ⚙️ Configuration

Create a `.env` file in the `asprams/` root based on `.env.example`:

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | ✅ Yes | Google Gemini API key |
| `GEMINI_MODEL` | No | Defaults to `gemini-1.5-flash` |
| `MAX_NEGOTIATION_ROUNDS` | No | Defaults to `5` |
| `JIRA_EMAIL` | Optional | Atlassian account email |
| `JIRA_API_TOKEN` | Optional | Jira API token |
| `JIRA_DOMAIN` | Optional | e.g. `yourcompany.atlassian.net` |
| `JIRA_PROJECT_KEY` | Optional | e.g. `PROJ` |
| `VITE_API_URL` | No | Backend URL, defaults to `http://localhost:8000` |

---

## 🤖 How the Multi-Agent System Works

```
  User Input (4 core fields + budget + hourly rates)
      │
      ├─────────────────────────────────┐
      │                                 │
      ▼                                 ▼
  Estimation Agent (Gemini)    [Feature Extraction]
  ──────────────────────────     14 ML features:
  "Optimistically, this project  • Effort & complexity
   needs ~24 person-weeks."      • Budget variance
                                  • Team experience
      │                           • Scope change rate
      ▼                           • Requirement clarity
  Risk Analysis Agent (Gemini)    • Tech debt, etc.
  ──────────────────────────      │
  "I see 3 key risks. I COUNTER   ▼
   with 31 person-weeks."    ML Risk Scoring
                             ──────────────
      │                       Linear Regression
      ▼                       Risk Score [0.0-1.0]
  Negotiation Loop (≤5 rounds)    ↓
  ──────────────────────────   Classification
  [ACCEPT or COUNTER?]        (LOW/MEDIUM/HIGH)
      │                           │
      ▼                           ▼
  Final Effort Agreed      Explainability Agent (Gemini)
                           ───────────────────────────────
                           • Executive summary
                           • Top 3 risk drivers
                           • Mitigation recommendations
                           • Confidence score
                                 │
                                 ▼
                           Budget Analysis
                           ───────────────
                           • Required vs. Available
                           • Budget risk flag
                           • Cost per person-week
                                 │
                                 ▼
                           Enhanced Response
```

### Agent Roles

| Agent | Persona | Strategy | Output |
|---|---|---|---|
| **Estimation Agent** | Optimistic planner | Minimizes effort, assumes smooth execution | Effort estimate |
| **Risk Analysis Agent** | Skeptical reviewer | Identifies risks, applies buffers | Risk-adjusted effort |
| **Explainability Agent** | Domain expert synthesizer | Converts agent reasoning + ML into actionable insights | Natural language explanation, recommendations |

---

## 🔗 API Reference

### `POST /analyze`

**Request:**
```json
{
  "description": "Build a real-time inventory management system with multi-warehouse support",
  "team_size": 8,
  "duration": 24,
  "complexity": "high",
  "available_budget": 200000.0,
  "hourly_rates": {
    "junior": 50.0,
    "mid": 80.0,
    "senior": 120.0
  }
}
```

**Response:**
```json
{
  "rounds": [
    {
      "round_number": 1,
      "estimation_agent": {
        "effort": 42.0,
        "decision": "COUNTER",
        "reason": "Assuming smooth development and team proficiency..."
      },
      "risk_agent": {
        "effort": 52.5,
        "decision": "COUNTER",
        "reason": "Integration complexity, team ramp-up, requirement clarity concerns..."
      }
    },
    {
      "round_number": 2,
      "estimation_agent": {
        "effort": 47.0,
        "decision": "COUNTER",
        "reason": "Revising estimate to account for identified risks..."
      },
      "risk_agent": {
        "effort": 47.0,
        "decision": "ACCEPT",
        "reason": "Estimate now adequately covers identified risks."
      }
    }
  ],
  "final_effort": 47.0,
  "converged": true,
  "risk_assessment": {
    "ml_risk_score": 0.58,
    "risk_level": "MEDIUM",
    "budget_risk": false,
    "explainability": {
      "executive_summary": "The 47 person-week estimate adequately accounts for technical integration risks and team ramp-up. Project is feasible within the 24-week timeline with medium risk.",
      "risk_drivers": [
        "Integration complexity with 3 external APIs",
        "Team scaling from 5 to 8 developers mid-project",
        "Requirement clarity gaps in reporting module"
      ],
      "mitigation_recommendations": [
        "Conduct 2-week API integration spike before full development",
        "Implement phased team onboarding with pair programming",
        "Schedule requirements workshop with stakeholders by week 2"
      ],
      "confidence": 0.82,
      "negotiation_insight": "Agents converged after 2 rounds, indicating good estimate agreement..."
    },
    "budget_analysis": {
      "available_budget": 200000.0,
      "required_budget": 282000.0,
      "budget_variance": -0.41,
      "is_affordable": false,
      "cost_per_personweek": 6000.0
    }
  },
  "jira_issue_key": "PROJ-42"
}
```

### `GET /health`

```json
{ "status": "ok", "service": "ASPRAMS API", "timestamp": "2026-01-01T00:00:00Z" }
```

---

## � User Interface

### Input Form (Left Panel)
The form collects:
- **Project Description** — Scope, technologies, goals (min 10 chars)
- **Team Size** — Number of developers (1-100)
- **Duration** — Planned timeline in weeks (1-365)
- **Complexity** — Subjective level (Low/Medium/High/Critical)
- **Available Budget** — Total project budget in USD (min $1,000)
- **Hourly Rates** — Configurable rates by seniority (defaults: Junior $50, Mid $80, Senior $120)

### Results Dashboard (Right Panel)
Displays comprehensive assessment including:

**1. Negotiation Status**
- ✅ Consensus Reached / ⚠️ Max Rounds (convergence indicator)
- Final effort estimate in person-weeks (large, prominent)

**2. Risk Assessment** (powered by ML + Gemini)
- Risk Level indicator (🟢 LOW / 🟡 MEDIUM / 🔴 HIGH)
- ML Risk Score [0-100%] with visual progress bar
- Executive summary (2-3 sentences for stakeholders)
- Top 3 risk drivers identified by agents
- Recommended mitigation actions (specific, actionable)
- Assessment confidence [0-100%]

**3. Budget Analysis**
- Available Budget vs. Required Budget
- Cost per person-week
- Budget Status (✅ Affordable / ❌ Over Budget)
- Budget variance percentage

**4. Negotiation Timeline**
- Visual sequence of agent rounds
- Each agent's effort estimate and reasoning
- Convergence point (where Risk Agent ACCEPTs)

---

## �🏗️ Docker (Production)

```bash
# From asprams/ directory
docker build -t asprams .

docker run -p 8000:8000 \
  -e GEMINI_API_KEY=your_key \
  -e JIRA_EMAIL=your@email.com \
  -e JIRA_API_TOKEN=your_token \
  -e JIRA_DOMAIN=yourco.atlassian.net \
  -e JIRA_PROJECT_KEY=PROJ \
  asprams
```

---

## 🛠️ CI/CD Pipeline

The `.github/workflows/ci.yml` pipeline runs on every push to `main`:

1. **Setup** — Python 3.11 + Node.js 20
2. **Backend** — Install deps → lint with flake8 → run API integration tests
3. **Frontend** — Install deps → `npm run build` (Vite)
4. **All Clear** — Pipeline reports success

Add your secrets to GitHub: `Settings → Secrets → Actions`:
- `GEMINI_API_KEY`
- `JIRA_EMAIL`, `JIRA_API_TOKEN`, `JIRA_DOMAIN`, `JIRA_PROJECT_KEY`

---

## 🧠 Machine Learning Risk Model

### How It Works

1. **Synthetic Data Generation** — Generates 1000 realistic software projects with:
   - User inputs (team size, duration, complexity)
   - Derived metrics (effort density, schedule slack)
   - Risk factors (scope change, team experience, dependencies, requirement clarity, technical debt, etc.)
   - Synthesized risk scores [0.0-1.0] with realistic correlations

2. **Feature Engineering** — Extracts 14 features from each project:
   - **Direct inputs**: team_size, planned_duration, estimated_effort, complexity
   - **Derived ratios**: effort_density, schedule_slack, team_size_norm
   - **Estimated factors** (intelligent inference from agent outputs):
     - scope_change_rate (from Risk Agent's text mentions)
     - team_experience_months (from negotiation convergence speed)
     - external_dependencies (counted from reasoning)
     - requirement_clarity (inverse of negotiation rounds)
     - infrastructure_readiness (from effort feasibility)
     - technical_debt_score (based on complexity)
     - budget_variance (available vs. required)

3. **Model Training** — Trains Linear Regression on synthetic data:
   - Interpretable coefficients show feature impact
   - Auto-trains on startup if pretrained model missing
   - Persisted to disk for fast inference (<1s)

4. **Risk Scoring** → **Categorization**:
   - Continuous score [0.0 - 1.0]
   - **LOW**: < 0.33
   - **MEDIUM**: 0.33 - 0.66
   - **HIGH**: > 0.66

### Why Linear Regression?

✅ **Interpretable** — Coefficients directly show which features increase/decrease risk
✅ **Fast** — Inference in milliseconds
✅ **Explainable** — Feature importance enables transparency
✅ **Sufficient** — Handles realistic correlations between project factors
✅ **Lightweight** — No heavy dependencies or GPU needed

---

## 🔗 Jira Integration

When Jira credentials are configured, ASPRAMS automatically creates a **Jira Story** after each simulation containing:
- Project description, team size, duration, complexity
- Final agreed effort estimate
- Risk agent reasoning
- ML risk score and level
- Mitigation recommendations
- Simulation convergence status

Issue labels: `asprams`, `risk-assessment`, `automated`

---

## ✅ Running Tests

```bash
cd backend

# Install test dependencies
pip install -r requirements.txt

# Run integration tests
pytest tests/ -v
```

---

## 🚀 Deployment Checklist

- [ ] Set `GEMINI_API_KEY` in production environment
- [ ] Optionally configure Jira: `JIRA_EMAIL`, `JIRA_API_TOKEN`, `JIRA_DOMAIN`, `JIRA_PROJECT_KEY`
- [ ] Set `VITE_API_URL` on frontend (if backend not on same machine)
- [ ] Backend startup will auto-train ML model on first run (~30s)
- [ ] Verify health check: `curl http://localhost:8000/health`
- [ ] Test /docs endpoint for Swagger UI

---

## 📚 Example Workflow

1. **Start the system** (backend + frontend)
2. **Fill project details** in the form:
   - Description: "Mobile banking app with OAuth2, real-time notifications, multi-currency support"
   - Team: 6 developers
   - Duration: 20 weeks
   - Complexity: High
   - Budget: $150,000
3. **Click "Run Simulation"** → Agents negotiate via Gemini
4. **Review results**:
   - "Agents agreed on 45 person-weeks after 2 rounds"
   - "ML Risk Score: 72% (HIGH) due to integration complexity and unclear requirements"
   - "Required Budget: $270K (we have $150K) — over budget by $120K"
   - "Mitigations: Prioritize OAuth integration, lock requirements early, plan incremental delivery"
5. **Export to Jira** (if configured) — Story automatically created with all details

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'google'` | Run `pip install -r requirements.txt` in backend directory |
| ML model takes too long to train | First run generates + trains on 1000 projects. Subsequent runs load cached model (<1s) |
| Gemini API errors | Verify `GEMINI_API_KEY` in `.env` and has sufficient quota |
| Frontend can't reach backend | Check `VITE_API_URL` env var matches backend URL (default `http://localhost:8000`) |
| Jira integration not working | Verify Jira credentials are complete and API token has project write permissions |
| Budget shows as "Over Budget" | This is intentional — alerts users when available budget < estimated cost. Plan accordingly |

---

## 📄 License

MIT License — free to use and modify.
