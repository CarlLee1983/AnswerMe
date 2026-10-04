# 把 Karpathy 的解說概念轉成可重用 skill

Label: wayfinder:map
Status: resolved

## Destination

釐清同時支援「概念學習」與「成果審視」的解說 skill：確定使用情境、媒介範圍、選型行為、技能邊界與驗收方式，使後續建立 skill 時不必再猜測關鍵需求。

地圖完成的條件是所有範圍內的決策票已解決，且下方未知已釐清或明確排除；建立、安裝與驗證實際 skill 屬於後續工作。

## Notes

- 使用者已確認：本輪先完成決策地圖；未來 skill 同時支援概念學習與成果審視。
- 兩張研究票與五張產品決策票均已解決，沒有尚待決定的範圍內問題。規劃階段沒有建立、安裝或執行驗證 skill；使用者後續確認的實作成果另記於[實作與驗證紀錄](../answer-me-implementation/verification.md)。
- 每次先讀本地圖，再依 `docs/agents/issue-tracker.md` 掃描本目錄的 `issues/`：依編號取第一張 `open` 且所有阻擋票皆 `resolved` 的票，工作前設為 `claimed`。以票名連結溝通，不用裸編號。
- 沿用 `wayfinder`；對話決策使用 `grilling` 與 `domain-modeling`，研究使用 `research`。規劃 skill 的規格時參考 `skill-creator` 與 `writing-for-agents`。這些是規劃工作指引；產物的依賴關係以技能邊界決策為準。
- 每次最多解決一張非研究票；HITL 票須由使用者參與決定，未確認的選擇保持未定案。
- 原始想法來自 [Karpathy 貼文](https://x.com/karpathy/status/2105819303471976479)。作者主張、查證限制與本案推論由來源研究票承載。
- 討論使用繁體中文。
- 目前目錄未初始化 Git。依已配置的本地 Markdown tracker 保存研究與票，不為研究建立 Git repository、分支或 commit。

## Decisions so far

<!-- 只放已解決票的名稱連結與一句摘要；詳細答案留在票內。 -->

- [原貼文有哪些可採用的主張與限制？](issues/01-source-concept.md)：已保存作者主張、設計推論與來源取得限制，原文未定義本案的選型及驗收規則。
- [現有解說技能能提供哪些能力，缺少哪些環節？](issues/02-existing-capabilities.md)：已盤點四份指引的媒介能力；動畫圖匯出不足以承諾完整旁白影片。
- [兩種用途各要讓誰理解什麼，才算有幫助？](issues/03-understanding-goals.md)：以有開發背景的使用者為首批受眾，採用陌生 repo 與 agent 變更作代表情境，支援理解與證據判斷。
- [首版支援哪些媒介、語言與交付環境？](issues/04-media-scope.md)：首版以繁體中文提供文字、圖解與可離線互動的 HTML，並確定漸進交付、成本與工具受限時的處理原則。
- [Skill 如何選擇解說形式，何時交回使用者決定？](issues/05-selection-behavior.md)：依理解障礙自動選型、尊重指定形式，並確定詢問、調整與停止條件。
- [新 skill 自己負責什麼，如何運用既有能力？](issues/06-skill-boundary.md)：定名 `answer-me`，首版面向 Codex，核心獨立且按需運用既有能力，來源保存在專案內。
- [如何驗證解說可信，而且達到理解目標？](issues/07-evidence-and-validation.md)：已確定內容依據、各媒介檢查、可選理解回饋及後續建立時的代表驗證案例。

## Not yet specified

無。試解說可能暴露的理解障礙，已由[驗收決策](issues/07-evidence-and-validation.md)的代表案例與回饋機制承接；實際試做在後續建立 skill 時執行。

## Out of scope

- 完整旁白影片不納入首版；此範圍決定記於[首版支援哪些媒介、語言與交付環境？](issues/04-media-scope.md)。
- 本輪建立、安裝、發布或修改任何解說 skill，以及修改現有視覺化技能；使用者選擇先完成決策地圖。
- 在規劃期間製作正式網站、影片、旁白服務整合，或購買／配置付費服務。便宜的討論樣稿只在後續決策確實需要時另開 prototype 票。
- 建立通用課程平台、知識庫產品或長期內容管理系統；本案聚焦可重用的解說 skill。
