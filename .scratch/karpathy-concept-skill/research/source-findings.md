# Karpathy 貼文來源考證：理解模型輸出的表達形式

## 來源與查證範圍

- 原貼文：[Andrej Karpathy，X 貼文 `2105819303471976479`](https://x.com/karpathy/status/2105819303471976479)，第三方擷取的 X 資料標示發表時間為 **2026-10-02 00:37 UTC**，作者為 `@karpathy`，含一張圖。研究時 X 原頁無法直接讀取（網頁工具回傳錯誤）；X 的[公開 syndication 端點](https://cdn.syndication.twimg.com/tweet-result?id=2105819303471976479&lang=en)僅回傳 `{}`。下述貼文內容取自 [FxTwitter 對同一貼文 ID 的轉送資料](https://api.fxtwitter.com/karpathy/status/2105819303471976479)；這是**第三方傳輸的原貼文資料**，不是直接由 X 原頁驗證，仍有擷取不完整或轉送錯誤的風險。
- 轉送資料指向的[附圖原始檔（X 圖片網域）](https://pbs.twimg.com/media/HTlaHqgbwAAS1lv.png?name=orig)可讀。圖像是一頁 ASD-STE100 速覽，包含文件結構、句型、動詞形式、字典、篇幅限制及沿革；它**不是**四種輸出形式的比較圖。圖內個別規則仍應以[標準制定者的文件](https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf)為準。

## 貼文實際主張

1. Karpathy 預期模型承擔更多執行工作後，人類會花更多時間**監督並理解模型產出**。[原貼文](https://x.com/karpathy/status/2105819303471976479)；[擷取資料](https://api.fxtwitter.com/karpathy/status/2105819303471976479)。
2. 他依序分享四種幫助理解的輸出：請模型用 **ASD-STE100** 風格解釋（標準太嚴時可要求約「80%」）、畫**圖像／圖解**、產生可互動的 **HTML 網頁**、製作特定主題的**客製解說影片**。他認為影片最有前景，並說這已開始可行；文中以 3Blue1Brown 風格與 ElevenLabs 旁白為例，同時指出後者需要 API 金鑰或其他方案。[原貼文](https://x.com/karpathy/status/2105819303471976479)；[擷取資料](https://api.fxtwitter.com/karpathy/status/2105819303471976479)。
3. 他提出的較大判斷是：智能與程式碼產能增加後，可以為單一問題製作大型、客製、**用後可丟棄**的軟體成果（如網頁或影片），即使過去不值得投入製作成本。[原貼文](https://x.com/karpathy/status/2105819303471976479)；[擷取資料](https://api.fxtwitter.com/karpathy/status/2105819303471976479)。
4. [ASD-STE100 官方 FAQ](https://www.asd-ste100.org/STE_faq.html)確認它是以寫作規則與受控字典組成的技術文件標準；官方也說標準本身並非一般用途的英文寫作規範，但其短句、單一主題、主動語態等原則可借用。因此「80%」是 Karpathy 的非正式提示方式，**不是**標準制定者定義的符合度、認證或驗證尺度。[Karpathy 原貼文](https://x.com/karpathy/status/2105819303471976479)；[官方 FAQ](https://www.asd-ste100.org/STE_faq.html)。

## 對可重用工作流程的推論（不是作者逐字要求）

- 先確定使用者要**理解或檢查什麼**，再按理解收益選一種表達：精簡文字適合直接事實；圖適合結構與關係；互動頁適合探索、比較或操作；影片適合需要時間順序與旁白的說明。貼文呈現由文字到影片的偏好，但**沒有**規定每次都製作四種成果，也未定義自動選型規則。[原貼文](https://x.com/karpathy/status/2105819303471976479)；[擷取資料](https://api.fxtwitter.com/karpathy/status/2105819303471976479)。
- 若整理成技能，應以「協助使用者看懂模型輸出」為任務邊界；保留來源、假設和不確定處，讓精美圖表、網頁或影片不掩蓋需審查的事實。這是針對作者的監督與理解主題所作的**設計推論**，不是貼文明示的步驟。[原貼文](https://x.com/karpathy/status/2105819303471976479)；[擷取資料](https://api.fxtwitter.com/karpathy/status/2105819303471976479)。

## 未解歧義

- 貼文沒有定義何時該升級為圖、網頁或影片，也沒有提供成效測量、成本門檻、媒體製作工具或驗證方法。這些需要後續技能設計自行確立，不能歸於作者。[原貼文](https://x.com/karpathy/status/2105819303471976479)；[擷取資料](https://api.fxtwitter.com/karpathy/status/2105819303471976479)。
- 貼文沒有主張將 ASD-STE100 一律套用於所有回覆，也沒有宣稱模型產生的文字即符合該標準。官方[AI 與 STE 相關說明](https://www.asd-ste100.org/STE_downloads.html)提醒 AI 文字可能看似符合 STE，實際上未正確套用規則與字典。
