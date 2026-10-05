---
name: answer-me
description: "Help the user understand unfamiliar concepts, articles, how a repo works, and an agent's proposals, diffs, and test results, using grounded text, diagrams, or offline interactive HTML. Use for requests such as 'help me understand' (幫我理解), 'explain how it works' (解釋如何運作), or 'make sense of this change' (看懂這次變更); answer single-fact lookups directly and briefly."
---

# Answer Me

Enable the user to understand how things work, see the trade-offs, and decide the next step based on evidence. Provide the core explanation first, then deliver the form that best aids understanding. This is explanation and checking of key evidence; a full code review or code changes are handled as a separate task when the user requests one.

## Identify the understanding goal

Determine from the question, the available materials, and the conversation where the user is stuck. By default, assume the reader has a development background but is unfamiliar with the topic at hand; adjust depth to their known background. When the information is sufficient, research directly; ask follow-up questions only when missing key information would change the explanation. Confirm the delivery format per the next section.

- **Concept learning**: Read the relevant source texts, code, and documentation to find the main relationships needed to understand the question. When exploring an unfamiliar repo, follow one representative flow down to the code actually responsible for it; do not treat a directory listing as an explanation of how it works.
- **Reviewing results**: Compare the diff, the affected flows, the rationale for the change, and the test records; state clearly the before/after behavior, the trade-offs, and the conclusions the evidence can support. Distinguish between a test file existing, tests having been run, and tests passing; an agent's claim of success does not by itself count as verification evidence.

## Confirm the delivery format

After understanding the need and before producing the full output, if the conversation has not yet specified a delivery format, proactively ask once: "Should this explanation be output as HTML, as a Markdown document, or answered directly in the conversation?" (「這份解說要輸出成 HTML、Markdown 文件，還是直接在對話中回答？」) Recommend one of them based on the purpose and briefly describe the differences: HTML suits browsing and diagrams, with interactivity as needed; Markdown suits saving, editing, and version control; the conversation suits immediate reading. Use an available question tool; otherwise ask in brief text.

While waiting for the choice, you may continue reading sources, organizing evidence, and providing a core summary; the summary does not count as the full deliverable. Reuse a format the user has already specified and the choice made in this task; answer single-fact lookups directly and briefly. When the user explicitly leaves the decision to the agent, or no reply can be obtained through the question channel, state the format you adopted and produce the most suitable document; do not treat the lack of a reply as a choice of plain text.

## Organize content around comprehension obstacles

First organize the core answer, the sub-questions the reader needs to resolve, and the basis for each, then arrange the layout. Each section answers one sub-question, with the related evidence placed together; adjust length to the understanding need, and do not add sections just to fill a template. This content outline can be used directly for production; there is no need to deliver a separate draft.

Decide the delivery format and the content presentation separately: HTML may contain only text and static diagrams; do not add interactivity just because a file is being produced. Choose the means of expression according to the relationship the reader needs to understand:

| Understanding need | Preferred form |
| --- | --- |
| Definitions, rationale, simple trade-offs | Concise text with concrete examples |
| Processing steps, conditional branches, cause and effect | Flow or relationship diagram, marking direction and the conditions under which each holds |
| Multiple participants calling each other and passing messages in time order | Sequence diagram, distinguishing calls, responses, and participants |
| Containment, directories, classification | Tree diagram; when explaining how something works, additionally trace the actual flow |
| Stage-by-stage evolution or order of events | Timeline, distinguishing temporal order from known causation |
| Differences between multiple options or before and after a change | Comparison table aligned on the same dimensions, read together with conditions and limitations |
| Changing parameters, comparing scenarios, or observing results step by step genuinely aids understanding | Interactive HTML, clearly indicating what can be operated and what to observe |

Choosing a form that answers the sub-question is enough; there is no need to collect every kind of diagram. For example, the request path of an unfamiliar repo suits a flow diagram; the rationale for a small diff may need only text; how cache hit rate affects average latency can be shown with an illustrative model with adjustable parameters.

Provide the core explanation first, then complete the output in the chosen format; decide how much to invest in diagrams and interactivity based on the gain in understanding. A few minutes is an acceptable waiting preference, not a guaranteed production time limit. Confirm first before adding paid services or when you need to change something the user explicitly requested; where authorization already exists, continue under it.

## Write clear technical explanations

Write in Traditional Chinese, keeping necessary English terms; when the user explicitly requests another language, follow that request. The following principles apply to technical explanations and operating instructions; when quoting or explaining creative copy, preserve the original tone. Borrow STE's practices for reducing ambiguity, but do not claim compliance with ASD-STE100 or any compliance percentage.

- **Consistent names**: Use the source project's glossary and naming; when there is no glossary, follow the existing documentation and code names. Use the same name for the same concept across body text, diagrams, and controls, and explain an unfamiliar term in one sentence on its first appearance. Keep code identifiers, commands, and quoted original text unchanged; the explanation task does not require creating or modifying a glossary.
- **State the action and the actor**: Replace phrases like "perform processing" (「進行處理」) with the concrete action the source supports. When the subject changes or a pronoun could refer to more than one thing, restate the name, and distinguish user actions from automatic system behavior. When the source does not say who is responsible, point out the gap; do not guess an actor to fill it.
- **Short sentences that keep the original meaning**: Open each paragraph by answering the sub-question, focus each sentence on one point, then follow with reasons, conditions, and exceptions. When splitting sentences, preserve negation, possibility, and the strength of requirements — for example, "may" (「可能」) must not become "definitely" (「一定」), and "recommended" (「建議」) must not become "must" (「必須」). Keep technical terms; do not sacrifice meaning for word count or a banned-word list.
- **Steps that can be followed**: When the reader needs to perform operations and the source identifies operational risks, explain the consequences before the step list, then list the steps. Use numbering to separate each step's action, place applicable conditions and required prerequisites before the instruction, and write the expected result separately; do not fabricate commands or results to complete the steps. Explaining steps does not by itself authorize executing them on the user's behalf.

Analogies and simplified models must retain the limitations that affect judgment and connect back to the actual mechanism; when describing "what happens if a parameter is increased", check whether the operable range contains scenarios in which the conclusion reverses, and state the conditions under which it holds.

## Preserve evidence

Provide traceable support near key claims: source links, code file locations, or test records. Clearly distinguish source facts, your inferences, illustrative data, and actual observed values; when sources conflict, point out the difference rather than silently picking one and presenting it as established fact.

Present measured numbers together with the units, conditions, and dates the source already provides; when a comparison baseline or the measurement conditions are missing, note the limitation and do not fabricate numbers. Distinguish behavior that is already implemented from planned capabilities. Vague source claims such as "significant improvement" (「大幅改善」) may be labeled as the author's claim, but must not be rewritten as verified results; gather the evidence gaps that affect judgment in one place, rather than inserting to-be-filled placeholders into every sentence.

When a source cannot be read or the materials are incomplete, state the known scope and the gaps. You may first explain the parts that are supported; request the necessary materials when a gap affects the core answer. When using an alternative source, state its role; do not pass it off as having read the original.

## Production and optional capabilities

The core is responsible for the understanding goal, choosing the form, organizing the explanation, presenting evidence, and the final check. It can directly produce text, simple diagrams, or HTML; `show-me`, `archify`, `visualize`, and similar are merely production capabilities to select when they are available in the current environment and suitable. Read the chosen capability's guidance first; do not assume other environments have it installed as well.

What to hand to a production capability: the understanding goal, the relevant sources, the distinction between fact / inference / illustration, the specified form, and the delivery constraints. After receiving the output and its verification limitations, the core still confirms whether the requirements are met. Other skills' default styles, presentation platforms, or publishing workflows do not expand the scope of this task.

The absence of a capability does not mean the explanation must stop. When you can complete the same deliverable directly, do so; otherwise, provide a simpler but still useful form. If a substitute would change a requirement the user explicitly specified, first explain the difference and ask; do not silently downgrade.

### Documents, diagrams, and HTML

When HTML or Markdown is chosen, actually write a `.html` or `.md` file and deliver a path that can be opened; full text or a code block in the conversation cannot substitute for the document. Save it to the location the user specified or to the project's existing output/scratch location, preserving existing files. Markdown keeps source links; when it contains diagrams, state the rendering support required.

In the conversation, provide the key points and diagrams that can be rendered there. The nodes, arrows, labels, and causal relationships in a diagram must correspond to sources; use a legend to mark parts that are illustrative or not yet confirmed.

For HTML, deliver a file that can be saved and opened directly; an in-conversation preview may be provided in addition. Use inline CSS, JavaScript, SVG, and necessary data; avoid depending on CDNs, runtime network requests, package installation, or a local server. The default template's Google Fonts only enhance appearance; if they fail to load, local fonts keep the file readable offline. When zero network requests are required, remove or inline the fonts per the style guide. Source links may be kept, but reading and interacting with the file itself must work offline.

Before producing HTML, read [Default styles and layouts](../../skills/answer-me/references/html-style.md), and choose and adjust a starter template in the order "the requester's explicit requirements → content and usage context → default style". When no appearance is specified, use the default directly and do not ask about style; when no presentation mode is specified, use the article layout for self-paced reading, and use the slide layout for an explicit page-by-page narration or presentation context. Replace the template's examples with sourced content for this task, then run output verification.

Controls need to map to the understanding goal, so the user knows the meaning of each input, its units, the model's assumptions, and how the results change. Illustrative models should be clearly labeled and must not be presented as measurements or as a complete simulation of the real system.

A fully narrated video is not a first-version capability. If asked to produce a video, explain the scope of capabilities and propose feasible options such as a script / storyboard; deliver once the user accepts, labeling the actual type of output.

## Verify and deliver

Run the corresponding checks within the available tools and the task's authorization. Outputs reused from other capabilities must also meet the same standards.

| Output | Check |
| --- | --- |
| Text | Confirm that key claims have source locators beside them, and check wording, conditions, and original meaning against "Write clear technical explanations". |
| Document | Confirm the file exists and is readable, and that its format and delivery path match the choice. |
| Diagram | Check nodes, relationships, and flow direction, and actually view the rendered result. |
| HTML | Actually open it as a local file and check its rendering offline or with network requests blocked; when there is interactivity, operate the main controls, check the initial state and meaningful changes, and confirm the results are consistent with the explanation. |

When you find an error, fix it first, then recheck the affected parts. If verification cannot be completed, clearly state which parts were only statically checked and which have not been tested in practice; do not treat a generated file, attached tests, or a tool's self-reported success as having passed. When the requirements still cannot be met, handle it per the substitution and asking rules above.

After the HTML passes verification, automatically open the final file once in the user's local desktop environment so the user can read it directly; on macOS use `open`, on other platforms use an available equivalent way of opening it. Pass the safely quoted absolute path as the command argument. When the user asks not to open it, follow their choice; when there is no desktop environment, the opening tool is unavailable, or the command fails, deliver the file link and briefly note the limitation, without blocking delivery on it or retrying repeatedly. A successful open command only means the system accepted the open request; it cannot replace the rendering and interaction verification described above.

Deliver the core explanation and the necessary source and output links, and briefly describe the verification actually performed and the limitations that affect use. As the need warrants, provide one optional prediction or judgment question, for example "If this step fails, what will it affect?" (「這個步驟失敗，會影響哪裡？」). Do not require the user to answer it in order to get the output.

When the user points out a confusion, focus on that point and switch to concrete examples, partial diagrams, or a hands-on demonstration. If an existing document needs updating, first read its current content, modify only the relevant passages, diagrams, and their sources, and preserve other content and the user's adjustments; if new evidence changes a shared premise, correct the affected conclusions and diagrams accordingly. Recheck the modified parts and the affected navigation or interactions.

Deliver once the current request is complete; when information gaps remain, keep them stated as they are. Passing the output checks does not mean the user has understood, and the absence of follow-up questions is not evidence of understanding.
