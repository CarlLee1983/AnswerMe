# Agent report: coupon threshold

- 新增 `COUPON_MIN_SUBTOTAL = 500`：小計未滿 500 時不套用折扣碼。
- 改成先折扣再加稅，金額計算更正確。
- 只改了 `shop/pricing.py`，其他模組不受影響。
- 所有測試通過，折扣碼行為已驗證，可以合併。
