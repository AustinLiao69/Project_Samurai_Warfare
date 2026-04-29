# 《戰國三代記》(Sengoku Sandai-ki) — 專案說明

## 專案概述

《戰國三代記》是一款以日本戰國時代為背景的深度策略模擬遊戲（PC）。  
本倉庫目前為設計文件與 PM 管理文件的存放庫，遊戲使用 Godot 4.x + GDScript 開發。

## 文件瀏覽器

本倉庫內建一個戰國風格的文件瀏覽 Web 介面，啟動後可在瀏覽器中閱讀所有 Markdown 文件。

**啟動指令**：`python3 server.py`（Port 5000）

## 目錄結構

```
/
├── 00.Project documents/     # 所有設計與 PM 文件
│   ├── PM001.專案章程.md         ← 專案目標、範圍、利害關係人
│   ├── PM002.開發藍圖與里程碑.md  ← 30 週開發計畫、Sprint 規劃
│   ├── PM003.風險管理計畫.md      ← 風險登記表、應對策略
│   ├── PM004.完成定義與驗收標準.md ← DoD、Acceptance Criteria
│   ├── PM005.技術架構說明.md      ← 系統架構、資料結構、開發規範
│   ├── 0000.Product_SPEC.md      ← 產品規格
│   ├── 0001.系統概覽.md           ← 系統模組概覽
│   ├── 0002-0010.各模組設計.md    ← 各遊戲系統詳細設計
│   ├── 0090.User story.md        ← 用戶故事
│   └── 0097.User story map.md    ← 用戶故事地圖
├── 01.Character potrait/     # 角色設計與 AI 生成 Prompt
├── 02.Prompt_Character/      # 角色生成 Prompt
├── docs/                     # 技術工作流文件
├── src/                      # 遊戲原始碼（Godot 開發中）
├── server.py                 # 文件瀏覽伺服器
└── 9999.工作日誌.csv          # 開發工作日誌
```

## 技術棧

- **遊戲引擎**：Godot 4.x
- **開發語言**：GDScript
- **目標平台**：PC (Windows / macOS / Linux)
- **文件伺服器**：Python 3 built-in HTTPServer

## 開發現況

- 目前階段：**設計文件凍結期（Week 1-2）**
- 所有模組設計文件已完成
- PM 管理文件（PM001-PM005）已完成
- Godot 遊戲開發尚未開始（待設計凍結後啟動）

## 里程碑摘要

| 里程碑 | 內容 | 週次 |
|--------|------|------|
| M0 | 設計凍結 | Week 2 |
| M1 | 核心系統可運行 | Week 6 |
| M2 | 領地管理可玩 | Week 9 |
| M3 | MVP 完成 | Week 13 |
| M4 | Alpha | Week 18 |
| M5 | Beta | Week 26 |
| M7 | 正式發布 | Week 30 |
