# Repository Guidelines

## 專案結構與模組組織
- 入口腳本：`checkin.py`。
- 輔助模組：`utils/config.py`、`utils/notify.py`。
- 測試：`tests/`（如 `tests/test_notify.py`）。
- 靜態資產：`assets/`（文件用圖）。
- 設定與工具：`.env`、`.env.example`、`pyproject.toml`、`.pre-commit-config.yaml`。

## 建置、測試與開發指令
- 安裝依賴：`uv sync --dev`（需 Python ≥ 3.11）。
- 本地執行：`uv run checkin.py` 進行簽到。
- 安裝 Playwright（WAF 規避）：`uv run playwright install chromium`。
- 測試：`uv run pytest tests/`（可加 `--cov` 產生覆蓋率）。
- 靜態檢查／格式化：`uv run ruff check .`、`uv run ruff format .`。
- Pre-commit：`pre-commit install` 後 `pre-commit run --all-files`。

## 程式風格與命名規範
- 語言：Python 3.11+。
- Ruff 格式：行寬 120、單引號、縮排使用 Tab（參見 `pyproject.toml`）。
- 檔案命名：`snake_case.py`（如 `utils/notify.py`）。
- 函式／變數：`lower_snake_case`；類別：`PascalCase`。
- 腳本副作用以 `if __name__ == "__main__":` 包裹。

## 測試指南
- 框架：`pytest`（可搭配 `pytest-cov`）。
- 檔名：`tests/test_*.py`；盡量鏡射模組名稱。
- 測試需快速、可隔離；請對網路與機密做 mock。
- 核心流程與 `utils/` 應維持有意義覆蓋率。

## Commit 與 Pull Request 規範
- 建議前綴：`feat:`、`fix:`、`docs:`、`refactor:`、`ci:`（符合歷史慣例）。
- PR 需包含：清楚描述、關聯 issue、變更理由、必要日誌／截圖。
- 面向使用者的變更請更新 `README.md`；保持差異最小。

## 安全與設定提示
- 機密以環境變數管理：`ANYROUTER_ACCOUNTS`、`PROVIDERS`、各通知 Token。
- 禁止提交機密；本地用 `.env`，CI 用 GitHub Environment Secrets。
- JSON 環境值需為單行字串（詳見 `README.md`）。
- 僅在 `bypass_method` 需要時安裝 Playwright。

## 代理／Agent 指引
- 本檔適用整個倉庫；若未來新增更深層 `AGENTS.md`，以其子目錄為準。
