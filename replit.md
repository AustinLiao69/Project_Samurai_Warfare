# 《戰國三代記》(Sengoku Sandai-ki)

**Product Owner**: AustinLiao69  
**目標**: 戰國時代單人策略模擬遊戲，最終以 Godot 4.x + GDScript 開發

---

## 當前狀態

- 文件完備（PM001–PM008、SRS_0002–SRS_0011、SPEC 0000–0011）
- MVP Webapp 互動原型：Python + Flask，運行於 Port 5000
- Webapp 路徑：`00.Documentation/0050.MVP/webapp/app.py`
- 啟動指令：`python3 '00.Documentation/0050.MVP/webapp/app.py'`

---

## 目錄結構

```
00.Documentation/
├── 0.對話/          ← email 式任務往來（YYYYMMDD.主題.md）
├── 0030.SPECs/      ← 0000.Product_SPEC.md ~ 0011.武將評價模組.md
├── 0040.Project documents/  ← PM001~PM004, PM006~PM008, 審查報告
├── 0050.MVP/        ← MVP 文件 + webapp 代碼
│   ├── PM006.MVP_SRS.md
│   ├── PM007.MVP劇本_永祿三年.md
│   ├── PM008.MVP初始資料.md
│   └── webapp/      ← Flask app（互動原型）
└── 0050.SRS/        ← SRS_0002~SRS_0011（GDScript 介面規格）
9999.工作日誌.csv    ← 所有工作記錄
```

---

## MVP Webapp 互動功能（PM006 對應）

| Use Case | 功能 |
|---------|------|
| UC-004 | 結束回合：資源結算、月份推進、設施完工 |
| UC-010 | 點擊郡點 → 詳情 Modal |
| UC-011 | 設施升級（扣金、建設計時） |
| UC-012 | 年貢率拉桿（10-60%，即時預估） |
| UC-022 | 攻郡野戰（選武將、公式結算、戰報） |

---

## 重要規格

- **武將四面向**：軍事 / 智謀 / 政治 / 魅力（玩家僅見文字評語，不見數值）
- **忠誠度**：唯一忠誠指標，6 個等級（臣服如山→潛在叛徒）
- **MVP 範圍**：Phase 1–3，2 勢力（織田 vs 今川），4 城，8 郡
- **正式版**：Godot 4.x + GDScript，webapp 僅為視覺原型

---

## 工作日誌規則

每次任務完成後必須在 `9999.工作日誌.csv` 追加記錄。
