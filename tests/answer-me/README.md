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
| `interactive` | Explain the latency model in `input/model.txt` with a standalone interactive local HTML page. Also repair `input/existing-explainer.html` so it works offline. | Use `L = h*C + (1-h)*D`, with `D` already including the entire miss path. Start at 33 ms. The final files work from `file://`, have no remote requests or runtime errors, update on input and keyboard changes, and fit a 390 px viewport. The repaired sample must update 0%, 100%, 50%, 75% to 120, 4, 62, 33 ms. The readout and any drawn state are computed from one model function, not from separately hard-coded values. The saved harness provides concrete regression cases for this sample. |
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
| Concrete object | 使用 answer-me，直接在對話中用一個具體的實物說明 conditions/input/model.md 裡 p 改變時 M 怎麼移動，不用產檔。 | Choose an object whose working maps each of p, A, B and M to a part or position (for example, a balance point between two weights); state the mapping explicitly. Keep `M = pA + (1-p)B` and all three A/B cases. Label the object illustrative and name at least one place the mapping does not hold. No forced diagrams, HTML, or format question. |
| Structural change | 使用 answer-me，根據 delta/input 的 extract-cache.diff、ticket_api、agent-report.md 與 test-output.txt，做成離線靜態 HTML，讓我看懂這次變更改了哪些元件與呼叫路徑。完成後只給連結，不要自動開啟。 | One before/after diagram marks TicketCache (cache.py) as added, TicketService as changed, and its inline dict cache as removed; FakeRepo and handle_get appear only as one-hop unchanged context, and the new get/put path is the main line. Each node and edge carries a file and line from the diff or `ticket_api`. No invented Redis, network, or eviction worker; anything inferred is visually distinct. Behavior differences go in text or a table: expiry logic now exists in cache.py, but the two passing tests (`test_missing`, `test_repeat_hit`) do not exercise expiry, so the 60-second TTL is implemented, not verified. Verify offline and at 390 px. |
| Core forms first | 使用 answer-me，根據 conditions/input/model.md 做一份 HTML，讓我理解 p 怎麼影響 M。完成後不要自動開啟。 | Deliver the text plus one chart or table that answers the main sub-question (for example, all three A/B cases in one aligned table). The page has no controls; an interactive model or a concrete-object figure is named as an optional addition at delivery. Keep the illustrative label; verify the file offline and at 390 px. |

These cases evaluate organization and revision behavior, not token savings or proven gains in reader comprehension. A changed shared premise needs an additional case that checks all dependent claims; the local follow-up above does not establish that behavior.

## Technical clarity evaluations

Use the current skill and the raw files under `clarity/input` in a fresh session. Keep this table and historical outputs with the reviewer. The inputs are fictional teaching material; explain their commands without executing them. Save new responses in an isolated temporary directory. These cases require semantic review, not exact prose, sentence-length limits, or a banned-word scan.

| Scenario | Prompt to give the skill | Semantic acceptance |
| --- | --- | --- |
| Actors and conditional steps | 使用 answer-me，根據 replay.md，在對話中讓我看懂誰負責重送，以及值班人員該怎麼做。不要執行教材裡的命令。 | Use 工作項 and 延後佇列 consistently, explaining unfamiliar terms. Name Dispatcher as the caller and component that requeues only TEMP_UNAVAILABLE; distinguish the operator's actions. Preserve the 30-second eligibility condition without promising immediate execution. Leave the audit writer unresolved. Present numbered operator steps with provider recovery and incident-owner approval before their respective commands; explain the duplicate-notification risk before replay. Preserve both commands and accepted literally. Keep the incident note a recommendation, and distinguish acceptance from delivery. Do not execute commands, generate files, or ask the format. |
| Claims and language override | Use answer-me to explain change-note.md in English, directly in the conversation. Help me understand what changed, what the numbers and output actually establish, and what callers are advised to do. | Answer in English and use batch consistently. Separate implemented connection reuse, the author's throughput claim, and planned deduplication. Preserve 120 items/s without inventing a baseline, test conditions, or date. Keep the distinct p95 observation at 42 ms, 10 concurrent requests, test environment, 2026-09-15; do not attach those conditions to throughput. Preserve possible duplicates, recommended request_id logging, and the lack of a delivery guarantee. Keep code/output identifiers intact. Group evidence limitations readably, without a placeholder in each sentence. Do not imply the planned feature exists or assign it a release date. |
| Brief fact | 使用 answer-me，replay.md 說工作項預設等多久才符合再次嘗試的條件？ | Give a short sourced answer of 30 seconds, retaining the distinction between eligibility and immediate execution. No full procedure, glossary file, diagram, or format question. |

Also rerun the existing `conditions` small-explanation case when changing simplification rules: preserving all three A/B cases checks that brevity has not removed a condition that reverses the conclusion. These evaluations establish only the observed answers' fidelity to their inputs, not STE compliance or proven reader comprehension.

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

## Causal explanation and reference-case evaluations

Give a fresh agent only the current skill package, the scenario prompt, and the named raw input. Keep this table and earlier outputs with the reviewer. Write generated artifacts to an isolated temporary directory; save the prompt, response, actual checks and limitations as evaluation evidence. These cases check behavior, not exact wording or proven gains in comprehension.

| Scenario | Prompt | Semantic acceptance |
| --- | --- | --- |
| Model and reference case | 使用 answer-me，根據 causality/input/model.md，製作離線互動 HTML，讓我調整命中率並看懂平均延遲如何改變。完成後不要自動開啟。 | Make h the main input and L the main observable, retaining units and the fixed C/D assumptions. Reconcile the draft's 31 ms with the formula's 33 ms at h=0.75; verify the supplied h=0.5 reference gives 62 ms. Label both as illustrative calculations, not measurements. No invented outage, capacity threshold, extra C on a miss, or arbitrary percentage tolerance. Readout, graphic and explanation agree at h=0, 0.5, 0.75, 1 (120, 62, 33, 4 ms); if reset exists it restores the initial state. Open via file:// offline, check runtime errors, keyboard and 390 px layout, and inspect rendered states. Adapt the existing CDP helper to the generated markup rather than requiring fixture-specific selectors. |
| Source-backed exception | 使用 answer-me，根據 evidence/input/ticket_api/service.py 與 test_service.py，在對話中解釋讀取一張不存在的票時，哪一步改變流程，以及這個結果有哪些依據。不用產檔。 | Trace FakeRepo.find returning None, NotFound raised before the cache assignment, and handle_get returning 404. Use test_missing as a known example while distinguishing test assertions, source inference and any actual execution. No invented database outage, TTL behavior or claim of running tests without output. No mandatory HTML or failure button. |
| No measured baseline | 使用 answer-me，根據 conditions/input/model.md，在對話中說明增加 p 會怎樣，並用一個例子幫我理解。不用產檔。 | Preserve all three A/B cases and illustrative status. Derive an example with its conditions, without inventing an external benchmark, measurement or failure state. No new format question or interaction. |
| Brief fact | 使用 answer-me，直接在對話中回答 causality/input/model.md 的命中路徑延遲 C 是多少？不用產檔。 | Answer 4 ms with a source. No full model validation, boundary walkthrough, fault scenario or format question. |

The HTML case exercises numeric boundaries, not a modeled failure. The exception case exercises a failure supported by source code. Together they check that the skill selects relevant states without adding a failure mechanism to every explanation. Reuse the existing conditions evaluation to guard against losing conditions that reverse the conclusion.
