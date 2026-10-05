import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { mkdtemp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const script = resolve(dirname(fileURLToPath(import.meta.url)), 'verify-site.mjs');
const viewports = { desktop: 1200, mobile: 390 };
const fontsLink = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC&display=swap">';
const page = (head, body) => `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">${head}</head><body>${body}</body></html>`;
const landing = page(fontsLink, '<h1>AnswerMe</h1><p>intro</p>');

// 以 { 相對路徑: 內容 } 建立暫時網站目錄，執行檢查腳本並讀回 results.json。
async function check(t, files) {
  const root = await mkdtemp(join(tmpdir(), 'answer-me-site-fixture-'));
  const artifacts = await mkdtemp(join(tmpdir(), 'answer-me-site-artifacts-'));
  t.after(() => Promise.all([root, artifacts].map(dir => rm(dir, { recursive: true, force: true }))));
  for (const [name, content] of Object.entries(files)) {
    await mkdir(dirname(join(root, name)), { recursive: true });
    await writeFile(join(root, name), content);
  }
  const run = spawnSync(process.execPath, [script, root, artifacts], { encoding: 'utf8', timeout: 120000 });
  const resultsFile = join(artifacts, 'results.json');
  const results = existsSync(resultsFile) ? JSON.parse(await readFile(resultsFile, 'utf8')) : undefined;
  return { ...run, artifacts, results };
}
const failuresOf = results => results.pages.flatMap(p => p.failures).join('\n');

test('valid landing and static example pass with screenshots', async t => {
  const run = await check(t, { 'index.html': landing, 'examples/static.html': page('', '<h1>static</h1>') });
  assert.equal(run.status, 0, run.stdout + run.stderr);
  assert.deepEqual(run.results.pages.map(p => [p.path, p.kind]).sort(), [['examples/static.html', 'example'], ['index.html', 'landing']]);
  for (const p of run.results.pages) {
    assert.deepEqual(p.failures, []);
    assert.ok(p.layout.desktop.scrollWidth <= viewports.desktop);
    assert.ok(p.layout.mobile.scrollWidth <= viewports.mobile);
  }
  for (const name of ['index-desktop.png', 'index-mobile.png', 'examples__static-desktop.png', 'examples__static-mobile.png']) {
    assert.ok(existsSync(join(run.artifacts, name)), name);
  }
});

test('example page requesting an http(s) URL fails and names it', async t => {
  const run = await check(t, { 'index.html': landing, 'examples/cdn.html': page('<script src="https://cdn.example.com/x.js"></script>', '<h1>cdn</h1>') });
  assert.equal(run.status, 1);
  assert.match(failuresOf(run.results), /https:\/\/cdn\.example\.com\/x\.js/);
});

test('page that throws at runtime fails', async t => {
  const run = await check(t, { 'index.html': landing, 'examples/boom.html': page('', "<h1>boom</h1><script>throw new Error('boom')</script>") });
  assert.equal(run.status, 1);
  assert.match(failuresOf(run.results), /runtime error.*boom/);
});

test('example wider than 390 px fails with a mobile overflow failure', async t => {
  const run = await check(t, { 'index.html': landing, 'examples/wide.html': page('', '<div style="width:600px;height:20px;background:#ccc">wide</div>') });
  assert.equal(run.status, 1);
  assert.match(failuresOf(run.results), /mobile overflow/);
});

test('landing page may only load Google Fonts hosts', async t => {
  const bad = page(fontsLink + '<script src="https://cdn.example.com/lib.js"></script>', '<h1>AnswerMe</h1>');
  const run = await check(t, { 'index.html': bad });
  assert.equal(run.status, 1);
  assert.match(failuresOf(run.results), /https:\/\/cdn\.example\.com\/lib\.js/);
  assert.doesNotMatch(failuresOf(run.results), /fonts\.googleapis\.com/);
});

const slider = script => page('', `<h1>slider</h1><input type="range" min="0" max="100" value="50" id="c"><p id="out">50</p><script>document.getElementById('c').addEventListener('input', e => { ${script} })</script>`);

test('interactive example whose control updates the page passes', async t => {
  const run = await check(t, { 'index.html': landing, 'examples/live.html': slider("document.getElementById('out').textContent = e.target.value;") });
  assert.equal(run.status, 0, run.stdout + run.stderr);
  const live = run.results.pages.find(p => p.path === 'examples/live.html');
  assert.equal(live.interaction.changed, true);
  assert.equal(run.results.pages.find(p => p.path === 'index.html').interaction.skipped, true);
});

test('interactive example whose control changes nothing fails', async t => {
  const run = await check(t, { 'index.html': landing, 'examples/dead.html': slider('') });
  assert.equal(run.status, 1);
  assert.match(failuresOf(run.results), /interaction/);
});

test('site root without any html page fails', async t => {
  const run = await check(t, { 'readme.txt': 'nothing here' });
  assert.equal(run.status, 1);
  assert.match(run.stderr, /no \.html pages/i);
});

test('an error while checking one page is recorded and the other pages still run', async t => {
  // Event 建構失敗會讓腳本對該頁的控制項操作丟出例外，既確定又很快。
  const broken = page('<script>window.Event = function () { throw new Error("no events") }</script>', '<h1>broken</h1><input type="range" min="0" max="10" value="5">');
  const run = await check(t, { 'index.html': landing, 'examples/a-broken.html': broken, 'examples/b-fine.html': page('', '<h1>fine</h1>') });
  assert.equal(run.status, 1);
  assert.deepEqual(run.results.pages.map(p => p.path), ['examples/a-broken.html', 'examples/b-fine.html', 'index.html']);
  const [bad, fine, home] = run.results.pages;
  assert.match(bad.failures.join('\n'), /check error/);
  assert.deepEqual([fine.failures, home.failures], [[], []]);
  assert.ok(existsSync(join(run.artifacts, 'examples__b-fine-desktop.png')));
});

test('example page that fires a request shortly after load fails', async t => {
  const late = page('', "<h1>late</h1><script>setTimeout(() => fetch('https://late.example/x').catch(() => {}), 1000)</script>");
  const run = await check(t, { 'index.html': landing, 'examples/late.html': late });
  assert.equal(run.status, 1);
  assert.match(failuresOf(run.results), /https:\/\/late\.example\/x/);
});

test('interactive example that updates 500 ms after the input passes', async t => {
  const run = await check(t, { 'index.html': landing, 'examples/slow.html': slider("setTimeout(() => { document.getElementById('out').textContent = e.target.value }, 500);") });
  assert.equal(run.status, 0, run.stdout + run.stderr);
});

test('select-driven example passes', async t => {
  const select = page('', `<h1>select</h1><select id="c"><option value="a" selected>A</option><option value="b">B</option></select><p id="out">A</p><script>document.getElementById('c').addEventListener('change', e => { document.getElementById('out').textContent = e.target.value })</script>`);
  const run = await check(t, { 'index.html': landing, 'examples/select.html': select });
  assert.equal(run.status, 0, run.stdout + run.stderr);
  const found = run.results.pages.find(p => p.path === 'examples/select.html');
  assert.deepEqual([found.interaction.control, found.interaction.after, found.interaction.changed], ['select', 'b', true]);
});

test('content wider than the desktop viewport fails with a desktop overflow failure', async t => {
  const run = await check(t, { 'index.html': landing, 'examples/huge.html': page('', '<div style="width:1500px;height:20px;background:#ccc">huge</div>') });
  assert.equal(run.status, 1);
  assert.match(failuresOf(run.results), /desktop overflow/);
});

test('landing page may load fonts from fonts.gstatic.com', async t => {
  const gstatic = page(fontsLink + '<link rel="preload" as="font" href="https://fonts.gstatic.com/s/x.woff2" crossorigin>', '<h1>AnswerMe</h1>');
  const run = await check(t, { 'index.html': gstatic });
  assert.equal(run.status, 0, run.stdout + run.stderr);
  assert.ok(run.results.pages[0].remoteRequests.some(url => url.startsWith('https://fonts.gstatic.com/')));
});

test('screenshots of x/y.html and x-y.html do not collide', async t => {
  const run = await check(t, { 'index.html': landing, 'x/y.html': page('', '<h1>y</h1>'), 'x-y.html': page('', '<h1>xy</h1>') });
  assert.equal(run.status, 0, run.stdout + run.stderr);
  for (const name of ['x__y-desktop.png', 'x__y-mobile.png', 'x-y-desktop.png', 'x-y-mobile.png']) assert.ok(existsSync(join(run.artifacts, name)), name);
});
