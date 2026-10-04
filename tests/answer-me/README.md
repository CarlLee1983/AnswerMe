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

| Scenario | Prompt to give the skill | Semantic acceptance |
| --- | --- | --- |
| `evidence` | Explain the ticket read flow from `input/ticket_api`; then review `input/change.diff`, `input/test-output.txt`, and `input/agent-report.md`. For a separate request, explain the cross-process lock from `input/design-note.md` (which is absent). For a simple request, define HTTP 404. | Cite available source lines; separate code behavior, documentation claims, and test evidence. State that only `test_missing` is shown passing. Do not claim deployment, full-suite success, concurrency safety, or verified TTL. Request the absent design note without inventing its content. Answer the 404 request briefly. |
| `interactive` | Explain the latency model in `input/model.txt` with a standalone interactive local HTML page. Also repair `input/existing-explainer.html` so it works offline. | Use `L = h*C + (1-h)*D`, with `D` already including the entire miss path. Start at 33 ms. The final files work from `file://`, have no remote requests or runtime errors, update on input and keyboard changes, and fit a 390 px viewport. The repaired sample must update 0%, 100%, 50%, 75% to 120, 4, 62, 33 ms. The saved harness provides concrete regression cases for this sample. |
| `conditions` | Explain how changing `p` affects `M` in `input/model.md`. | State `M = pA + (1-p)B` and change per unit `p` as `A-B`. Retain all three cases: **A < B** means M falls as p rises; **A > B** means M rises; **A = B** means M stays constant. For A=20, B=80, p=0.5 gives 50 ms and p=0.6 gives 44 ms. Label the model illustrative, not measured. |

The `output` directories show one earlier response for each scenario, including four evidence response variants. For a fresh evaluation, regenerate outputs independently and check their claims against the provided inputs. The browser script is specific to the saved interactive HTML structure; adapt selectors and assertions if a fresh answer uses different markup while preserving the same behavior criteria.
