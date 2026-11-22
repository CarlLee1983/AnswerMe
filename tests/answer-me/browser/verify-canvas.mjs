import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { existsSync } from 'node:fs';
import { mkdtemp, readFile, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { withOfflinePage } from './cdp.mjs';

const assets = new URL('../../../skills/answer-me/assets/', import.meta.url);
const snippetURL = new URL('explanation-canvas.html', assets);
assert.ok(existsSync(snippetURL), 'Provide a reusable inline Explanation Canvas snippet');

const snippet = await readFile(snippetURL, 'utf8');
const output = await mkdtemp(join(tmpdir(), 'answer-me-canvas-'));
const mobile = { width: 390, height: 844, deviceScaleFactor: 1, mobile: true };
const disclosure = index => `document.querySelectorAll('details[data-answerme-canvas]')[${index}]`;
const summary = index => `${disclosure(index)}.querySelector(':scope > summary')`;
const stepButton = (index, label) => `[...${disclosure(index)}.querySelectorAll('button')].find(button => button.textContent.trim() === '${label}')`;
const activeSlide = `[...document.querySelectorAll('.slide')].findIndex(slide => !slide.hidden)`;
const expectedSteps = [
  { title: '三台各收到一筆', explanation: /三筆都還在處理/, readouts: ['處理中', '處理中', '處理中'] },
  { title: '只剩 A 還在處理', explanation: /從三筆變成一筆.*累計收到的請求仍是一筆/, readouts: ['處理中', '已完成', '已完成'] },
];
const expectedSource = /自造教學示例.*兩次觀察之間沒有新請求/;
const readSteps = `details => [...details.querySelectorAll('ol[data-canvas-frames] > li')]
  .filter(step => step.checkVisibility())
  .map(step => ({
    title: step.querySelector(':scope > strong').textContent.trim(),
    explanation: step.querySelector(':scope > p').innerText.trim(),
    readouts: [...step.querySelectorAll(':scope > dl > dt')].map(term => [
      term.textContent.trim(), term.nextElementSibling.textContent.trim()
    ])
  }))`;

function checkStep(actual, expected) {
  assert.equal(actual.title, expected.title);
  assert.match(actual.explanation, expected.explanation);
  assert.deepEqual(actual.readouts, expected.readouts.map((value, index) => [
    `伺服器 ${'ABC'[index]}`, value
  ]));
}

async function generatePage(kind, sections, { name = kind, block = snippet } = {}) {
  const template = await readFile(new URL(`${kind}.html`, assets), 'utf8');
  let sectionIndex = 0;
  let inserted = 0;
  const html = template.replaceAll('</section>', closingTag => {
    if (!sections.includes(sectionIndex++)) return closingTag;
    inserted++;
    return block + '\n' + closingTag;
  });
  assert.equal(inserted, sections.length, `${kind}: insert a Canvas into each intended section`);
  const path = join(output, `${name}.html`);
  await writeFile(path, html);
  return { path, html, url: pathToFileURL(path).href };
}

async function key(send, name, code = name) {
  const windowsVirtualKeyCode = { Enter: 13, ' ': 32, ArrowRight: 39 }[name];
  const text = { Enter: '\r', ' ': ' ' }[name];
  await send('Input.dispatchKeyEvent', { type: 'keyDown', key: name, code, windowsVirtualKeyCode, text });
  await send('Input.dispatchKeyEvent', { type: 'keyUp', key: name, code, windowsVirtualKeyCode });
}

async function settle(evaluate) {
  await evaluate('new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(() => resolve())))');
}

async function click(evaluate, element) {
  await evaluate(`${element}.click()`);
  await settle(evaluate);
}

async function initialDisclosures(evaluate, count) {
  assert.deepEqual(await evaluate(`[...document.querySelectorAll('details[data-answerme-canvas]')].map(details => ({
    open: details.open,
    label: details.querySelector(':scope > summary').textContent.trim()
  }))`), Array.from({ length: count }, () => ({ open: false, label: '看不懂這一步' })));
}

async function renderedStep(evaluate, index, expected, steps = expectedSteps) {
  const state = await evaluate(`(() => {
    const details = ${disclosure(index)};
    const canvas = details.querySelector('canvas');
    const source = details.querySelector('[data-canvas-sources]');
    const rect = canvas.getBoundingClientRect();
    const { width, height } = canvas;
    const context = canvas.getContext('2d');
    if (!width || !height || !context) throw new Error('No readable 2D canvas');
    const { data } = context.getImageData(0, 0, width, height);
    let pixelHash = 2166136261;
    const colors = new Set();
    for (let i = 0; i < data.length; i += 4) {
      const color = (data[i] << 24) | (data[i + 1] << 16) | (data[i + 2] << 8) | data[i + 3];
      pixelHash = Math.imul(pixelHash ^ color, 16777619);
      if (data[i + 3]) colors.add(color);
    }
    return {
      caption: details.querySelector('[data-canvas-caption]').innerText,
      source: source?.checkVisibility() ? source.innerText.trim() : '',
      steps: (${readSteps})(details),
      previousDisabled: ${stepButton(index, '上一步')}.disabled,
      nextDisabled: ${stepButton(index, '下一步')}.disabled,
      width: rect.width,
      height: rect.height,
      colors: colors.size,
      pixelHash
    };
  })()`);
  assert.ok(state.caption.includes(steps[expected].title), `Canvas ${index + 1}: step ${expected + 1} title is readable`);
  assert.match(state.source, expectedSource, 'Source and timing assumption stay visible during interaction');
  assert.equal(state.steps.length, 1, 'Only the current state is visible');
  checkStep(state.steps[0], steps[expected]);
  assert.ok(state.width > 0 && state.height > 0, 'Canvas diagram is visible');
  assert.ok(state.colors > 10, 'Canvas contains drawn pixels with multiple colors');
  assert.equal(state.previousDisabled, expected === 0, 'Previous respects the first step');
  assert.equal(state.nextDisabled, expected === steps.length - 1, 'Next respects the final step');
  return state;
}

async function checkMobile(page, index, expected, screenshotName) {
  const { send, evaluate, screenshot } = page;
  await send('Emulation.setDeviceMetricsOverride', mobile);
  await settle(evaluate);
  const scrollWidth = await evaluate('document.documentElement.scrollWidth');
  assert.ok(scrollWidth <= mobile.width, `390px layout overflows to ${scrollWidth}px`);
  const state = await renderedStep(evaluate, index, expected);
  assert.ok(state.width <= mobile.width, 'Canvas fits a narrow screen');
  await evaluate(`${summary(index)}.scrollIntoView()`);
  await screenshot(join(output, screenshotName));
  return { scrollWidth, diagramWidth: state.width };
}

async function noNavigation(page, expectedURL, eventStart) {
  assert.equal(await page.evaluate('location.href'), expectedURL, 'Canvas stays in the same file');
  const navigations = page.events.slice(eventStart).filter(event => event.method === 'Page.frameNavigated');
  assert.deepEqual(navigations, [], 'Canvas does not navigate');
}

async function run(page, action) {
  const result = await withOfflinePage(page.path, action);
  assert.deepEqual(result.runtimeErrors, [], 'No runtime exceptions');
  assert.deepEqual(result.remoteRequests, [], 'No HTTP(S) requests while offline');
  assert.equal(await readFile(page.path, 'utf8'), page.html, 'Both interactive and fallback modes use the same generated file bytes');
  return { ...result, sha256: createHash('sha256').update(page.html).digest('hex') };
}

const article = await generatePage('article', [0, 1]);
const slides = await generatePage('slides', [1]);

const results = {};
results.article = await run(article, async page => {
  const { evaluate, screenshot, events } = page;
  const eventStart = events.length;
  await initialDisclosures(evaluate, 2);
  await click(evaluate, summary(0));
  const first = await renderedStep(evaluate, 0, 0);
  assert.equal(await evaluate(`${disclosure(1)}.open`), false, 'Opening one disclosure leaves the other closed');

  await click(evaluate, stepButton(0, '下一步'));
  const next = await renderedStep(evaluate, 0, 1);
  assert.notEqual(next.pixelHash, first.pixelHash, 'Next step draws a different diagram');

  await click(evaluate, summary(1));
  await renderedStep(evaluate, 1, 0);
  await renderedStep(evaluate, 0, 1);
  await click(evaluate, stepButton(1, '下一步'));
  await click(evaluate, stepButton(0, '上一步'));
  await renderedStep(evaluate, 0, 0);
  await renderedStep(evaluate, 1, 1);

  await click(evaluate, summary(1));
  assert.equal(await evaluate(`${disclosure(1)}.open`), false, 'Disclosure closes');
  await click(evaluate, summary(1));
  await renderedStep(evaluate, 1, 1);
  await evaluate(`${summary(1)}.scrollIntoView()`);
  await screenshot(join(output, 'article-desktop.png'));
  const mobileLayout = await checkMobile(page, 1, 1, 'article-mobile.png');
  await noNavigation(page, article.url, eventStart);
  return { independentlyStateful: true, diagramChanges: true, mobileLayout };
});

results.slides = await run(slides, async page => {
  const { evaluate, send, events } = page;
  const eventStart = events.length;
  await initialDisclosures(evaluate, 1);
  assert.equal(await evaluate(activeSlide), 0, 'Canvas starts on a hidden slide');
  await key(send, 'ArrowRight');
  assert.equal(await evaluate(activeSlide), 1, 'ArrowRight navigates the deck outside Canvas');
  await evaluate(`${summary(0)}.focus()`);
  assert.equal(await evaluate(`document.activeElement === ${summary(0)}`), true, 'The newly visible summary can receive focus');
  await key(send, 'ArrowRight');
  assert.equal(await evaluate(activeSlide), 1, 'Focused disclosure summary does not navigate the deck');
  await key(send, 'Enter');
  await settle(evaluate);
  assert.equal(await evaluate(`${disclosure(0)}.open`), true, 'Enter opens the disclosure');
  await renderedStep(evaluate, 0, 0);

  await evaluate(`${stepButton(0, '下一步')}.focus()`);
  await key(send, 'ArrowRight');
  assert.equal(await evaluate(activeSlide), 1, 'Focused step control does not navigate the deck');
  await key(send, ' ', 'Space');
  await settle(evaluate);
  await renderedStep(evaluate, 0, 1);
  const mobileLayout = await checkMobile(page, 0, 1, 'slides-mobile.png');
  await noNavigation(page, slides.url, eventStart);
  return { keyboard: true, mobileLayout };
});

const longStatus = 'RESPONSE_COMPLETE_WITH_RETRY_AND_CONNECTION_POOL_RECOVERY_CONFIRMED';
const authoredSnippet = snippet.replace('<dt>伺服器 B</dt><dd>已完成</dd>', `<dt>伺服器 B</dt><dd>${longStatus}</dd>`);
assert.notEqual(authoredSnippet, snippet, 'Add a long technical status to the second authored step');
const narrow = await generatePage('article', [0], { name: 'article-long-state', block: authoredSnippet });
results.narrow = await run(narrow, async page => {
  const { evaluate, send, events, screenshot } = page;
  const eventStart = events.length;
  await send('Emulation.setDeviceMetricsOverride', mobile);
  await click(evaluate, summary(0));
  const short = await renderedStep(evaluate, 0, 0);
  const next = stepButton(0, '下一步');
  const previous = stepButton(0, '上一步');
  await evaluate(`${next}.focus()`);
  await key(send, ' ', 'Space');
  await settle(evaluate);
  assert.equal(await evaluate(`${previous}.checkVisibility() && !${previous}.disabled`), true,
    'A long technical status leaves an operable Previous control at 390px');
  assert.equal(await evaluate(`document.activeElement === ${previous}`), true, 'Focus moves to the available Previous control');

  const longStep = { ...expectedSteps[1], readouts: ['處理中', longStatus, '已完成'] };
  const wrapped = await renderedStep(evaluate, 0, 1, [expectedSteps[0], longStep]);
  assert.ok(wrapped.height > short.height, 'The diagram gives wrapped labels extra height');
  const scrollWidth = await evaluate('document.documentElement.scrollWidth');
  assert.ok(scrollWidth <= mobile.width, `390px layout overflows to ${scrollWidth}px with a long status`);
  await screenshot(join(output, 'article-long-state-mobile.png'));

  await key(send, 'Enter');
  await settle(evaluate);
  await renderedStep(evaluate, 0, 0);
  assert.equal(await evaluate(`document.activeElement === ${next}`), true, 'Keyboard Back restores focus to Next');
  await noNavigation(page, narrow.url, eventStart);
  return { scrollWidth, shortDiagramHeight: short.height, wrappedDiagramHeight: wrapped.height, keyboardBack: true };
});

for (const mode of ['no-canvas', 'no-script']) {
  results[mode] = await run(slides, async ({ evaluate, send, events, screenshot, sleep }) => {
    if (mode === 'no-canvas') {
      await send('Page.addScriptToEvaluateOnNewDocument', { source: 'HTMLCanvasElement.prototype.getContext = () => null;' });
    } else {
      await send('Emulation.setScriptExecutionDisabled', { value: true });
    }
    const eventStart = events.length;
    await send('Page.reload');
    for (let attempt = 0; attempt < 100 && !events.slice(eventStart).some(event => event.method === 'Page.loadEventFired'); attempt++) {
      await sleep(25);
    }
    assert.ok(events.slice(eventStart).some(event => event.method === 'Page.loadEventFired'), `${mode}: same file reloaded`);
    await initialDisclosures(evaluate, 1);
    if (mode === 'no-canvas') await key(send, 'ArrowRight');
    await evaluate(`${summary(0)}.focus()`);
    await key(send, 'Enter');
    const fallback = await evaluate(`(() => {
      const details = ${disclosure(0)};
      const visible = element => element.checkVisibility({ visibilityProperty: true });
      const source = details.querySelector('[data-canvas-sources]');
      return {
        open: details.open,
        steps: (${readSteps})(details),
        source: source && visible(source) ? source.innerText.trim() : '',
        controls: [...details.querySelectorAll('canvas, button')].filter(visible).length,
      };
    })()`);
    assert.equal(fallback.open, true, `${mode}: native disclosure still opens`);
    assert.equal(fallback.steps.length, expectedSteps.length, `${mode}: all authored steps remain visible`);
    fallback.steps.forEach((step, index) => checkStep(step, expectedSteps[index]));
    assert.match(fallback.source, expectedSource, `${mode}: source and timing assumption remain readable`);
    assert.equal(fallback.controls, 0, `${mode}: no inoperative diagram or controls`);
    assert.equal(await evaluate('location.href'), slides.url);
    await screenshot(join(output, `slides-${mode}.png`));
    return fallback;
  });
}

await writeFile(join(output, 'verification.json'), JSON.stringify(results, null, 2));
console.log(`Canvas browser checks passed. Artifacts: ${output}`);
