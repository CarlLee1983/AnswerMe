# 檢查與回歸演練

## 快速檢查

需求：Python 3.10+、PyYAML，以及已安裝的 `skill-creator/scripts/quick_validate.py`。

```sh
python3 -m venv "$HOME/.cache/answer-me/check-env"
"$HOME/.cache/answer-me/check-env/bin/python" -m pip install -r requirements-check.txt
"$HOME/.cache/answer-me/check-env/bin/python" scripts/check.py
```

若目前 Python 已有 PyYAML，可直接執行 `python3 scripts/check.py`；建立環境只是缺少依賴時的一次性準備。

檢查器優先使用 `SKILL_VALIDATOR` 指定的檔案，否則使用 `${CODEX_HOME:-~/.codex}/skills/.system/skill-creator/scripts/quick_validate.py`。沒有 validator 或 PyYAML 時會失敗並提示設定，不略過檢查。這沿用 Codex 安裝中的驗證器；乾淨 checkout 仍須先準備上述檢查依賴，沒有將其複製進技能。

快速檢查涵蓋 skill frontmatter、`agents/openai.yaml` 必要顯示欄位，以及專案文件的行內相對檔案連結。外部網址、絕對路徑、頁內 anchor 及歷史演練產物中的來源連結不在連結檢查範圍；它不驗證解說語意或使用者理解。

## 提交檢查

```sh
sh scripts/install-hooks.sh
```

安裝器只設定本 repository 的 `core.hooksPath`，遇到既有 hooks 路徑或啟用的 hooks 會保留並停止。pre-commit 呼叫同一檢查器的 `--staged` 模式：從 Git index 建立暫存快照，檢查即將提交的內容，避免未暫存的修正掩蓋待提交錯誤。

Hook 預設使用 `.venv/bin/python`（若存在），否則 `python3`；可用 `ANSWERME_PYTHON` 指定已備妥依賴的 Python，例如 `export ANSWERME_PYTHON="$HOME/.cache/answer-me/check-env/bin/python"`。若本次是首次安裝，移除設定可停用：`git config --local --unset core.hooksPath`。未來 checkout 須執行安裝命令；Git 不會自動啟用版本庫內的 hooks。

## 行為與瀏覽器驗證

技能行為有變更時，依[演練說明](../tests/answer-me/README.md)用原始材料重新產出答案，再檢查語意及 HTML。已保存的範例可驗證瀏覽器檢查程式與既有成果，不能證明更新後的技能仍會產生相同品質。

檢查器或 hook 改動時，執行：

```sh
python3 -m unittest discover -s tests -p 'test_checks.py'
```
