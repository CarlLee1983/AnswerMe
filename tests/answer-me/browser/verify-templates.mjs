import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { withOfflinePage } from './cdp.mjs';

const repo = resolve(dirname(fileURLToPath(import.meta.url)), '../../..');
const templateRoot = resolve(process.argv[2] ?? join(repo, 'skills/answer-me/assets'));
const outputRoot = resolve(process.argv[3] ?? await mkdtemp(join(tmpdir(), 'answer-me-templates-')));
await mkdir(outputRoot, { recursive: true });
const tokens = ['--bg', '--surface', '--ink', '--muted', '--accent', '--line', '--soft', '--code-bg'];
const results = {};
const fontStylesheet = 'https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;600;700&family=Noto+Serif+TC:wght@600&display=swap';
const visibleSlides = `Array.from(document.querySelectorAll('.slide')).filter(el => getComputedStyle(el).display !== 'none')`;
const activeSlide = `Array.from(document.querySelectorAll('.slide')).findIndex(el => getComputedStyle(el).display !== 'none')`;

async function keyboard(send, key, code = key) {
  const keyCode = { ArrowLeft: 37, ArrowRight: 39, Home: 36, End: 35 }[key];
  await send('Input.dispatchKeyEvent', { type: 'keyDown', key, code, windowsVirtualKeyCode: keyCode });
  await send('Input.dispatchKeyEvent', { type: 'keyUp', key, code, windowsVirtualKeyCode: keyCode });
}

for (const kind of ['article', 'slides']) {
  results[kind] = await withOfflinePage(join(templateRoot, `${kind}.html`), async ({ evaluate, send, screenshot }) => {
    const palette = await evaluate(`Object.fromEntries(${JSON.stringify(tokens)}.map(k => [k,getComputedStyle(document.documentElement).getPropertyValue(k).trim()]))`);
    for (const token of tokens) assert.match(palette[token], /^#[0-9a-f]{6}$/i, `${kind}: ${token}`);
    assert.deepEqual(await evaluate(`Array.from(document.querySelectorAll('link[rel="stylesheet"]'), el => el.href)`), [fontStylesheet], `${kind}: Google Fonts stylesheet`);
    const fonts = await evaluate(`({body:getComputedStyle(document.body).fontFamily,heading:getComputedStyle(document.querySelector('h1')).fontFamily})`);
    assert.match(fonts.body, /^"?Noto Sans TC"?,.*system-ui/, `${kind}: body font and offline fallback`);
    assert.match(fonts.heading, /^"?Noto Serif TC"?,.*Georgia/, `${kind}: heading font and offline fallback`);
    const layout = await evaluate(`({width:innerWidth,scrollWidth:document.documentElement.scrollWidth})`);
    assert.ok(layout.scrollWidth <= layout.width, `${kind}: desktop overflow`);
    await screenshot(join(outputRoot, `${kind}-desktop.png`));
    let navigation;
    if (kind === 'slides') {
      const count = await evaluate(`document.querySelectorAll('.slide').length`);
      assert.ok(count >= 2, 'deck must have multiple pages');
      assert.equal(await evaluate(`${visibleSlides}.length`), 1);
      assert.equal(await evaluate(activeSlide), 0);
      assert.equal(await evaluate(`document.querySelector('#previous').disabled`), true);
      await evaluate(`document.querySelector('#next').click()`);
      assert.equal(await evaluate(activeSlide), 1, 'next button');
      await evaluate(`document.querySelector('#previous').click()`);
      assert.equal(await evaluate(activeSlide), 0, 'previous button');
      await evaluate(`document.activeElement?.blur()`);
      await keyboard(send, 'End');
      assert.equal(await evaluate(activeSlide), count - 1, 'End');
      assert.equal(await evaluate(`document.querySelector('#next').disabled`), true);
      const lastPageLabel = await evaluate(`document.querySelector('#page-count').textContent`);
      assert.ok(lastPageLabel.includes(String(count)), 'last page count');
      await keyboard(send, 'ArrowRight');
      assert.equal(await evaluate(activeSlide), count - 1, 'last page boundary');
      await keyboard(send, 'Home');
      assert.equal(await evaluate(activeSlide), 0, 'Home');
      await keyboard(send, 'ArrowLeft');
      assert.equal(await evaluate(activeSlide), 0, 'first page boundary');
      await keyboard(send, 'ArrowRight');
      assert.equal(await evaluate(activeSlide), 1, 'ArrowRight');
      await keyboard(send, 'ArrowLeft');
      assert.equal(await evaluate(activeSlide), 0, 'ArrowLeft');
      // Future explanations can add links, controls and model inputs. Navigation must leave their keys alone.
      for (const html of ['<input value="sample">', '<textarea>sample</textarea>', '<div contenteditable="true">sample</div>', '<button>sample</button>', '<a href="#sample">sample</a>']) {
        await evaluate(`(() => { const wrapper=document.createElement('div'); wrapper.id='key-test'; wrapper.innerHTML=${JSON.stringify(html)}; document.querySelector('.slide').append(wrapper); wrapper.firstElementChild.focus(); })()`);
        await keyboard(send, 'ArrowRight');
        assert.equal(await evaluate(activeSlide), 0, `interactive target ${html}`);
        await evaluate(`document.querySelector('#key-test').remove()`);
      }
      navigation = { count, buttons: true, arrows: true, homeEnd: true, bounds: true, interactiveTargets: true, lastPageLabel };
    }
    await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 1, mobile: true });
    const mobile = [];
    const pages = navigation?.count ?? 1;
    for (let i = 0; i < pages; i++) {
      const row = await evaluate(`({width:innerWidth,scrollWidth:document.documentElement.scrollWidth})`);
      assert.ok(row.scrollWidth <= row.width, `${kind} mobile page ${i + 1}: ${JSON.stringify(row)}`);
      mobile.push(row);
      await screenshot(join(outputRoot, `${kind}-mobile-${i + 1}.png`));
      if (kind === 'slides') await evaluate(`document.querySelector('#next').click()`);
    }
    await send('Emulation.setDeviceMetricsOverride', { width: 1200, height: 900, deviceScaleFactor: 1, mobile: false });
    await send('Emulation.setEmulatedMedia', { media: 'print' });
    if (kind === 'slides') {
      assert.equal(await evaluate(`${visibleSlides}.length`), navigation.count, 'print includes all slides');
      assert.equal(await evaluate(`getComputedStyle(document.querySelector('#slide-controls')).display`), 'none', 'print hides navigation');
    }
    await screenshot(join(outputRoot, `${kind}-print.png`));
    const printPalette = await evaluate(`Object.fromEntries(${JSON.stringify(tokens)}.map(k => [k,getComputedStyle(document.documentElement).getPropertyValue(k).trim()]))`);
    assert.deepEqual(printPalette, palette, `${kind}: print preserves chosen palette`);
    const pdf = await send('Page.printToPDF', { printBackground: true });
    const pdfBytes = Buffer.from(pdf.data, 'base64');
    await writeFile(join(outputRoot, `${kind}-print.pdf`), pdfBytes);
    const printedPages = (pdfBytes.toString('latin1').match(/\/Type \/Page\b/g) ?? []).length;
    assert.ok(printedPages > 0, `${kind}: Chrome produced print pages`);
    if (kind === 'slides') assert.equal(printedPages, navigation.count, 'one printed page per starter slide');
    const customPalette = { '--bg': '#16191d', '--surface': '#20262c', '--ink': '#f3f0e8', '--muted': '#c2c9d0', '--accent': '#ffb36b', '--line': '#49525b', '--soft': '#2b333b', '--code-bg': '#252d35' };
    await evaluate(`(() => { const style=document.createElement('style'); style.textContent=':root {' + Object.entries(${JSON.stringify(customPalette)}).map(([k,v])=>k+':'+v+';').join('') + '}'; document.head.append(style); })()`);
    const customPrint = await evaluate(`Object.fromEntries(${JSON.stringify(tokens)}.map(k => [k,getComputedStyle(document.documentElement).getPropertyValue(k).trim()]))`);
    assert.deepEqual(customPrint, customPalette, `${kind}: print respects dark/orange customization`);
    await screenshot(join(outputRoot, `${kind}-custom-print.png`));
    return { fileProtocol: true, offline: true, fonts, palette, desktop: layout, mobile, navigation, print: { palette: printPalette, printedPages, customPalette: customPrint } };
  });
  assert.deepEqual(results[kind].runtimeErrors, [], `${kind} runtime errors`);
  assert.deepEqual(results[kind].remoteRequests, [fontStylesheet], `${kind}: only optional Google Fonts request while offline`);
}
assert.deepEqual(results.article.palette, results.slides.palette, 'templates share default palette');

results.noScript = await withOfflinePage(join(templateRoot, 'slides.html'), async ({ evaluate, send, screenshot }) => {
  await send('Emulation.setScriptExecutionDisabled', { value: true });
  await send('Page.reload');
  // Runtime.evaluate is a debugger operation and remains available while page scripts are disabled.
  for (let i = 0; i < 100; i++) {
    if (await evaluate(`document.readyState === 'complete' && !document.documentElement.classList.contains('enhanced')`)) break;
    await new Promise(resolve => setTimeout(resolve, 50));
  }
  const count = await evaluate(`document.querySelectorAll('.slide').length`);
  assert.ok(count >= 2);
  assert.equal(await evaluate(`${visibleSlides}.length`), count, 'no-JS includes all slides');
  assert.equal(await evaluate(`getComputedStyle(document.querySelector('#slide-controls')).display`), 'none', 'no-JS hides inoperative controls');
  await screenshot(join(outputRoot, 'slides-no-script.png'));
  return { count, allVisible: true };
});
assert.ok(results.noScript.remoteRequests.length > 0);
assert.ok(results.noScript.remoteRequests.every(url => url === fontStylesheet), 'no-JS: only optional Google Fonts request');
assert.deepEqual(results.noScript.runtimeErrors, []);
await writeFile(join(outputRoot, 'verification.json'), JSON.stringify(results, null, 2));
console.log(`Template browser checks passed. Artifacts: ${outputRoot}`);
