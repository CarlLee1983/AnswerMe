# 02: staged 文件提醒

**What to build:** 維護者提交時，若即將提交的變更動到技能資料夾，卻沒動到 README 或介紹頁，pre-commit 印出一則提醒，但不阻擋提交。提醒只依 Git index 判斷，不受工作區未暫存的修改影響。

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] 檢查器的 staged 模式在上述條件下於 stderr 輸出提醒，結束碼不因提醒改變
- [ ] 非 staged 模式不輸出此提醒
- [ ] 測試涵蓋：只動技能 → 有提醒且結束碼 0；技能加 README → 無提醒；技能加介紹頁 → 無提醒；只動文件 → 無提醒；技能變更未 stage → 無提醒；技能已 stage 但 README 修改未 stage → 有提醒
- [ ] 測試沿用既有暫存 git repo 加 subprocess 的模式
- [ ] 檢查說明文件補上提醒的條件與「不阻擋」的性質
- [ ] 既有檢查測試全數通過
