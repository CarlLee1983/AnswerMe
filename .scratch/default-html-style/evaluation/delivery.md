# Delivery

- Article: [article.html](article.html)
- Five-page dark/orange presentation: [slides.html](slides.html)
- Source: `tests/answer-me/conditions/input/model.md` (linked from both files)

Both outputs explain the supplied weighted-average model and distinguish its calculated examples from product measurements. The interactive controls cover `p` in 0–1 and `A`, `B` in 0–100 ms. The direction explanation changes for `A < B`, `A > B`, and `A = B`.

## Verification

Raw browser observations: [verification.json](verification.json). Chrome opened each artifact as a `file:` URL with network requests blocked. Both began at `M = 50.0 ms`; setting `p = 1` gave 20 ms for `A = 20, B = 80` and 80 ms for reversed times; equal 50 ms paths stayed at 50 ms. No runtime errors or remote requests occurred. At 390 px, neither document overflowed horizontally. The presentation's buttons and Home/End navigation reached the expected pages; all five slides were visible with JavaScript disabled and in print media, with controls hidden in print. The article and presentation were visually inspected at desktop and mobile sizes, including the interactive slide. Screenshots are in this directory.

Limits: Print media visibility and palette were checked in the browser; no physical printer output was inspected. The user explicitly requested links only and no automatic desktop opening, so no desktop `open` command was run.
