# SeniorPM — 每次任務標準作業程序（SOP）

**適用對象**：Agent（每次與 AustinLiao69 進行開發任務後必須執行）
**最後更新**：2026-05-01

---

## 每次任務結束後，必須完成以下 5 項：

---

### ✅ Step 1 — 更新工作日誌（9999.工作日誌.csv）

**位置**：`/9999.工作日誌.csv`

**格式**：
```
MM    DD    Description    Progress
```

**規則**：
- 每一項實作/修復/文件 → 各自一行
- `Progress`：`Done` / `Ongoing` / `Backlog`
- 若為回饋 feedback，標注 `[FBn]`；若為 Bug Fix，標注 `BUG FIX`
- 粒度適中：一行描述一個完整的邏輯變更單元

---

### ✅ Step 2 — 更新功能規格（PM006.MVP_SRS.md）

**位置**：`00.Documentation/0050.MVP/PM006.MVP_SRS.md`

**更新項目（視變更內容選擇）**：
- **版本號與最後更新日期**（文件頂端）
- **三、UI 架構**：若有新的介面設計或互動方式
- **五、功能需求**：新增 UC-xxx 條目描述新功能
- **六、資料模型**：若有新增/修改欄位（如 chatelain/daikan）
- **十、API 規格**：若有新增/修改 API 路由
- **十二、版本更新歷史**：每次更新必填，描述本次主要變更

---

### ✅ Step 3 — 記錄對話（00.Documentation/0.對話/）

**位置**：`00.Documentation/0.對話/YYYYMMDD.主題.md`

**格式參考**：`20260430.MVP第二次回饋紀錄.md`

**規則**：
- 每次有意義的回饋/需求討論 → 建立新的對話紀錄檔案
- 檔名：`YYYYMMDD.主題簡述.md`（日期 + 主題，不超過 20 字）
- 內容：每個 Feedback 一個 `##` 區塊，包含：**需求**、**設計決策**、**處理方式**
- 若同一天有多次對話 → 檔名加後綴，如 `20260501.主題_2.md`

---

### ✅ Step 4 — 更新 SeniorPM.md（本文件）

**位置**：`/SeniorPM.md`

**何時更新**：
- 有新的 SOP 規則需要加入
- 現有規則描述不夠清楚需要修訂
- 工作流程有重大調整

**規則**：維持精簡、可執行性高；每條規則必須具體到能立即照做。

---

### ✅ Step 5 — 驗收確認

完成以上步驟後，自我確認：

| 檢查項目 | 是否完成 |
|---------|---------|
| 9999.工作日誌.csv 已新增本次所有項目 | ☐ |
| PM006 版本號已更新 | ☐ |
| PM006 相關 UC / 資料模型 / 版本歷史已更新 | ☐ |
| 0.對話/ 已建立本次紀錄檔案 | ☐ |
| SeniorPM.md 本身是否需要更新（如有新規則） | ☐ |

---

## 附錄：重要檔案位置速查

| 用途 | 路徑 |
|------|------|
| 工作日誌 | `9999.工作日誌.csv` |
| MVP SRS（主規格書）| `00.Documentation/0050.MVP/PM006.MVP_SRS.md` |
| 對話紀錄資料夾 | `00.Documentation/0.對話/` |
| MVP Webapp 進入點 | `00.Documentation/0050.MVP/webapp/app.py` |
| 初始資料 | `00.Documentation/0050.MVP/webapp/data/initial.py` |
| 遊戲邏輯 | `00.Documentation/0050.MVP/webapp/game/logic.py` |
| 前端 JS | `00.Documentation/0050.MVP/webapp/static/js/game.js` |
| CSS | `00.Documentation/0050.MVP/webapp/static/css/style.css` |
| 模板資料夾 | `00.Documentation/0050.MVP/webapp/templates/` |
