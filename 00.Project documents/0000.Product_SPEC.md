
# 《戰國三代記》Product SPEC v1.0

## 1. 產品概述 (Product Overview)

### 1.1 遊戲類型與目標市場
- **遊戲類型**：戰略模擬遊戲 (Strategy Simulation Game)
- **平台**：PC (Windows, macOS, Linux)
- **開發引擎**：Godot 4.x
- **開發語言**：GDScript
- **目標市場**：喜愛日本戰國歷史、策略遊戲和政治權謀的玩家

### 1.2 核心價值主張
- 深度的封建社會模擬，強調家臣團內部政治
- 多層級的領地管理系統 (令制國 → 城 → 郡)
- 豐富的權謀系統，包含忠誠度、派系鬥爭、叛變風險
- 真實的戰國時代軍事系統，區分城兵與農兵

### 1.3 競品分析與差異化定位
- 與《信長之野望》相比：更深入的家臣團內部政治
- 與《全軍破敵》相比：更專注於封建社會結構
- 與《十字軍之王》相比：更聚焦於日本戰國特色

## 2. 技術規格 (Technical Specifications)

### 2.1 系統架構

#### 核心架構設計
```
MainGame (主遊戲控制器)
├── GameStateManager (遊戲狀態管理)
├── SaveSystem (存檔系統)
├── UIManager (UI管理器)
└── GameSystems (遊戲系統集合)
    ├── CoreSystem (核心系統)
    ├── RetainerSystem (家臣團系統)
    ├── TerritorySystem (領國系統)
    ├── IntrigueSystem (權謀系統)
    ├── MilitarySystem (軍事系統)
    ├── CouncilSystem (評定系統)
    └── IntelligenceSystem (情報系統)
```

#### 資料結構設計
```gdscript
# 主要資料類
class_name GameData extends Resource

# 勢力資料
class_name Faction extends Resource
@export var name: String
@export var daimyo: Retainer
@export var territories: Array[Territory]
@export var retainer_groups: Array[RetainerGroup]

# 家臣資料
class_name Retainer extends Resource
@export var name: String
@export var rank: RetainerRank
@export var abilities: RetainerAbilities
@export var loyalty: LoyaltyLevel
@export var faction_allegiance: String

# 領地資料
class_name Territory extends Resource
@export var name: String
@export var type: TerritoryType
@export var level: int
@export var facilities: Array[Facility]
@export var assigned_retainer: Retainer
```

### 2.2 核心系統模組

#### 2.2.1 核心系統 (CoreSystem)
**功能**：遊戲入口、命令處理、回合管理
```gdscript
class_name CoreSystem extends Node

func process_turn():
    # 處理每回合事件
    pass

func execute_command(command: GameCommand):
    # 執行玩家命令
    pass

func save_game(slot: int):
    # 儲存遊戲
    pass

func load_game(slot: int):
    # 讀取遊戲
    pass
```

#### 2.2.2 家臣團系統 (RetainerSystem)
**功能**：家臣管理、階級系統、兵力計算
```gdscript
class_name RetainerSystem extends Node

func create_retainer_group(leader: Retainer, type: GroupType) -> RetainerGroup:
    # 創建家臣團
    pass

func calculate_total_forces(group: RetainerGroup) -> int:
    # 計算家臣團總兵力
    pass

func promote_retainer(retainer: Retainer, new_rank: RetainerRank):
    # 晉升家臣
    pass

func assign_subordinates(leader: Retainer, subordinates: Array[Retainer]):
    # 指派下屬
    pass
```

#### 2.2.3 領國系統 (TerritorySystem)
**功能**：領地管理、設施升級、年貢收取
```gdscript
class_name TerritorySystem extends Node

func upgrade_facility(territory: Territory, facility_type: FacilityType):
    # 升級設施
    pass

func collect_nengu(territory: Territory) -> Resources:
    # 收取年貢
    pass

func set_nengu_rate(territory: Territory, rate: float):
    # 設定年貢比例
    pass

func calculate_loyalty_impact(territory: Territory, nengu_rate: float) -> float:
    # 計算年貢對忠誠度的影響
    pass
```

### 2.3 資料庫設計

#### 主要資料表結構
```sql
-- 勢力表
Factions:
- id (Primary Key)
- name
- daimyo_id
- gold
- military_supplies
- created_at

-- 家臣表
Retainers:
- id (Primary Key)
- faction_id (Foreign Key)
- name
- rank
- martial_ability
- command_ability
- intelligence
- politics
- loyalty_level
- current_forces

-- 領地表
Territories:
- id (Primary Key)
- faction_id (Foreign Key)
- name
- type (國/城/郡)
- level
- assigned_retainer_id
- nengu_rate

-- 設施表
Facilities:
- id (Primary Key)
- territory_id (Foreign Key)
- type
- level
- upgrade_cost
```

### 2.4 性能指標與限制
- **最大勢力數**：50個
- **最大家臣數**：每勢力500人
- **最大領地數**：每勢力200個
- **回合處理時間**：< 3秒
- **存檔大小**：< 10MB
- **記憶體使用**：< 1GB

## 3. 功能需求規格 (Functional Requirements)

### 3.1 遊戲入口功能
- 新遊戲創建
- 存檔讀取 (最多10個存檔槽)
- 自創武將系統
- 稱號一覽查看

### 3.2 政務管理功能

#### 3.2.1 基本政務
| 功能 | 描述 | 輸入 | 輸出 |
|------|------|------|------|
| 任命官職 | 指派家臣擔任職位 | 家臣ID, 職位類型 | 家臣忠誠度變化 |
| 治理郡城 | 管理領地發展 | 領地ID, 治理指令 | 領地等級/資源變化 |
| 施行法令 | 頒布政策影響全勢力 | 法令類型, 參數 | 全體忠誠度/資源變化 |
| 視察地方 | 巡視領地觸發事件 | 領地ID | 隨機事件觸發 |

#### 3.2.2 高級政務
| 功能 | 描述 | 業務邏輯 |
|------|------|----------|
| 舉行典禮 | 提升威望和忠誠度 | 消耗金錢，提升全體忠誠度 |
| 評定會議 | 重大決策制定 | 家臣提案，大名決策，影響派系關係 |
| 召集農民兵 | 徵召臨時兵力 | 影響農業產出，增加軍事力量 |
| 授予知行 | 分封領地給家臣 | 轉移領地控制權，影響家臣忠誠度 |

### 3.3 軍事系統功能

#### 3.3.1 兵力管理
```gdscript
# 兵力類型定義
enum ForceType {
    CASTLE_FORCES,    # 城兵：立即可用，由勢力負擔軍糧
    PEASANT_FORCES    # 農兵：需1個月集結，前3月自負軍糧
}

# 兵力計算
func calculate_available_forces(territory: Territory, force_type: ForceType) -> int:
    match force_type:
        ForceType.CASTLE_FORCES:
            return territory.castle_level * 500
        ForceType.PEASANT_FORCES:
            return territory.population * 0.1
```

#### 3.3.2 戰鬥系統
| 戰鬥類型 | 觸發條件 | 介面類型 | 勝利條件 |
|---------|----------|----------|----------|
| 野戰 | 攻擊郡 | 戰棋式地圖 | 敵軍全滅或撤退 |
| 圍城戰 | 包圍城池 | 回合制消耗 | 敵方軍糧耗盡 |
| 攻城戰 | 強攻城池 | 分層攻防 | 攻破本丸 |

### 3.4 權謀系統功能

#### 3.4.1 忠誠度系統
```gdscript
enum LoyaltyLevel {
    ABSOLUTE_LOYALTY,    # 臣服如山 (91-100)
    HIGH_LOYALTY,        # 忠心耿耿 (76-90)
    MODERATE_LOYALTY,    # 表面恭敬 (61-75)
    UNCERTAIN,           # 意圖未明 (41-60)
    LOW_LOYALTY,         # 暗懷異志 (21-40)
    POTENTIAL_TRAITOR    # 潛在叛徒 (0-20)
}
```

#### 3.4.2 派系系統
- 家臣可組成支持不同繼承人的派系
- 派系間可進行政治鬥爭
- 影響評定會議的決策結果

### 3.5 情報系統功能

#### 3.5.1 忍者任務類型
| 任務類型 | 目標 | 成功效果 | 失敗風險 |
|---------|------|----------|----------|
| 刺探 | 獲取敵方情報 | 揭露軍力/忠誠度 | 忍者被捕 |
| 暗殺 | 消除敵方將領 | 目標死亡 | 外交惡化 |
| 籠絡 | 策反敵方家臣 | 獲得內應 | 身分暴露 |
| 離間 | 挑撥敵方內鬥 | 降低敵方團結 | 計謀被識破 |
| 破壞 | 損壞敵方設施 | 削弱敵方實力 | 戒備提升 |

## 4. 用戶體驗設計 (UX Design Requirements)

### 4.1 介面設計原則
- **戰情室風格**：古風地圖攤在桌上，立體旗幟標示
- **分層導航**：令制國 → 城 → 郡的階層式瀏覽
- **資訊密度適中**：重要資訊一目了然，詳細資訊點擊查看

### 4.2 主要介面規劃

#### 4.2.1 主地圖介面
- 全國地圖模式：顯示勢力分布
- 地方地圖模式：顯示城郡詳情
- 軍勢標示：立體軍旗顯示部隊位置
- 切換按鈕：勢力圖/外交圖/分封圖

#### 4.2.2 政務介面
- 常駐命令列：存檔、讀檔、情報查看
- 政務選單：樹狀結構，最多三層
- 執行確認：重要決策需確認對話框

#### 4.2.3 戰鬥介面
- 野戰：六角格戰棋，地形效果明顯
- 攻城：分層城防圖，進攻路線清楚
- 部隊資訊：血量、士氣、武將能力一目了然

### 4.3 操作流程設計

#### 4.3.1 典型遊戲回合流程
```
1. 回合開始 → 事件提示 → 收入結算
2. 政務階段 → 選擇政務項目 → 執行決策
3. 軍事階段 → 部隊移動 → 戰鬥解決
4. 評定階段 → 家臣提案 → 大名決策
5. 情報階段 → 忍者報告 → 指派新任務
6. 回合結束 → 自動存檔 → 下一回合
```

#### 4.3.2 家臣管理流程
```
查看家臣列表 → 選擇家臣 → 查看詳細資訊
→ 執行操作（晉升/指派/獎賞） → 確認變更
→ 查看忠誠度變化 → 更新家臣團結構
```

## 5. 開發階段規劃 (Development Phases)

### 5.1 MVP 功能定義 (最小可行產品)
**目標**：實現基本的戰國領主體驗

#### 階段 1：核心系統 (4週)
- 遊戲入口與存檔系統
- 基本地圖顯示
- 簡化的家臣團系統
- 基本政務功能

#### 階段 2：領地管理 (3週)
- 三層級領地系統
- 設施建設與升級
- 年貢收取機制
- 資源管理

#### 階段 3：軍事基礎 (4週)
- 基本兵力系統
- 簡化野戰
- 城兵與農兵區別
- 基本攻城機制

### 5.2 完整版本開發計畫

#### 階段 4：權謀系統 (5週)
- 忠誠度系統
- 派系機制
- 評定會議
- 家臣互動事件

#### 階段 5：情報系統 (4週)
- 忍者系統
- 情報收集
- 謀略活動
- 反間諜機制

#### 階段 6：高級軍事 (6週)
- 完整攻城系統
- 戰術與計謀
- 武將能力影響
- 軍事研發

#### 階段 7：優化與平衡 (4週)
- 遊戲平衡調整
- 效能優化
- Bug 修復
- UI/UX 改進

### 5.3 優先級排序
1. **高優先級**：核心系統、領地管理、基本軍事
2. **中優先級**：權謀系統、情報系統
3. **低優先級**：高級軍事功能、特殊事件

## 6. 品質保證 (Quality Assurance)

### 6.1 測試策略

#### 6.1.1 單元測試
- 核心邏輯函數測試
- 資料計算準確性驗證
- 邊界條件測試

#### 6.1.2 整合測試
- 系統間介面測試
- 資料流正確性驗證
- 存檔讀取完整性測試

#### 6.1.3 遊戲性測試
- 平衡性測試
- 用戶體驗測試
- 長時間遊戲穩定性測試

### 6.2 驗收標準

#### 6.2.1 功能性標準
- 所有核心功能正常運作
- 存檔系統穩定可靠
- 戰鬥計算準確無誤
- UI 操作流暢直觀

#### 6.2.2 效能標準
- 回合處理時間 < 3秒
- 介面響應時間 < 0.5秒
- 記憶體使用 < 1GB
- 無明顯記憶體洩漏

#### 6.2.3 穩定性標準
- 連續遊玩4小時無當機
- 存檔成功率 > 99.9%
- 關鍵操作錯誤率 < 0.1%

### 6.3 風險評估

#### 6.3.1 技術風險
- **複雜度風險**：家臣團系統邏輯複雜，需充分測試
- **效能風險**：大量資料計算可能影響效能
- **相容性風險**：跨平台相容性需要驗證

#### 6.3.2 時程風險
- **功能蔓延**：避免需求無限擴張
- **技術債務**：控制程式碼品質
- **測試時間**：預留充足的測試時間

#### 6.3.3 市場風險
- **競品競爭**：保持特色差異化
- **玩家接受度**：及早獲得玩家回饋
- **長期維護**：規劃後續更新內容

## 7. 部署與維護

### 7.1 部署規劃
- **平台**：Steam、itch.io
- **版本控制**：Git + Replit
- **自動化建置**：CI/CD 流程
- **發布流程**：Beta測試 → 正式發布

### 7.2 後續維護
- **Bug 修復**：快速響應機制
- **內容更新**：定期新增事件和功能
- **社群經營**：收集玩家意見
- **長期規劃**：續作或大型DLC

---

**文件版本**：v1.0
**撰寫日期**：2024
**預計開發週期**：30週
**目標平台**：PC (Windows, macOS, Linux)
**開發工具**：Godot 4.x + GDScript
