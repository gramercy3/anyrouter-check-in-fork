**通知／Telegram**
- 支援 `TELEGRAM_FORMAT` 三態：`table`／`plain`／`auto`（現為 `auto`，可改為預設 `table`）。
- 表格欄位可配置（預設：帳號、餘額、已用），加入欄寬上限與截斷避免超長名稱撐寬。
- 針對不同語系與貨幣（例如 TWD／USD）加上顯示單位與格式化（小數位、千分位）。
- 更嚴謹的 HTML 轉義與訊息長度分段（Telegram 有訊息長度上限）。
- 成功／失敗摘要改為表格外提示，表格僅呈現餘額資訊；並可選擇只顯示失敗帳號。

**工作流／CI**
- 將 `runs-on: windows-2025` 改為 `windows-latest`（或加入自託管 runner label 檢查）。
- 在 workflow_dispatch 加入 inputs（如 `always_notify`、`notify_debug`、`format`），以便臨時覆蓋環境行為。
- 加入 `concurrency` 與 `fail-fast: false`，避免重覆執行互相干擾。
- 緩存 Playwright 與 Python 依賴時加入 OS 與版本 key，降低快取碰撞風險。
- 上傳執行日誌與 `balance_hash.txt` 為 artifacts，便於回溯分析。

**錯誤處理與重試**
- Telegram 推送加入指數退避重試（HTTP 429／5xx），重試次數與間隔可配置。
- httpx 請求統一 timeout／重試策略，並支援 proxy（如企業網路）。
- 更完整的 API 回應驗證（`ok`、`error_code`、`description`），並在 `NOTIFY_DEBUG=true` 時輸出堆疊。
- 將失敗通知去重與彙整，避免同一帳號多次重覆訊息。

**測試覆蓋率**
- 將 `tests/test_notify.py` 由 `requests` 改為 `httpx` mock，對齊目前實作。
- 新增 Telegram 表格自動偵測（auto／plain／table）與欄位格式的單元測試。
- 為通知路由（Email／DingTalk／Feishu／WeCom）建立最小可行 mock 測試確保介面穩定。
- 加入 `pytest-cov` 報告並在 CI 顯示覆蓋率摘要。

**設定與安全**
- 以 JSON Schema 驗證 `ANYROUTER_ACCOUNTS`／`PROVIDERS`，在啟動前印出清楚的設定錯誤。
- 秘密使用 GitHub Environments 管理，統一命名並避免在 logs 中洩漏敏感內容。
- `ALWAYS_NOTIFY`、`NOTIFY_DEBUG` 改由 workflow inputs 控制，減少環境漂移造成的不可預期行為。

**程式碼品質與維護**
- 將平臺差異（Windows／Linux）抽象為設定，避免硬編 UA 與 headless 參數。
- 將餘額雜湊包含 `quota + used`（現僅 `quota`），更精確偵測變化；並提供忽略門檻（變動小於 X 不通知）。
- 加入結構化日誌（JSON lines），利於在 CI 與本地分析；同時維持人類可讀輸出。
- 規範 utils 介面並補充型別註記，避免未定義變數在 `finally` 使用的情況。

**使用者體驗**
- CLI 旗標：`--always-notify`、`--format=table|plain|auto`、`--notify-debug`，優先於環境。
- 加入時區設定（如 `TZ=Asia/Taipei`）與顯示格式，讓時間資訊在通知中更直觀。
- 在 README 新增常見錯誤排除（chat_id 取得、bot 權限、群組／頻道設定）與範例。
