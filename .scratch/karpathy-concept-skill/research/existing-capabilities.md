# 既有解說能力盤點

本筆記整理本次已完成的 read-only scout 盤點，不重跑研究。範圍限於下列四份已安裝 skill 指引；結論是文件宣告的能力，沒有執行產製、驗證目前工具可用性，或遍查所有已安裝技能。

| 能力來源 | 指引已涵蓋 | 不能由此推定 |
| --- | --- | --- |
| [show-me](/Users/carl/.agents/skills/show-me/SKILL.md) | 精簡說明搭配 pseudocode、呼叫樹、檔案／元件樹、Mermaid、diff、聚焦的 HTML 解說頁或短簡報；選最小而有用的視圖。 | 包含完整影片產製流程，或任何主題都需要 HTML。 |
| [visualize](/Users/carl/.codex/plugins/cache/openai-bundled/visualize/1.0.45/skills/visualize/SKILL.md) | 互動解說、模擬、比較；少量控制項、一個主要視覺、對話內 HTML，以及現有視覺成果的匯出。 | 每個 agent 環境都有同一呈現工具，或互動必然增加理解。 |
| [archify](/Users/carl/.agents/skills/archify/SKILL.md) | 架構、流程、時序、資料流及生命週期圖；standalone HTML、inline SVG、可選 trace motion，以及 PNG／JPEG／WebP／SVG／WebM 匯出。 | 動畫圖的 WebM 匯出等於完整客製旁白解說影片。 |
| [imagegen](/Users/carl/.codex/skills/.system/imagegen/SKILL.md) | 點陣圖的生成與編輯，包括資訊圖像；簡單圖解可交由 HTML、SVG、CSS 或 canvas 等方式處理。 | 同時提供精確資料圖表、互動模型或影片／旁白管線。 |

## 可支持的結論

- 四份指引已涵蓋多數媒介製作；研究當時提出的候選責任是圍繞理解目標、選型、證據與成效形成一致流程。這是比較後的設計推論；後續使用者選擇記於[技能邊界決策](../issues/06-skill-boundary.md)。
- 此盤點未找到完整的客製旁白影片產製流程。這不代表環境絕對無法製作影片；[媒介範圍決策](../issues/04-media-scope.md)已將完整旁白影片排除於首版之外。若後續另立影片工作，仍須另查所選工具、金鑰、成本與交付格式。
- 研究曾提出三種候選邊界：自成一體、選擇性使用既有能力、固定依賴指定技能。後續定案見[技能邊界決策](../issues/06-skill-boundary.md)；能力盤點本身不構成新增依賴或外部操作授權。

## 後續使用

[技能邊界決策](../issues/06-skill-boundary.md)已採用此盤點；[解說驗收決策](../issues/07-evidence-and-validation.md)已定義選用能力的成果如何檢查，實際試做留到後續建立 skill 時執行。只有當目標環境、媒介或依賴選擇改變，才重查受影響的能力與原始指引。
