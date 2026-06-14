# Universal Analytics Platform Master Roadmap

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement each phase plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver the confirmed universal AI analytics platform as seven independently testable phases without replacing real analysis behavior with simulated UI.

**Architecture:** The product keeps Next.js and FastAPI, then introduces a PostgreSQL metadata layer, Redis-backed workers, a model plugin registry, and artifact storage. Each phase ends in runnable software and a documented verification checkpoint; later phases extend stable interfaces from earlier phases instead of rewriting them.

**Tech Stack:** Next.js 16, React 19, TypeScript, Tailwind CSS, shadcn/ui primitives, Motion, FastAPI, PostgreSQL, Redis, pandas, scipy, scikit-learn, statsmodels, Plotly, Matplotlib, XGBoost, LightGBM, CatBoost, Prophet, TensorFlow, PyTorch, Docker Compose.

---

## Working Rules

- Preserve every existing dirty-worktree change unless the task explicitly replaces that code.
- Stage and commit only files named by the active task.
- Run the active phase's focused tests before its full regression suite.
- Update `README.md` and `PROGRESS.md` at every phase boundary.
- Do not expose a model as executable unless the capability API confirms its dependency group is installed.
- Do not display fake progress. Before the worker phase lands, existing synchronous API states remain explicit.
- Do not claim production readiness until Phase G passes.

## Phase Order

### Phase A: Product Interface and Theme System

Plan: `docs/superpowers/plans/2026-06-15-phase-a-product-interface.md`

Delivers:

- Data Lens marketing hero with a guaranteed two-line title.
- Desktop-tool workspace shell and mobile navigation.
- Progressive result hierarchy and contextual detail panel.
- Ten semantic color themes.
- Reusable reduced-motion-aware transitions.
- UI component tests, production build, desktop and mobile browser verification.

Exit command:

```bash
cd frontend
npm run test
npm run typecheck
npm run build
```

### Phase B: Persistent Job Infrastructure

Plan filename: `docs/superpowers/plans/2026-06-15-phase-b-job-infrastructure.md`

Delivers:

- PostgreSQL entities and migrations.
- Redis queue and Core Worker.
- Dataset, job, event, capability, artifact repositories.
- SSE progress with polling recovery.
- Docker Compose services for frontend, API, worker, PostgreSQL, and Redis.
- Cancellation, retry, timeout, and interrupted-job recovery.

Primary verification:

```bash
docker compose up -d postgres redis
cd backend
pytest tests/jobs tests/database tests/api/test_analysis_jobs.py -q
```

### Phase C: Universal Dataset Understanding

Plan filename: `docs/superpowers/plans/2026-06-15-phase-c-dataset-understanding.md`

Delivers:

- CSV, Excel, JSON, and NDJSON readers.
- Multi-sheet selection and nested JSON flattening.
- Schema, missing, duplicate, outlier, imbalance, constant, and high-cardinality profiling.
- Domain classification with evidence and confidence.
- Multi-path task recommendations.
- Merge preview, join-key candidates, type-conflict warnings, and real merge jobs.

Primary verification:

```bash
cd backend
pytest tests/datasets tests/profiling tests/recommendation -q
```

### Phase D: Model Registry and Traditional AutoML

Plan filename: `docs/superpowers/plans/2026-06-15-phase-d-model-registry-automl.md`

Delivers:

- Unified plugin interface and capability API.
- Regression, classification, clustering, anomaly detection, and PCA plugins.
- Leak-safe preprocessing pipelines.
- Fast, balanced, and deep search budgets.
- Manual parameters, feature selection, split, seed, scaling, encoding, cross-validation, and metric controls.
- Real model ranking, explanation, and artifact persistence.

Primary verification:

```bash
cd backend
pytest tests/ml/registry tests/ml/pipelines tests/ml/integration -q
```

### Phase E: Time Series and Heavy Workers

Plan filename: `docs/superpowers/plans/2026-06-15-phase-e-timeseries-heavy-models.md`

Delivers:

- Moving Average, Exponential Smoothing, ARIMA, SARIMA, and Prophet.
- TensorFlow LSTM and GRU.
- PyTorch LSTM and GRU.
- Heavy Worker dependency image and resource routing.
- Time-order validation, forecast windows, and MAE/RMSE/MAPE evaluation.

Primary verification:

```bash
cd backend
pytest tests/ml/timeseries tests/ml/deep_learning -q
```

### Phase F: Visualization, Statistics, Reports, and Artifacts

Plan filename: `docs/superpowers/plans/2026-06-15-phase-f-visualization-reports.md`

Delivers:

- Automatic and manual Plotly chart builder.
- Matplotlib PNG rendering.
- Correlation, T-test, ANOVA, Chi-square, A/B testing, effect size, and limitations.
- PDF, HTML, DOCX, Python, notebook, CSV, XLSX, PNG, and trained-model artifacts.
- In-product code and report previews.

Primary verification:

```bash
cd backend
pytest tests/charts tests/statistics tests/reports tests/artifacts -q
```

### Phase G: End-to-End Acceptance and Documentation

Plan filename: `docs/superpowers/plans/2026-06-15-phase-g-acceptance.md`

Delivers:

- Finance, housing, medical/classification, sports/business clustering, dirty-table, and nested-JSON end-to-end fixtures.
- Full capability audit proving visible models are executable.
- Desktop, tablet, mobile, keyboard, reduced-motion, and theme verification.
- Production Docker build.
- Final README, PROGRESS, demo flow, known issues, and launch checklist.

Primary verification:

```bash
docker compose up --build -d
pytest backend/tests/e2e -q
cd frontend
npm run test
npm run typecheck
npm run build
```

## Phase Dependency Graph

```text
Phase A UI foundation
        |
Phase B job infrastructure
        |
Phase C dataset understanding
        |
Phase D traditional AutoML
        |
Phase E heavy/time-series models
        |
Phase F charts/reports/artifacts
        |
Phase G full acceptance
```

Phase A can ship independently because it preserves the current real APIs. Phases B–F are sequential because each adds stable backend contracts consumed by the following phase.

## Commit Strategy

- Phase A uses small UI commits after theme, hero, shell, dashboard, and verification tasks.
- Phase B commits database, queue, API, and Docker changes separately.
- Phase C commits readers, profiler, recommender, and merge flow separately.
- Phase D commits registry contracts before individual plugin groups.
- Phase E commits statistical time-series plugins before deep-learning workers.
- Phase F commits charts, statistics, reports, and exports separately.
- Phase G commits test fixtures, fixes, and documentation separately.

## Final Definition of Done

- Every visible result comes from a real backend computation.
- Different datasets produce different domain, task, model, chart, and next-step recommendations.
- All listed executable models train through the common job system.
- Missing dependencies and incompatible data produce structured, actionable errors.
- The Hero never breaks beyond two lines.
- Ten themes remain readable across supported viewports.
- The workspace remains usable with keyboard, touch, and reduced motion.
- Production builds and all phase suites pass.
