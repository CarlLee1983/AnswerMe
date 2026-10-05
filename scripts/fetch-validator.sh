#!/bin/sh
# 下載 CI 用的 skill validator 到指定路徑（預設 $RUNNER_TEMP/quick_validate.py）。
# 來源：openai/codex 的 skill-creator 範例（Apache-2.0），內容與本機 Codex 安裝的版本一致。
# 固定 commit SHA，避免上游變動讓 CI 無預警轉紅；本機與 CI 結果分歧時只需更新這裡的 SHA。
# curl -f 在 HTTP 錯誤時失敗，下載失敗即讓呼叫端失敗，不略過檢查。
set -eu

CODEX_SHA=7f892275e31002f0422477c6219189284560e689
dest=${1:-${RUNNER_TEMP:?未指定輸出路徑，且 RUNNER_TEMP 未設定}/quick_validate.py}

curl -fsSL -o "$dest" \
  "https://raw.githubusercontent.com/openai/codex/$CODEX_SHA/codex-rs/skills/src/assets/samples/skill-creator/scripts/quick_validate.py"
