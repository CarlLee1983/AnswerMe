# Answer-me evaluation samples

These inputs and outputs are saved historical samples. Passing the browser check confirms that the saved HTML still behaves as recorded; it does **not** validate a newly generated answer or the current skill instructions.

## Reproduce the saved browser check

Requires Node.js 22 or newer (native `WebSocket` and `fetch`) and headless Google Chrome or Chromium. Set `CHROME_BIN` to the browser executable if it is not in a standard macOS or system location or on `PATH`. From this directory:

```sh
node browser/verify.mjs
```

The optional first argument is a fixture root with the same `interactive/input` and `interactive/output` layout. The optional second argument is an artifact directory; by default the script creates a fresh temporary directory and prints its path. It opens HTML with `file://`, emulates offline mode, and needs no server, network access, or installed packages. New screenshots and JSON results go only to the artifact directory. The checked-in `browser/verification.json` and `browser/broken-baseline.json` preserve the earlier run as evidence.

The check covers ten numeric cases, four presets, keyboard input, a 390 px layout, and four repaired-page values. It asserts that both final pages make no HTTP(S) requests and have no runtime exceptions. It also opens the saved broken input, confirms its value remains stuck after moving the slider, and detects its remote script request. A failure exits with a nonzero status.

## Fresh independent evaluations

Use each input directory as the only source material for a new answer. Compare the new answer with the semantic criteria below, rather than matching the saved prose or treating the saved browser result as a new run.

Give the evaluating agent only the skill, a scenario prompt, and its raw inputs. Keep the acceptance column and saved outputs with the reviewer so they cannot supply the answer to the evaluating agent.

For prompts without an output format, capture the first response, then provide a simulated user choice and continue the same session. Evaluate the resulting artifact as well as the format question. For the existing `evidence` and `conditions` content evaluations, reply “直接在對話中回答” if asked; the explicit HTML requests in `interactive` need no format round-trip.

| Scenario | Prompt to give the skill | Semantic acceptance |
| --- | --- | --- |
| `evidence` | Explain the ticket read flow from `input/ticket_api`; then review `input/change.diff`, `input/test-output.txt`, and `input/agent-report.md`. For a separate request, explain the cross-process lock from `input/design-note.md` (which is absent). For a simple request, define HTTP 404. | Cite available source lines; separate code behavior, documentation claims, and test evidence. State that only `test_missing` is shown passing. Do not claim deployment, full-suite success, concurrency safety, or verified TTL. Request the absent design note without inventing its content. Answer the 404 request briefly. |
| `interactive` | Explain the latency model in `input/model.txt` with a standalone interactive local HTML page. Also repair `input/existing-explainer.html` so it works offline. | Use `L = h*C + (1-h)*D`, with `D` already including the entire miss path. Start at 33 ms. The final files work from `file://`, have no remote requests or runtime errors, update on input and keyboard changes, and fit a 390 px viewport. The repaired sample must update 0%, 100%, 50%, 75% to 120, 4, 62, 33 ms. The saved harness provides concrete regression cases for this sample. |
| `conditions` | Explain how changing `p` affects `M` in `input/model.md`. | State `M = pA + (1-p)B` and change per unit `p` as `A-B`. Retain all three cases: **A < B** means M falls as p rises; **A > B** means M rises; **A = B** means M stays constant. For A=20, B=80, p=0.5 gives 50 ms and p=0.6 gives 44 ms. Label the model illustrative, not measured. |

The `output` directories show one earlier response for each scenario, including four evidence response variants. For a fresh evaluation, regenerate outputs independently and check their claims against the provided inputs. The browser script is specific to the saved interactive HTML structure; adapt selectors and assertions if a fresh answer uses different markup while preserving the same behavior criteria.

## Output-format evaluations

Use `conditions/input/model.md` as the raw material and an isolated temporary directory for any new files. These scenarios check the format decision and actual delivery, not exact wording. Give the agent only the prompt, skill, and raw material; keep the expected behavior with the reviewer.

| Scenario | Prompt / next user turn | Semantic acceptance |
| --- | --- | --- |
| Unspecified format | 使用 answer-me 幫我理解 model.md 中，改變 p 時 M 為什麼可能增加也可能減少，整理成容易理解的解說。 Then: 請做成 Markdown 文件。 | First offer HTML, Markdown file, and conversation with a recommendation; a core summary is allowed. After the choice, create a readable `.md` file and link it without asking the format again. Preserve all three cases from `conditions`. |
| Explicit HTML | 使用 answer-me，把 model.md 做成可離線開啟的 HTML 解說，只要靜態文字與圖解。 | Create a real `.html` file without asking the format or adding controls. Check the rendered content offline, then open the final file once for the user on an available local desktop (macOS: `open` with a safely quoted absolute path). Retain the artifact link; distinguish opener success from rendering verification. |
| HTML without auto-open | 使用 answer-me，把 model.md 做成可離線開啟的 HTML 解說；完成後只給連結，不要自動開啟。 | Create and verify the HTML, deliver its link, and do not launch a desktop opener. Offline verification remains required; it can use a headless browser. |
| HTML without desktop access | 使用 answer-me，把 model.md 做成可離線開啟的 HTML 解說。此次環境沒有使用者桌面可用。 | Deliver the file and report the desktop-opening limitation without blocking delivery or repeatedly retrying. Do not claim it was opened for the user; report rendering verification separately. |
| Explicit conversation | 使用 answer-me，在對話中用文字解釋 model.md，不用產檔。 | Answer directly without a format question or file. |
| Simple fact | 使用 answer-me，model.md 的 p 範圍是多少？ | Give a brief sourced answer, without a format question or file. |
| Delegated choice | 使用 answer-me 解釋 model.md，輸出格式由你決定。 | State the selected document format, create that file, and provide its path without a format question. |

When the question channel returns no answer and cannot accept a later reply, check that the agent states its format assumption and completes a document. An asynchronous question still awaiting a reply is not the same condition.

## Content organization and follow-up evaluations

Use the current skill package and only the raw inputs named below. Generate into a fresh temporary directory. Keep the acceptance criteria and previous outputs with the reviewer; continue follow-ups in the same evaluation session.

| Scenario | Prompt / next user turn | Semantic acceptance |
| --- | --- | --- |
| Calls and branches | 使用 answer-me，根據 evidence/input/ticket_api，做成離線靜態 HTML，讓我看懂 TicketService 與 FakeRepo 之間誰先呼叫誰、首次與再次讀取同一張票的差別，以及找不到票時怎麼回覆。完成後只給連結，不要自動開啟。 | Lead with the core answer; group sections by a reader question. Use a sequence view for ordered calls, with branches or an aligned comparison for hit/miss/not-found. Preserve actual method names and source links. A hit skips FakeRepo.find; a missing row raises NotFound and handle_get returns 404. Distinguish README's 60-second TTL claim from service.py, which has no expiry logic. Do not invent a network or database tier or test results. Reuse the article starter without changing the shipped template; verify the new file offline and at 390 px, with no unnecessary controls or desktop opener. |
| Local follow-up | After the first answer, record a copy and add a distinctive reader note to an unrelated section. Then: 我只是不懂找不到票時，為什麼沒有寫入快取。請在同一份 HTML 補清楚這一段。 | Read the current artifact; explain the exception occurs before the cache assignment, citing the raw code. Preserve the reader note and unrelated sections, layout and sources. Recheck the edited content and any affected navigation. Evaluate the file diff, not merely the agent's claim that it made a local edit. |
| Small explanation | 使用 answer-me，直接在對話中說明 conditions/input/model.md 的 p 增加時 M 會怎麼變，不用產檔。 | Retain all three A/B cases and illustrative status. A compact explanation or aligned table is enough; no forced diagrams, HTML, or format question. |

These cases evaluate organization and revision behavior, not token savings or proven gains in reader comprehension. A changed shared premise needs an additional case that checks all dependent claims; the local follow-up above does not establish that behavior.

## Default HTML style evaluations

Use the updated skill package (including its referenced guide and templates), a prompt below, and raw `conditions/input/model.md` in a fresh session. Keep these acceptance criteria and saved outputs with the reviewer. Use a new output directory and do not alter the shipped templates. These evaluations check style selection as well as actual generation; browser checks on the starter files alone cannot establish skill behavior.

| Scenario | Prompt | Semantic acceptance |
| --- | --- | --- |
| Default reading style | 使用 answer-me，把 model.md 做成離線 HTML，說明改變 p 如何影響 M。完成後只給連結，不要自動開啟。 | Use the article starter and default palette without asking a style question. Replace illustrative template content with the supplied model and source. Preserve all three conditions from the `conditions` evaluation. Deliver and verify a standalone HTML; do not launch a desktop opener. |
| Requested slide style | 使用 answer-me，把 model.md 做成逐頁 HTML 簡報，說明改變 p 如何影響 M。請使用深色背景與橘色重點色；完成後只給連結，不要自動開啟。 | Use the slide structure while overriding the default palette. One point per page; source and all three conditions retained. Verify offline navigation, keyboard, mobile layout, all pages in print and without JavaScript. No design reconfirmation or desktop opener. |

To check the shipped starter files from the repository root:

```sh
node tests/answer-me/browser/verify-templates.mjs
```

Uses the same Node.js 22+, Chrome/Chromium and `CHROME_BIN` setup as the saved-page check. It checks consistent palette tokens, Google Fonts family stacks with local fallbacks, offline loading (only the exact optional Google Fonts stylesheet request is allowed), desktop and 390 px layout, slide buttons/keyboard/bounds, keyboard handling inside interactive elements, print visibility, custom print colors and no-JavaScript readability. It also exports print PDFs and checks one page per starter slide. The first optional argument is a directory containing `article.html` and `slides.html`; the second is the artifact directory. Screenshots, PDFs and JSON go to a new temporary directory by default. Inspect rendered output for text or diagram clipping that width and page-count assertions cannot detect. A shared palette assertion is for the shipped defaults; customized outputs need assertions appropriate to their requested palette.
