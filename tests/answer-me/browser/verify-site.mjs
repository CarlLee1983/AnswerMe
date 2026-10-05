import { mkdtemp, mkdir, readdir, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { withOfflinePage } from './cdp.mjs';

const repo = resolve(dirname(fileURLToPath(import.meta.url)), '../../..');
const siteRoot = resolve(process.argv[2] ?? join(repo, 'site'));
const outputRoot = resolve(process.argv[3] ?? await mkdtemp(join(tmpdir(), 'answer-me-site-')));
await mkdir(outputRoot, { recursive: true });
const landingHosts = new Set(['fonts.googleapis.com', 'fonts.gstatic.com']);
const controlSelector = 'input[type=range], input[type=number], select';
// 在頁面內把第一個控制項改成另一個合法值並送出 input/change；沒有可改的值時回傳 reason。
const changeControl = `(() => {
  const el = document.querySelector(${JSON.stringify(controlSelector)});
  if (!el) return { skipped: true };
  const control = el.tagName === 'SELECT' ? 'select' : 'input[type=' + el.type + ']';
  const before = el.value;
  let next;
  if (el.tagName === 'SELECT') {
    next = Array.from(el.options).find(o => !o.disabled && o.value !== before)?.value;
  } else {
    const min = el.min === '' ? undefined : Number(el.min), max = el.max === '' ? undefined : Number(el.max);
    const step = Number(el.step) > 0 ? Number(el.step) : 1;
    const candidates = [max, min, Number(before) + step, Number(before) - step].filter(v => v !== undefined && v !== Number(before));
    next = candidates.find(v => (min === undefined || v >= min) && (max === undefined || v <= max));
  }
  if (next === undefined) return { control, reason: 'no alternative valid value' };
  const textBefore = document.body.textContent;
  el.value = String(next);
  el.dispatchEvent(new Event('input', { bubbles: true }));
  el.dispatchEvent(new Event('change', { bubbles: true }));
  return { control, before, after: el.value, textBefore };
})()`;
// 載入後與互動後各等這段時間，讓延遲發出的請求與例外有機會被記錄。
const settleMs = 2000;
const changeTimeoutMs = 2000;
const pollMs = 100;
const viewports = { desktop: 1200, mobile: 390 };
// 行動模擬下 Chrome 會把 innerWidth 撐到內容寬度，所以溢出要對照模擬的視窗寬度，不能對照 innerWidth。
const layoutProbe = `({width:innerWidth,scrollWidth:document.documentElement.scrollWidth})`;

const pagePaths = (await readdir(siteRoot, { recursive: true }))
  .filter(name => name.endsWith('.html')).map(name => name.split(sep).join('/')).sort();
if (!pagePaths.length) {
  console.error(`No .html pages found under ${siteRoot}`);
  process.exit(1);
}

async function checkPage(path) {
  const slug = path.replace(/\.html$/, '').replaceAll('/', '__');
  const kind = path === 'index.html' ? 'landing' : 'example';
  const failures = [];
  let outcome = { layout: undefined, interaction: undefined, remoteRequests: [], runtimeErrors: [] };
  try {
    outcome = await withOfflinePage(join(siteRoot, path), async ({ evaluate, send, screenshot, sleep }) => {
      await sleep(settleMs);
      const desktop = await evaluate(layoutProbe);
      await screenshot(join(outputRoot, `${slug}-desktop.png`));
      await send('Emulation.setDeviceMetricsOverride', { width: viewports.mobile, height: 844, deviceScaleFactor: 1, mobile: true });
      const mobile = await evaluate(layoutProbe);
      await screenshot(join(outputRoot, `${slug}-mobile.png`));
      await send('Emulation.setDeviceMetricsOverride', { width: viewports.desktop, height: 900, deviceScaleFactor: 1, mobile: false });
      const attempt = await evaluate(changeControl);
      let interaction = { skipped: true };
      if (!attempt.skipped) {
        const { textBefore, ...rest } = attempt;
        let changed = false;
        for (let waited = 0; !rest.reason && !changed && waited <= changeTimeoutMs; waited += pollMs) {
          if (waited) await sleep(pollMs);
          changed = (await evaluate('document.body.textContent')) !== textBefore;
        }
        interaction = { ...rest, changed };
        await sleep(settleMs);
      }
      return { layout: { desktop, mobile }, interaction };
    });
  } catch (error) {
    failures.push(`check error: ${error.message}`);
  }
  for (const [mode, row] of Object.entries(outcome.layout ?? {})) {
    if (row.scrollWidth > viewports[mode]) failures.push(`${mode} overflow: scrollWidth ${row.scrollWidth} > ${viewports[mode]}`);
  }
  for (const url of outcome.remoteRequests) {
    if (kind === 'example' || !landingHosts.has(new URL(url).hostname)) failures.push(`remote request: ${url}`);
  }
  for (const error of outcome.runtimeErrors) failures.push(`runtime error: ${error.exception?.description ?? error.text}`);
  if (outcome.interaction?.changed === false) {
    failures.push(`interaction: ${outcome.interaction.control} ${outcome.interaction.reason ?? 'changed but page text did not change'}`);
  }
  return { path, kind, layout: outcome.layout, interaction: outcome.interaction,
    remoteRequests: outcome.remoteRequests, runtimeErrors: outcome.runtimeErrors, failures };
}

const pages = [];
for (const path of pagePaths) pages.push(await checkPage(path));

await writeFile(join(outputRoot, 'results.json'), JSON.stringify({ siteRoot, pages }, null, 2));
const failed = pages.flatMap(p => p.failures.map(f => `${p.path}: ${f}`));
for (const f of failed) console.error(f);
console.log(`Site browser checks ${failed.length ? 'FAILED' : 'passed'}: ${pages.length} pages, ${failed.length} failures. Artifacts: ${outputRoot}`);
process.exit(failed.length ? 1 : 0);
