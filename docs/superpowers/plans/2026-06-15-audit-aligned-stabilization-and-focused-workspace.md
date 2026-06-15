# Audit-Aligned Stabilization and Focused Workspace Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修正一致性稽核列出的立即風險，並將模型分析頁改成已確認的 A「聚焦流程台」，讓產品保持封閉測試定位、產物不再由公開靜態目錄直出、配色立即生效、文字清楚可讀且分析流程只呈現真實後端狀態。

**Architecture:** 這一批不建立完整多租戶 SaaS，也不假裝已完成 Project ownership。後端先以短效 HMAC capability URL 取代 `/generated_outputs/*` 公開靜態掛載，作為 Phase B 前的封閉測試防護；前端拆出小型分析流程元件，由 `ModelAnalysisPanel` 保留資料與 API 協調責任。完整 PostgreSQL、Analysis Run、Run Manifest、auth、Redis Worker 與 SSE 必須另立 Phase B 計畫。

**Tech Stack:** Next.js 16 App Router、React 19、TypeScript、Tailwind CSS、shadcn/ui、Motion、Vitest、Testing Library、FastAPI、Pydantic、pytest、HMAC SHA-256。

---

## Scope Boundary

本計畫實作稽核報告的：

- 立即 0–3 天修正。
- C1 公開靜態產物的封閉測試緩解。
- C2 部署定位誠實化。
- M3 重複主要操作收斂。
- M6 Docker Node 版本一致。
- 已確認 A 工作區中的可讀性、資訊層級、真實進度與程式碼預覽。

本計畫不宣稱解決：

- 多租戶身份與 Project ownership。
- PostgreSQL domain model。
- immutable Analysis Run 與 Manifest。
- Redis queue、獨立 Worker、retry、restart recovery、SSE。
- 完整資料品質、可信模型評估與 Join／Append preview。

上述項目在本計畫通過後進入獨立的 Phase B implementation plan。

## File Map

### 新增

- `backend/app/services/artifact_access.py`：建立及驗證短效 artifact capability token。
- `backend/tests/test_artifact_access.py`：驗證過期、竄改、路徑逃逸與下載 endpoint。
- `frontend/src/components/EnvironmentNotice.tsx`：封閉測試與敏感資料警示。
- `frontend/src/components/analysis/AnalysisStepRail.tsx`：四步分析狀態。
- `frontend/src/components/analysis/AnalysisModeSelector.tsx`：自動／迴歸／分類模式選擇。
- `frontend/src/components/analysis/DatasetMetricStrip.tsx`：緊湊資料摘要。
- `frontend/src/components/analysis/AnalysisRecommendationPanel.tsx`：由真實 dataset profile 推導的建議理由。
- `frontend/src/components/analysis/ModelSelectionDrawer.tsx`：搜尋、篩選與手動模型選擇。
- `frontend/src/components/analysis/InlineCodeViewer.tsx`：Python／Notebook 分頁、行號與複製。
- `frontend/src/components/__tests__/EnvironmentNotice.test.tsx`
- `frontend/src/components/__tests__/AnalysisWorkspace.test.tsx`
- `frontend/src/components/__tests__/InlineCodeViewer.test.tsx`

### 修改

- `Dockerfile`
- `DEPLOYMENT.md`
- `README.md`
- `PROGRESS.md`
- `backend/app/main.py`
- `backend/app/services/code_generator.py`
- `backend/app/services/financial_analyzer.py`
- `backend/app/services/model_runner.py`
- `backend/app/services/report_generator.py`
- `backend/tests/test_api_hardening.py`
- `frontend/next.config.js`
- `frontend/src/app/product-interface.css`
- `frontend/src/app/product-motion.css`
- `frontend/src/components/AppShell.tsx`
- `frontend/src/components/MarketingShell.tsx`
- `frontend/src/components/MarketingHome.tsx`
- `frontend/src/components/ModelAnalysisPanel.tsx`
- `frontend/src/components/PagePrimitives.tsx`
- `frontend/src/components/ThemePicker.tsx`
- `frontend/src/components/ThemeProvider.tsx`
- `frontend/src/components/WorkspaceToolPages.tsx`
- `frontend/src/components/__tests__/SemanticColorUsage.test.ts`
- `frontend/src/components/__tests__/ThemePicker.test.tsx`
- `frontend/src/components/__tests__/ThemeProvider.test.tsx`

## Task 1: Lock the Closed-Beta Product Contract

**Files:**
- Create: `frontend/src/components/EnvironmentNotice.tsx`
- Create: `frontend/src/components/__tests__/EnvironmentNotice.test.tsx`
- Modify: `frontend/src/components/AppShell.tsx`
- Modify: `frontend/src/components/MarketingShell.tsx`
- Modify: `frontend/src/components/MarketingHome.tsx`
- Modify: `README.md`
- Modify: `DEPLOYMENT.md`
- Modify: `Dockerfile`

- [ ] **Step 1: Write the failing product notice test**

```tsx
import { render, screen } from "@testing-library/react";
import { LocaleProvider } from "@/components/LocaleProvider";
import { EnvironmentNotice } from "@/components/EnvironmentNotice";

it("states that the current environment is for closed testing and rejects sensitive data", () => {
  render(
    <LocaleProvider locale="zh-Hant">
      <EnvironmentNotice />
    </LocaleProvider>
  );

  expect(screen.getByRole("status")).toHaveTextContent("封閉測試");
  expect(screen.getByRole("status")).toHaveTextContent("請勿上傳敏感資料");
});
```

- [ ] **Step 2: Run the test and verify it fails**

Run:

```bash
cd frontend
npm run test:run -- EnvironmentNotice.test.tsx
```

Expected: FAIL because `EnvironmentNotice` does not exist.

- [ ] **Step 3: Implement the notice component**

```tsx
"use client";

import { ShieldAlert } from "lucide-react";
import { useLocale } from "@/components/LocaleProvider";

export function EnvironmentNotice() {
  const { text } = useLocale();

  return (
    <div className="environment-notice" role="status">
      <ShieldAlert aria-hidden="true" />
      <span>
        {text(
          "目前為封閉測試環境，請勿上傳個資、醫療、財務帳戶或其他敏感資料。",
          "Closed testing environment. Do not upload personal, medical, financial-account, or other sensitive data."
        )}
      </span>
    </div>
  );
}
```

- [ ] **Step 4: Mount the notice once in each product shell**

In `MarketingShell.tsx`, render it directly below the marketing header.  
In `AppShell.tsx`, render it below the product topbar and above routed content.

Do not repeat the notice inside each page.

- [ ] **Step 5: Remove duplicate primary actions**

In `AppShell.tsx`, keep the topbar `加入資料` action only when the current page has no page-level primary upload control.

In `WorkspaceEmptyState`, keep one primary button. Page headers must not render a second button that performs the same navigation.

Add an assertion to `AppShell.test.tsx`:

```tsx
expect(screen.getAllByRole("link", { name: "加入資料" })).toHaveLength(1);
```

- [ ] **Step 6: Correct deployment and product claims**

Change `DEPLOYMENT.md` heading to:

```markdown
# 封閉測試部署指南
```

Add this warning before deployment steps:

```markdown
> 目前架構不適合公開匿名上傳或敏感資料。部署用途限私人展示、封閉測試與非敏感樣本資料；正式多租戶 SaaS 仍需完成 PostgreSQL、身份授權、私人產物、Redis Worker、retention 與 rate limit。
```

Update README phrases:

- Replace 「正式雲端部署」 with 「封閉測試雲端部署」.
- Replace claims that imply full traceability with wording limited to current generated files and local workspace persistence.
- State that IndexedDB persistence does not sync across devices.
- State that capability URLs introduced in Task 2 are temporary closed-beta protection, not tenant authorization.

- [ ] **Step 7: Align Docker Node version**

Change both Node stages in `Dockerfile`:

```dockerfile
FROM node:22-bookworm-slim AS frontend-builder
FROM node:22-bookworm-slim AS runner
```

Keep the existing commands between the two `FROM` declarations unchanged.

- [ ] **Step 8: Run focused checks**

Run:

```bash
cd frontend
npm run test:run -- EnvironmentNotice.test.tsx AppShell.test.tsx MarketingShell.test.tsx
```

Expected: PASS.

Run:

```bash
rg -n "正式部署指南|建議正式部署方式|正式雲端部署" README.md DEPLOYMENT.md
```

Expected: no matches.

- [ ] **Step 9: Commit**

```bash
git add Dockerfile DEPLOYMENT.md README.md \
  frontend/src/components/EnvironmentNotice.tsx \
  frontend/src/components/AppShell.tsx \
  frontend/src/components/MarketingShell.tsx \
  frontend/src/components/MarketingHome.tsx \
  frontend/src/components/PagePrimitives.tsx \
  frontend/src/components/__tests__/EnvironmentNotice.test.tsx \
  frontend/src/components/__tests__/AppShell.test.tsx \
  frontend/src/components/__tests__/MarketingShell.test.tsx
git commit -m "fix: label the app as a closed testing environment"
```

## Task 2: Replace Public Static Artifacts with Expiring Capability URLs

**Files:**
- Create: `backend/app/services/artifact_access.py`
- Create: `backend/tests/test_artifact_access.py`
- Modify: `backend/app/main.py`
- Modify: `backend/app/services/code_generator.py`
- Modify: `backend/app/services/financial_analyzer.py`
- Modify: `backend/app/services/model_runner.py`
- Modify: `backend/app/services/report_generator.py`
- Modify: `frontend/next.config.js`
- Modify: `backend/tests/test_analysis_jobs.py`

- [ ] **Step 1: Write failing artifact token tests**

```python
from pathlib import Path

import pytest
from fastapi import HTTPException

from app.services.artifact_access import create_artifact_url, resolve_artifact_token


def test_artifact_token_resolves_only_inside_generated_outputs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "generated_outputs"
    file_path = root / "charts" / "result.png"
    file_path.parent.mkdir(parents=True)
    file_path.write_bytes(b"png")
    monkeypatch.setenv("ARTIFACT_SIGNING_SECRET", "test-secret")

    url = create_artifact_url(file_path, root=root, now=1_000, ttl_seconds=60)
    token = url.rsplit("/", 1)[-1]

    assert resolve_artifact_token(token, root=root, now=1_030) == file_path


def test_artifact_token_rejects_tampering_and_expiry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "generated_outputs"
    file_path = root / "data" / "clean.csv"
    file_path.parent.mkdir(parents=True)
    file_path.write_text("a\n1\n", encoding="utf-8")
    monkeypatch.setenv("ARTIFACT_SIGNING_SECRET", "test-secret")
    token = create_artifact_url(file_path, root=root, now=1_000, ttl_seconds=10).rsplit("/", 1)[-1]

    with pytest.raises(HTTPException) as tampered:
        resolve_artifact_token(f"{token}x", root=root, now=1_005)
    assert tampered.value.status_code == 403

    with pytest.raises(HTTPException) as expired:
        resolve_artifact_token(token, root=root, now=1_011)
    assert expired.value.status_code == 410
```

- [ ] **Step 2: Run tests and verify failure**

```bash
cd backend
pytest tests/test_artifact_access.py -q
```

Expected: collection FAIL because `artifact_access` does not exist.

- [ ] **Step 3: Implement artifact signing and resolution**

Create `backend/app/services/artifact_access.py`:

```python
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from pathlib import Path

from fastapi import HTTPException

DEFAULT_TTL_SECONDS = 60 * 30
_PROCESS_SECRET = secrets.token_bytes(32)


def create_artifact_url(
    path: Path,
    *,
    root: Path,
    now: int | None = None,
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
) -> str:
    resolved_root = root.resolve()
    resolved_path = path.resolve()
    try:
        relative_path = resolved_path.relative_to(resolved_root)
    except ValueError as error:
        raise ValueError("Artifact must be inside generated_outputs.") from error

    payload = {
        "path": relative_path.as_posix(),
        "exp": int(time.time() if now is None else now) + ttl_seconds,
    }
    encoded = _encode(json.dumps(payload, separators=(",", ":")).encode())
    signature = hmac.new(_secret(), encoded.encode(), hashlib.sha256).digest()
    return f"/api/artifacts/{encoded}.{_encode(signature)}"


def resolve_artifact_token(
    token: str,
    *,
    root: Path,
    now: int | None = None,
) -> Path:
    try:
        encoded, supplied_signature = token.split(".", 1)
        expected_signature = _encode(
            hmac.new(_secret(), encoded.encode(), hashlib.sha256).digest()
        )
        if not hmac.compare_digest(supplied_signature, expected_signature):
            raise HTTPException(status_code=403, detail="產物連結無效。")
        payload = json.loads(_decode(encoded))
        if int(payload["exp"]) < int(time.time() if now is None else now):
            raise HTTPException(status_code=410, detail="產物連結已過期。")
        resolved_root = root.resolve()
        resolved_path = (resolved_root / str(payload["path"])).resolve()
        resolved_path.relative_to(resolved_root)
    except HTTPException:
        raise
    except (ValueError, KeyError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=403, detail="產物連結無效。") from error

    if not resolved_path.is_file():
        raise HTTPException(status_code=404, detail="找不到產物檔案。")
    return resolved_path


def _secret() -> bytes:
    value = os.getenv("ARTIFACT_SIGNING_SECRET", "").strip()
    return value.encode() if value else _PROCESS_SECRET


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
```

- [ ] **Step 4: Add protected download endpoint and remove StaticFiles**

In `backend/app/main.py`:

```python
from fastapi.responses import FileResponse, JSONResponse
from app.services.artifact_access import resolve_artifact_token
```

Add:

```python
@app.get("/api/artifacts/{token}")
async def download_artifact(token: str) -> FileResponse:
    artifact_path = resolve_artifact_token(token, root=GENERATED_OUTPUTS_DIR)
    return FileResponse(
        artifact_path,
        filename=artifact_path.name,
        headers={"Cache-Control": "private, no-store"},
    )
```

Delete the `from fastapi.staticfiles import StaticFiles` import and the final
`app.mount("/generated_outputs", StaticFiles(directory=GENERATED_OUTPUTS_DIR), name="generated_outputs")`
statement.

- [ ] **Step 5: Generate signed URLs at artifact creation**

In each generator service import:

```python
from app.services.artifact_access import create_artifact_url
```

Replace the URL construction at:

- `code_generator.py` for `python_url` and `notebook_url`.
- `financial_analyzer.py` for `indicator_url` and every generated chart URL.
- `model_runner.py` for model, model results, cleaned dataset, primary chart, and chart collection URLs.
- `report_generator.py` for `report_url`.

Use:

```python
create_artifact_url(path, root=REPO_ROOT / "generated_outputs")
```

Use the exact generated `Path` object already returned by the service; do not rebuild paths from user input.

- [ ] **Step 6: Remove the public Next.js artifact rewrite**

Delete this rewrite from `frontend/next.config.js`:

```js
{
  source: "/generated_outputs/:path*",
  destination: `${internalApiBaseUrl}/generated_outputs/:path*`
}
```

The existing `/api/:path*` rewrite will proxy `/api/artifacts/:token`.

- [ ] **Step 7: Add endpoint assertions**

Add to `backend/tests/test_artifact_access.py`:

```python
from fastapi.testclient import TestClient
from app.main import GENERATED_OUTPUTS_DIR, app


def test_artifact_endpoint_requires_a_valid_capability_token(tmp_path: Path) -> None:
    response = TestClient(app).get("/api/artifacts/not-a-token")
    assert response.status_code == 403


def test_generated_outputs_is_no_longer_publicly_mounted() -> None:
    response = TestClient(app).get("/generated_outputs/charts/unknown.png")
    assert response.status_code == 404
```

Update `test_analysis_jobs.py` to assert:

```python
assert result["charts"][0]["chart_url"].startswith("/api/artifacts/")
assert result["model_results"][0]["model_url"].startswith("/api/artifacts/")
```

- [ ] **Step 8: Run backend tests**

```bash
cd backend
pytest tests/test_artifact_access.py tests/test_analysis_jobs.py tests/test_api_hardening.py -q
```

Expected: PASS.

- [ ] **Step 9: Commit**

```bash
git add backend/app/main.py backend/app/services/artifact_access.py \
  backend/app/services/code_generator.py \
  backend/app/services/financial_analyzer.py \
  backend/app/services/model_runner.py \
  backend/app/services/report_generator.py \
  backend/tests/test_artifact_access.py \
  backend/tests/test_analysis_jobs.py \
  frontend/next.config.js
git commit -m "fix: protect generated artifacts with expiring links"
```

## Task 3: Make Theme Selection Immediate and Text Colors Explicit

**Files:**
- Modify: `frontend/src/components/ThemeProvider.tsx`
- Modify: `frontend/src/components/ThemePicker.tsx`
- Modify: `frontend/src/components/__tests__/ThemeProvider.test.tsx`
- Modify: `frontend/src/components/__tests__/ThemePicker.test.tsx`
- Modify: `frontend/src/components/__tests__/SemanticColorUsage.test.ts`
- Modify: `frontend/src/app/product-interface.css`

- [ ] **Step 1: Replace preview/apply tests with immediate-selection tests**

In `ThemeProvider.test.tsx`, replace preview-specific cases with:

```tsx
it("selects, applies, and persists a theme in one operation", async () => {
  const { result } = renderHook(() => useProductTheme(), { wrapper });
  await waitFor(() => expectRootTheme("mist"));

  act(() => result.current.selectTheme("deep-sea"));

  expect(result.current.appliedTheme).toBe("deep-sea");
  expect(window.localStorage.getItem(storageKey)).toBe("deep-sea");
  expectRootTheme("deep-sea");
});
```

In `ThemePicker.test.tsx`:

```tsx
it("applies and persists a theme immediately when clicked", async () => {
  const user = userEvent.setup();
  renderPicker();

  await user.click(screen.getByRole("button", { name: "配色" }));
  await user.click(screen.getByRole("radio", { name: /Deep Sea 深色/ }));

  expect(document.documentElement.dataset.productTheme).toBe("deep-sea");
  expect(localStorage.getItem("finai-product-theme-v1")).toBe("deep-sea");
  expect(screen.queryByText("套用")).not.toBeInTheDocument();
  expect(screen.queryByText("取消")).not.toBeInTheDocument();
});
```

- [ ] **Step 2: Run tests and verify failure**

```bash
cd frontend
npm run test:run -- ThemeProvider.test.tsx ThemePicker.test.tsx
```

Expected: FAIL because `selectTheme` does not exist and Apply/Cancel still render.

- [ ] **Step 3: Simplify ThemeProvider**

Change the context type to:

```tsx
type ThemeContextValue = {
  appliedTheme: ThemeId;
  selectTheme: (theme: ThemeId) => void;
};
```

Implement:

```tsx
const selectTheme = useCallback((theme: ThemeId) => {
  const nextTheme = getTheme(theme).id;
  setAppliedTheme(nextTheme);
  applyThemeToRoot(nextTheme);
  try {
    window.localStorage.setItem(storageKey, nextTheme);
  } catch {
    // The current page theme still changes when persistence is unavailable.
  }
}, []);
```

Remove preview refs, preview state, `applyPreview`, and `cancelPreview`.

- [ ] **Step 4: Simplify ThemePicker**

Use:

```tsx
const { appliedTheme, selectTheme } = useProductTheme();
```

On option click:

```tsx
onClick={() => {
  selectTheme(theme.id);
  setOpen(false);
}}
```

Remove `theme-picker-actions`, Apply, Cancel, preview copy, and intentional-close refs.

Arrow keys only move focus. Enter and Space use the button's native click to select.

- [ ] **Step 5: Add explicit semantic text classes**

Add to `product-interface.css`:

```css
.ui-copy-primary {
  color: var(--product-text-primary) !important;
  opacity: 1 !important;
}

.ui-copy-secondary,
.ui-metric-label,
.ui-option-description {
  color: var(--product-text-secondary) !important;
  opacity: 1 !important;
}

.ui-copy-tertiary {
  color: color-mix(
    in srgb,
    var(--product-text-secondary) 88%,
    var(--product-text-primary)
  ) !important;
  opacity: 1 !important;
}
```

Add defensive form rules:

```css
.product-shell label,
.product-shell legend,
.product-shell dt,
.product-shell small,
.product-shell p {
  text-shadow: none;
}
```

Do not use opacity to represent secondary text.

- [ ] **Step 6: Strengthen semantic color tests**

Add:

```ts
expect(source).toMatch(/\.ui-option-description[\s\S]*opacity:\s*1\s*!important/);
expect(source).toMatch(/\.ui-metric-label[\s\S]*var\(--product-text-secondary\)/);
```

Also scan `ModelAnalysisPanel.tsx`, `FinancialAnalysisPanel.tsx`, and `AgentReportPanel.tsx` for `text-white/` or opacity-based text utilities on light surfaces.

- [ ] **Step 7: Run tests**

```bash
cd frontend
npm run test:run -- ThemeProvider.test.tsx ThemePicker.test.tsx SemanticColorUsage.test.ts
```

Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add frontend/src/components/ThemeProvider.tsx \
  frontend/src/components/ThemePicker.tsx \
  frontend/src/components/__tests__/ThemeProvider.test.tsx \
  frontend/src/components/__tests__/ThemePicker.test.tsx \
  frontend/src/components/__tests__/SemanticColorUsage.test.ts \
  frontend/src/app/product-interface.css
git commit -m "fix: apply themes immediately with readable semantic text"
```

## Task 4: Build the Focused Analysis Workspace Components

**Files:**
- Create: `frontend/src/components/analysis/AnalysisStepRail.tsx`
- Create: `frontend/src/components/analysis/AnalysisModeSelector.tsx`
- Create: `frontend/src/components/analysis/DatasetMetricStrip.tsx`
- Create: `frontend/src/components/analysis/AnalysisRecommendationPanel.tsx`
- Create: `frontend/src/components/analysis/ModelSelectionDrawer.tsx`
- Create: `frontend/src/components/__tests__/AnalysisWorkspace.test.tsx`
- Modify: `frontend/src/app/product-interface.css`
- Modify: `frontend/src/app/product-motion.css`

- [ ] **Step 1: Write failing component tests**

```tsx
it("shows one active step and exposes status without relying on color", () => {
  render(<AnalysisStepRail current="method" />);
  expect(screen.getByText("選擇方法").closest("li")).toHaveAttribute(
    "aria-current",
    "step"
  );
  expect(screen.getByText("資料理解").closest("li")).toHaveTextContent("完成");
});

it("uses real radio controls for analysis modes", async () => {
  const onChange = vi.fn();
  render(<AnalysisModeSelector value="auto" onChange={onChange} />);
  await userEvent.click(screen.getByRole("radio", { name: /迴歸分析/ }));
  expect(onChange).toHaveBeenCalledWith("regression");
});

it("derives recommendation copy from the dataset profile", () => {
  render(
    <AnalysisRecommendationPanel
      dataset={datasetWithMissingValues}
      targetColumn="price"
      analysisMode="auto"
      availableModelCount={8}
    />
  );
  expect(screen.getByText(/連續數值/)).toBeInTheDocument();
  expect(screen.getByText(/缺失/)).toBeInTheDocument();
});
```

- [ ] **Step 2: Run tests and verify failure**

```bash
cd frontend
npm run test:run -- AnalysisWorkspace.test.tsx
```

Expected: FAIL because the analysis components do not exist.

- [ ] **Step 3: Implement AnalysisStepRail**

Use this public API:

```tsx
export type AnalysisWorkspaceStep = "data" | "method" | "running" | "result";

export function AnalysisStepRail({
  current
}: {
  current: AnalysisWorkspaceStep;
}) {
  const { text } = useLocale();
  const orderedSteps: Array<{
    id: AnalysisWorkspaceStep;
    zh: string;
    en: string;
  }> = [
    { id: "data", zh: "資料理解", en: "Understand data" },
    { id: "method", zh: "選擇方法", en: "Choose method" },
    { id: "running", zh: "執行分析", en: "Run analysis" },
    { id: "result", zh: "整理結果", en: "Review results" }
  ];
  const activeIndex = orderedSteps.findIndex((step) => step.id === current);

  return (
    <ol className="analysis-step-rail" aria-label={text("分析流程", "Analysis flow")}>
      {orderedSteps.map((step, index) => {
        const status =
          index < activeIndex ? "done" : index === activeIndex ? "active" : "pending";
        return (
          <li
            key={step.id}
            className={`is-${status}`}
            aria-current={status === "active" ? "step" : undefined}
          >
            <span className="analysis-step-index" aria-hidden="true">
              {status === "done" ? <Check /> : index + 1}
            </span>
            <span>{text(step.zh, step.en)}</span>
            <span className="sr-only">
              {status === "done"
                ? text("完成", "Complete")
                : status === "active"
                  ? text("目前步驟", "Current step")
                  : text("尚未開始", "Not started")}
            </span>
          </li>
        );
      })}
    </ol>
  );
}
```

Each item must include visually hidden state text:

```tsx
<span className="sr-only">
  {status === "done" ? text("完成", "Complete") : status === "active" ? text("目前步驟", "Current step") : text("尚未開始", "Not started")}
</span>
```

- [ ] **Step 4: Implement AnalysisModeSelector**

Public API:

```tsx
type AnalysisMode = "auto" | "regression" | "classification";

export function AnalysisModeSelector({
  value,
  onChange
}: {
  value: AnalysisMode;
  onChange: (value: AnalysisMode) => void;
}) {
  const { text } = useLocale();
  const modes = [
    {
      value: "auto" as const,
      label: text("自動選擇", "Automatic"),
      description: text(
        "依目標欄位型態與資料規模選擇候選模型。",
        "Select candidate models from target type and dataset size."
      )
    },
    {
      value: "regression" as const,
      label: text("迴歸分析", "Regression"),
      description: text(
        "預測價格、銷售額或其他連續數值。",
        "Predict prices, sales, or other continuous values."
      )
    },
    {
      value: "classification" as const,
      label: text("分類分析", "Classification"),
      description: text(
        "預測類別、狀態或事件是否發生。",
        "Predict categories, states, or event outcomes."
      )
    }
  ];

  return (
    <fieldset>
      <legend>{text("分析模式", "Analysis mode")}</legend>
      <div className="analysis-mode-grid">
        {modes.map((mode) => (
          <label
            key={mode.value}
            className={`${value === mode.value ? "is-selected" : ""} ${
              mode.value === "auto" ? "is-recommended" : ""
            }`}
          >
            <input
              type="radio"
              name="analysis-mode"
              value={mode.value}
              checked={value === mode.value}
              onChange={() => onChange(mode.value)}
            />
            <strong>{mode.label}</strong>
            <span className="ui-option-description">{mode.description}</span>
          </label>
        ))}
      </div>
    </fieldset>
  );
}
```

Apply `ui-option-description` to every description. The auto option receives `is-recommended`, but all three remain equal native radio controls.

- [ ] **Step 5: Implement DatasetMetricStrip**

Public API:

```tsx
export function DatasetMetricStrip({
  rows,
  features,
  models
}: {
  rows: number;
  features: number;
  models: number;
}) {
  const { text } = useLocale();
  const metrics = [
    { label: text("資料列", "Rows"), value: rows },
    { label: text("特徵欄位", "Features"), value: features },
    { label: text("可用模型", "Available models"), value: models }
  ];

  return (
    <dl className="dataset-metric-strip">
      {metrics.map((metric) => (
        <div key={metric.label}>
          <dt className="ui-metric-label">{metric.label}</dt>
          <dd>{metric.value.toLocaleString()}</dd>
        </div>
      ))}
    </dl>
  );
}
```

Use `ui-metric-label` for `dt`. Do not render three independent cards.

- [ ] **Step 6: Implement AnalysisRecommendationPanel**

Compute deterministic reasons only from:

- `dataset.data_types[targetColumn]`
- `dataset.row_count`
- `dataset.missing_values`
- `dataset.recommended_target_columns`
- `analysisMode`
- `availableModelCount`

Rules:

```ts
const targetType = dataset.data_types[targetColumn] ?? "";
const numericTarget = /int|float|double|decimal/i.test(targetType);
const missingCells = Object.values(dataset.missing_values).reduce(
  (sum, value) => sum + value,
  0
);
```

Never claim correlation, leakage, imbalance, or outliers because the current backend does not provide them.

- [ ] **Step 7: Implement ModelSelectionDrawer**

Public API:

```tsx
type ModelOption = {
  key: string;
  label: string;
  problemType: "regression" | "classification";
  description: string;
};

export function ModelSelectionDrawer({
  open,
  options,
  selected,
  onToggle,
  onClear
}: {
  open: boolean;
  options: ModelOption[];
  selected: string[];
  onToggle: (key: string) => void;
  onClear: () => void;
}) {
  const { text } = useLocale();
  const reducedMotion = useReducedMotion();
  const [query, setQuery] = useState("");
  const [family, setFamily] = useState<"all" | "regression" | "classification">("all");
  const visibleOptions = options.filter((option) => {
    const matchesFamily = family === "all" || option.problemType === family;
    const normalizedQuery = query.trim().toLocaleLowerCase();
    const matchesQuery =
      !normalizedQuery ||
      option.label.toLocaleLowerCase().includes(normalizedQuery) ||
      option.description.toLocaleLowerCase().includes(normalizedQuery);
    return matchesFamily && matchesQuery;
  });

  return (
    <AnimatePresence initial={false}>
      {open ? (
        <motion.section
          className="model-selection-drawer"
          initial={reducedMotion ? false : { opacity: 0, transform: "translate3d(0,-6px,0)" }}
          animate={{ opacity: 1, transform: "translate3d(0,0,0)" }}
          exit={{ opacity: 0, transform: reducedMotion ? "none" : "translate3d(0,-4px,0)" }}
          transition={{ duration: reducedMotion ? 0 : 0.2 }}
          aria-label={text("手動選擇模型", "Choose models manually")}
        >
          <div className="model-selection-toolbar">
            <label>
              <span className="sr-only">{text("搜尋模型", "Search models")}</span>
              <input
                type="search"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder={text("搜尋模型", "Search models")}
              />
            </label>
            <div role="group" aria-label={text("模型類型", "Model type")}>
              {(["all", "regression", "classification"] as const).map((value) => (
                <button
                  key={value}
                  type="button"
                  aria-pressed={family === value}
                  onClick={() => setFamily(value)}
                >
                  {value === "all"
                    ? text("全部", "All")
                    : value === "regression"
                      ? text("回歸", "Regression")
                      : text("分類", "Classification")}
                </button>
              ))}
            </div>
            <button type="button" onClick={onClear} disabled={selected.length === 0}>
              {text("清除選擇", "Clear selection")}
            </button>
          </div>
          <p className="ui-copy-secondary">
            {text(`已選 ${selected.length} 個模型`, `${selected.length} models selected`)}
          </p>
          <div className="model-selection-options">
            {visibleOptions.map((option) => (
              <label key={option.key}>
                <input
                  type="checkbox"
                  checked={selected.includes(option.key)}
                  onChange={() => onToggle(option.key)}
                />
                <span>
                  <strong>{option.label}</strong>
                  <small className="ui-option-description">{option.description}</small>
                </span>
              </label>
            ))}
          </div>
        </motion.section>
      ) : null}
    </AnimatePresence>
  );
}
```

The drawer stays in document flow. Animate only `height`, `opacity`, and `transform` through Motion; reduced motion renders immediately.

- [ ] **Step 8: Add workspace CSS**

Create named blocks:

```css
.analysis-focus-workspace {}
.analysis-step-rail {}
.analysis-focus-grid {}
.analysis-primary-stage {}
.analysis-recommendation-panel {}
.analysis-mode-grid {}
.dataset-metric-strip {}
.model-selection-drawer {}
.analysis-next-action {}
```

Desktop:

```css
.analysis-focus-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.55fr) minmax(260px, 0.72fr);
  gap: 18px;
}
```

At `max-width: 1024px`, move recommendation below the primary stage.  
At `max-width: 680px`, use one-column modes and 44px controls.

- [ ] **Step 9: Run component tests**

```bash
cd frontend
npm run test:run -- AnalysisWorkspace.test.tsx
```

Expected: PASS.

- [ ] **Step 10: Commit**

```bash
git add frontend/src/components/analysis \
  frontend/src/components/__tests__/AnalysisWorkspace.test.tsx \
  frontend/src/app/product-interface.css \
  frontend/src/app/product-motion.css
git commit -m "feat: add focused analysis workspace components"
```

## Task 5: Integrate the Focused Flow into ModelAnalysisPanel

**Files:**
- Modify: `frontend/src/components/ModelAnalysisPanel.tsx`
- Modify: `frontend/src/components/WorkspaceToolPages.tsx`
- Modify: `frontend/src/components/__tests__/AnalysisWorkspace.test.tsx`
- Modify: `frontend/src/app/product-interface.css`

- [ ] **Step 1: Add an integration test for information hierarchy**

Mock the workspace provider and render a real dataset profile. Assert:

```tsx
expect(screen.getByRole("heading", { name: "選擇分析方式" })).toBeVisible();
expect(screen.getByText("清楚的下一步")).toBeVisible();
expect(screen.getByRole("button", { name: "執行模型分析" })).toBeVisible();
expect(screen.queryByText("Quick AutoML")).not.toBeVisible();
expect(screen.queryByRole("checkbox", { name: /Ridge/ })).not.toBeInTheDocument();
```

Then select manual model mode and assert the model drawer appears.

- [ ] **Step 2: Run test and verify failure**

```bash
cd frontend
npm run test:run -- AnalysisWorkspace.test.tsx
```

Expected: FAIL because the current panel displays all strategy fieldsets.

- [ ] **Step 3: Replace the top-level panel structure**

`ModelAnalysisPanel` keeps:

- API calls.
- workspace state keys.
- validation.
- result state.
- code generation orchestration.

Replace the current two-column fieldset wall with:

```tsx
<section className="analysis-focus-workspace" aria-busy={isLoading}>
  <AnalysisStepRail current={workspaceStep} />
  <div className="analysis-focus-grid">
    <div className="analysis-primary-stage">
      <label>
        <span className="ui-copy-primary">{text("目標欄位", "Target column")}</span>
        <select
          value={targetColumn}
          onChange={(event) => {
            setTargetColumn(event.target.value);
            setResult(null);
            setError(null);
          }}
        >
          {dataset.columns.map((column) => (
            <option key={column} value={column}>{column}</option>
          ))}
        </select>
      </label>
      <AnalysisModeSelector
        value={analysisMode}
        onChange={(value) => {
          setAnalysisMode(value);
          setResult(null);
          setError(null);
        }}
      />
      <DatasetMetricStrip
        rows={dataset.row_count}
        features={featureCount}
        models={visibleModelOptions.length}
      />
      <div className="analysis-next-action">
        <div>
          <span>{text("清楚的下一步", "A clear next step")}</span>
          <strong>
            {runDisabledReason ??
              text("開始比較候選模型", "Start comparing candidate models")}
          </strong>
        </div>
        <Button
          type="button"
          disabled={Boolean(runDisabledReason) || isLoading}
          aria-describedby={runDisabledReason ? "analysis-run-disabled-reason" : undefined}
          onClick={handleRunModels}
        >
          {text("執行模型分析", "Run model analysis")}
        </Button>
        {runDisabledReason ? (
          <p id="analysis-run-disabled-reason" className="ui-copy-secondary">
            {runDisabledReason}
          </p>
        ) : null}
      </div>
    </div>
    <AnalysisRecommendationPanel
      dataset={dataset}
      targetColumn={targetColumn}
      analysisMode={analysisMode}
      availableModelCount={visibleModelOptions.length}
    />
  </div>
  {isLoading ? (
    <AnalysisLoadingState
      title={text("正在評估模型組合", "Evaluating model candidates")}
      steps={[text("等待後端回報分析階段", "Waiting for the backend stage")]}
      progress={jobProgress}
      onCancel={activeJobId ? handleCancelAnalysis : undefined}
      isCancelling={isCancelling}
    />
  ) : null}
  {result ? <ModelAnalysisResult result={result} file={file} files={files} isMerged={isMerged} /> : null}
</section>
```

Compute:

```tsx
const workspaceStep = result
  ? "result"
  : isLoading
    ? "running"
    : "method";
```

- [ ] **Step 4: Keep only one primary action**

Move `執行模型分析` into `.analysis-next-action`. Remove the duplicate top-right button.

Disabled reasons:

```tsx
const runDisabledReason =
  !targetColumn
    ? text("請先選擇目標欄位", "Choose a target column first")
    : modelSelectionMode === "custom" && selectedModels.length === 0
      ? text("請至少選擇一個模型", "Choose at least one model")
      : chartSelectionMode === "custom" && selectedCharts.length === 0
        ? text("請至少選擇一張圖表", "Choose at least one chart")
        : null;
```

Render the reason adjacent to the disabled button and connect it with `aria-describedby`.

- [ ] **Step 5: Place advanced controls behind progressive disclosure**

Default visible:

- target column.
- recommended targets.
- analysis mode.
- dataset metric strip.
- automatic/manual model strategy.

Collapsed:

- manual model drawer.
- AutoML.
- chart selection.

Do not delete existing functionality.

- [ ] **Step 6: Update WorkspaceToolPages copy**

Model page title:

```tsx
title={text("選擇分析方式", "Choose an analysis approach")}
```

Description:

```tsx
description={text(
  "先確認目標與方法，系統再依真實資料選出候選模型。",
  "Confirm the target and approach before the system selects candidates from the real dataset."
)}
```

Keep the text within two lines at 1280px.

- [ ] **Step 7: Run integration tests**

```bash
cd frontend
npm run test:run -- AnalysisWorkspace.test.tsx
```

Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add frontend/src/components/ModelAnalysisPanel.tsx \
  frontend/src/components/WorkspaceToolPages.tsx \
  frontend/src/components/__tests__/AnalysisWorkspace.test.tsx \
  frontend/src/app/product-interface.css
git commit -m "feat: focus model analysis on one decision at a time"
```

## Task 6: Show Only Real Progress and Prioritize Results

**Files:**
- Modify: `frontend/src/components/PagePrimitives.tsx`
- Modify: `frontend/src/components/ModelAnalysisPanel.tsx`
- Create: `frontend/src/components/analysis/InlineCodeViewer.tsx`
- Create: `frontend/src/components/__tests__/InlineCodeViewer.test.tsx`
- Modify: `frontend/src/components/__tests__/AnalysisWorkspace.test.tsx`
- Modify: `frontend/src/app/product-interface.css`

- [ ] **Step 1: Write a failing no-fake-progress test**

Use fake timers:

```tsx
it("does not rotate through fabricated steps when backend progress is absent", () => {
  vi.useFakeTimers();
  render(
    <AnalysisLoadingState
      title="正在分析"
      steps={["第一步", "第二步", "第三步"]}
    />
  );

  expect(screen.getByText("第一步")).toBeVisible();
  act(() => vi.advanceTimersByTime(10_000));
  expect(screen.getByText("第一步")).toBeVisible();
  expect(screen.queryByText("第二步")).not.toBeInTheDocument();
});
```

- [ ] **Step 2: Remove the rotating fallback timer**

Delete `activeStep`, `setInterval`, and timer-based transitions from `AnalysisLoadingState`.

When `progress` is absent, render:

```tsx
steps[0]
```

When `progress` exists, use only:

```tsx
analysisStageLabel(progress.stage, text)
```

- [ ] **Step 3: Write InlineCodeViewer tests**

```tsx
it("shows generated code with line numbers and copies the active content", async () => {
  const writeText = vi.fn().mockResolvedValue(undefined);
  Object.assign(navigator, { clipboard: { writeText } });

  render(
    <InlineCodeViewer
      pythonContent={"a = 1\nprint(a)"}
      notebookContent={'{"cells":[]}'}
      pythonPath="generated_code.py"
      notebookPath="notebook.ipynb"
    />
  );

  expect(screen.getByText("1")).toBeVisible();
  expect(screen.getByText("2")).toBeVisible();
  await userEvent.click(screen.getByRole("button", { name: "複製程式碼" }));
  expect(writeText).toHaveBeenCalledWith("a = 1\nprint(a)");
});
```

- [ ] **Step 4: Implement InlineCodeViewer**

Public API:

```tsx
export function InlineCodeViewer({
  pythonContent,
  notebookContent,
  pythonPath,
  notebookPath
}: {
  pythonContent: string;
  notebookContent: string;
  pythonPath: string;
  notebookPath: string;
}) {
  const { text } = useLocale();
  const [mode, setMode] = useState<"python" | "notebook">("python");
  const [copied, setCopied] = useState(false);
  const content = mode === "python" ? pythonContent : notebookContent;
  const path = mode === "python" ? pythonPath : notebookPath;

  async function copyCode() {
    await navigator.clipboard.writeText(content);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  }

  return (
    <section className="inline-code-viewer">
      <div className="inline-code-toolbar">
        <div role="tablist" aria-label={text("程式碼格式", "Code format")}>
          {(["python", "notebook"] as const).map((value) => (
            <button
              key={value}
              type="button"
              role="tab"
              aria-selected={mode === value}
              onClick={() => setMode(value)}
            >
              {value === "python" ? "Python" : "Notebook"}
            </button>
          ))}
        </div>
        <button type="button" onClick={copyCode}>
          {copied ? text("已複製", "Copied") : text("複製程式碼", "Copy code")}
        </button>
      </div>
      <div className="inline-code-path">{path}</div>
      <pre>
        <code>
          {content.split("\n").map((line, index) => (
            <span className="inline-code-line" key={`${index}-${line}`}>
              <span aria-hidden="true">{index + 1}</span>
              <span>{line || " "}</span>
            </span>
          ))}
        </code>
      </pre>
    </section>
  );
}
```

Use a CSS grid with a line-number column. Do not add a large syntax-highlighting dependency in this tranche; apply lightweight token coloring only to Python keywords through precomputed spans, or retain monospace high-contrast text if tokenization would be unsafe.

- [ ] **Step 5: Reorder ModelAnalysisResult**

First viewport order:

1. best model.
2. primary metrics.
3. explicit next action.
4. model comparison chart.

Move:

- full table into disclosure.
- downloads after the primary conclusion.
- notes after the result summary.
- code generation after result outputs.

Add a deterministic next-action sentence:

```tsx
const nextAction = isClassification
  ? text(
      "先檢查 F1 與 Accuracy 是否同時可接受，再查看完整模型比較。",
      "Confirm that F1 and accuracy are both acceptable before reviewing the full comparison."
    )
  : text(
      "先比較 RMSE 與 R²，再查看特徵重要性與殘差。",
      "Compare RMSE and R² before reviewing feature importance and residuals."
    );
```

Do not state that a model is trustworthy or production-ready.

- [ ] **Step 6: Replace the existing code preview**

In `CodeGenerationPanel`, replace the raw `<pre>` block and local preview-mode buttons with `InlineCodeViewer`.

Keep Python and Notebook downloads as secondary buttons.

- [ ] **Step 7: Run tests**

```bash
cd frontend
npm run test:run -- AnalysisWorkspace.test.tsx InlineCodeViewer.test.tsx
```

Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add frontend/src/components/PagePrimitives.tsx \
  frontend/src/components/ModelAnalysisPanel.tsx \
  frontend/src/components/analysis/InlineCodeViewer.tsx \
  frontend/src/components/__tests__/AnalysisWorkspace.test.tsx \
  frontend/src/components/__tests__/InlineCodeViewer.test.tsx \
  frontend/src/app/product-interface.css
git commit -m "fix: show real progress and prioritize analysis conclusions"
```

## Task 7: Add Restrained Motion Without Reintroducing Decorative Risk

**Files:**
- Modify: `frontend/src/app/product-motion.css`
- Modify: `frontend/src/app/product-interface.css`
- Modify: `frontend/src/components/analysis/ModelSelectionDrawer.tsx`
- Modify: `frontend/src/components/analysis/AnalysisRecommendationPanel.tsx`
- Modify: `frontend/src/components/ModelAnalysisPanel.tsx`

- [ ] **Step 1: Define allowed motion tokens**

Add:

```css
:root {
  --motion-fast: 180ms;
  --motion-standard: 240ms;
  --motion-section: 380ms;
  --motion-ease: cubic-bezier(0.16, 1, 0.3, 1);
}
```

- [ ] **Step 2: Add only task-supporting transitions**

Allowed:

- selected option border/background transition.
- drawer reveal.
- recommendation panel replacement.
- result reveal.
- button press.

Not allowed in this tranche:

- new particles.
- cursor-following glow.
- additional themes.
- continuous decorative mesh animation.
- magnetic buttons.

- [ ] **Step 3: Add reduced-motion fallbacks**

```css
@media (prefers-reduced-motion: reduce) {
  .analysis-focus-workspace *,
  .model-selection-drawer,
  .analysis-recommendation-panel {
    animation: none !important;
    scroll-behavior: auto !important;
    transition-duration: 0.01ms !important;
  }
}
```

- [ ] **Step 4: Verify keyboard and touch behavior**

The plan implementer must confirm:

- every radio/checkbox receives visible `focus-visible`.
- touch targets are at least 44px.
- drawer content remains reachable without hover.
- no animation delays API actions.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/app/product-motion.css \
  frontend/src/app/product-interface.css \
  frontend/src/components/analysis/ModelSelectionDrawer.tsx \
  frontend/src/components/analysis/AnalysisRecommendationPanel.tsx \
  frontend/src/components/ModelAnalysisPanel.tsx
git commit -m "style: add restrained motion to the analysis workflow"
```

## Task 8: Update Progress Records and Run Full Verification

**Files:**
- Modify: `README.md`
- Modify: `PROGRESS.md`
- Modify: `docs/audits/2026-06-15-project-plan-consistency-audit.md`

- [ ] **Step 1: Update README to match actual behavior**

Document:

- theme selection is immediate.
- generated artifact URLs expire.
- direct `/generated_outputs/*` access is removed.
- environment remains closed beta and not multi-tenant safe.
- focused model analysis flow.
- generated code is visible before download.

- [ ] **Step 2: Add a dated PROGRESS entry**

Include:

- completed files.
- features.
- startup commands.
- test commands and actual counts.
- known issues.
- next phase: Persistent Analysis Run, PostgreSQL, auth, Worker, SSE.

Do not mark Phase B complete.

- [ ] **Step 3: Add an audit follow-up section**

Append a short section to the audit:

```markdown
## 14. 第一批修正追蹤

- C1：部分緩解。公開 StaticFiles 已移除，改為短效 capability URL；尚未完成 user/project ownership。
- C2：已修正。部署文件與產品入口改為封閉測試定位。
- M3：已修正。重複主要 CTA 已收斂。
- M6：已修正。Docker 與 package engine 統一 Node 22。
- 可讀性與工作區：已依 A 聚焦流程台完成；未新增模型或裝飾性主題。
```

- [ ] **Step 4: Run backend suite**

```bash
cd backend
pytest -q
```

Expected: all tests pass.

- [ ] **Step 5: Run frontend suite**

```bash
cd frontend
npm run test:run
npm run typecheck
npm run build -- --webpack
```

Expected: all tests pass, typecheck exits 0, production build exits 0.

- [ ] **Step 6: Run repository checks**

```bash
git diff --check
rg -n "StaticFiles|/generated_outputs/:path|先即時預覽|按下「套用」" \
  backend frontend README.md DEPLOYMENT.md
```

Expected:

- `git diff --check` exits 0.
- no public StaticFiles mount.
- no generated-output rewrite.
- no outdated theme instructions.

- [ ] **Step 7: Browser verification**

Start backend:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Start frontend:

```bash
cd frontend
npm run dev -- --hostname 127.0.0.1 --port 3010
```

Verify with Browser:

1. Open `/`.
2. Confirm closed-testing notice is readable.
3. Open `/app/data`, upload `sample_datasets/housing_sample.csv`.
4. Open `/app/models`.
5. Confirm labels and descriptions are readable in Mist, Frost, Deep Sea, and Midnight.
6. Click a theme and confirm immediate application with no Apply button.
7. Run automatic model analysis with `price_usd`.
8. Confirm progress follows backend stages.
9. Confirm best model and next action appear before the full table.
10. Generate code and confirm Python content is visible, copyable, and downloadable.
11. Open one artifact URL and confirm it downloads.
12. Change one character in the token and confirm HTTP 403.
13. Check 1440×900, 1024×768, 390×844.
14. Check browser zoom at 80%, 100%, 125%, 150%.
15. Confirm console has no errors or hydration warnings.

- [ ] **Step 8: Commit documentation and verification evidence**

```bash
git add README.md PROGRESS.md docs/audits/2026-06-15-project-plan-consistency-audit.md
git commit -m "docs: record audit-aligned stabilization results"
```

## Phase B Handoff

After this plan passes, create a separate implementation plan for:

1. PostgreSQL and migrations.
2. Project, Dataset, DatasetVersion, AnalysisPlan, AnalysisRun, RunEvent, Artifact.
3. immutable Run Manifest.
4. basic auth and Project ownership.
5. private artifact authorization replacing capability-only access.
6. Redis queue and independent worker.
7. retry, timeout, restart recovery, and SSE.
8. resource and cost records.

The current product must remain labeled closed beta until that Phase B plan is implemented and verified.
