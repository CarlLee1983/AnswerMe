import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { withOfflinePage } from './cdp.mjs';
const sampleRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const inputRoot = resolve(process.argv[2] ?? sampleRoot);
const outputRoot = resolve(process.argv[3] ?? await mkdtemp(join(tmpdir(), 'answer-me-browser-')));
await mkdir(outputRoot, { recursive: true });
const results = {};
results.explainer = await withOfflinePage(join(inputRoot, 'interactive/output/explainer.html'), async ({evaluate, send, screenshot}) => {
  const rows = [];
  const cases = [
    [75,4,120,33], [0,4,120,120], [100,4,120,4], [50,4,120,62],
    [90,4,120,15.6], [75,10,120,37.5], [75,4,60,18], [75,0,0,0],
    [25,80,20,35], [75,80,20,65]
  ];
  for (const [h,c,d,expected] of cases) {
    const actual = await evaluate(`(() => {
      const values = ${JSON.stringify([['hit-rate',h],['hit-latency',c],['miss-latency',d]])};
      for (const [id,value] of values) {
        const el=document.getElementById(id); el.value=String(value); el.dispatchEvent(new Event('input',{bubbles:true}));
      }
      return {total:document.getElementById('latency').textContent,
        hit:document.getElementById('hit-part').textContent, miss:document.getElementById('miss-part').textContent,
        body:document.body.innerText};
    })()`);
    assert.ok(Math.abs(Number(actual.total)-expected)<0.011, JSON.stringify({h,c,d,expected,actual}));
    assert.ok(!/NaN|Infinity/.test(actual.body), 'invalid numeric output');
    rows.push({h,c,d,expected,actual:Number(actual.total)});
  }
  const presets = [33,15.6,18,31.5];
  for (let i=0;i<presets.length;i++) {
    const n=await evaluate(`document.querySelectorAll('button[data-h]')[${i}].click(); Number(document.querySelector('#latency').textContent)`);
    assert.ok(Math.abs(n-presets[i])<0.011, 'preset '+i);
  }
  await evaluate(`document.querySelector('button[data-h]').click(); document.querySelector('#hit-rate').focus()`);
  await send('Input.dispatchKeyEvent',{type:'keyDown',key:'ArrowRight',code:'ArrowRight',windowsVirtualKeyCode:39});
  await send('Input.dispatchKeyEvent',{type:'keyUp',key:'ArrowRight',code:'ArrowRight',windowsVirtualKeyCode:39});
  const keyboard = await evaluate(`({rate:document.querySelector('#hit-rate').value,total:document.querySelector('#latency').textContent})`);
  assert.equal(keyboard.rate,'76'); assert.equal(Number(keyboard.total),31.84);
  await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
  const layout = await evaluate(`({width:innerWidth,scrollWidth:document.documentElement.scrollWidth})`);
  assert.ok(layout.scrollWidth<=layout.width,JSON.stringify(layout));
  await screenshot(join(outputRoot, 'explainer-mobile.png'));
  return {fileProtocol:true,offline:true,rows,presets,keyboard,mobileLayout:layout};
});
results.repaired = await withOfflinePage(join(inputRoot, 'interactive/output/repaired.html'),async ({evaluate}) => {
  const rows=[];
  assert.equal(await evaluate(`document.querySelector('#answer').textContent`),'33 ms');
  for (const [h,expected] of [[0,120],[100,4],[50,62],[75,33]]) {
    const actual = await evaluate(`(() => { const e=document.querySelector('#hit'); e.value='${h}'; e.dispatchEvent(new Event('input',{bubbles:true})); return document.querySelector('#answer').textContent; })()`);
    assert.equal(Number.parseFloat(actual),expected); rows.push({h,expected,actual});
  }
  return {fileProtocol:true,offline:true,rows};
});
for (const [name,result] of Object.entries(results)) {
  assert.deepEqual(result.remoteRequests,[],name+' remote dependency');
  assert.deepEqual(result.runtimeErrors,[],name+' runtime error');
}
results.broken = await withOfflinePage(join(inputRoot, 'interactive/input/existing-explainer.html'), async ({ evaluate }) => {
  const initial = await evaluate(`document.querySelector('#answer').textContent`);
  const changed = await evaluate(`(() => { const e=document.querySelector('#hit'); e.value='50'; e.dispatchEvent(new Event('input',{bubbles:true})); return document.querySelector('#answer').textContent; })()`);
  return { initial, changed };
});
assert.equal(results.broken.initial, '31 ms');
assert.equal(results.broken.changed, results.broken.initial, 'broken sample must remain stuck');
assert.ok(results.broken.remoteRequests.includes('https://cdn.example.invalid/answer-me-latency.js'), 'broken sample must reveal remote dependency');
await writeFile(join(outputRoot, 'verification.json'),JSON.stringify(results,null,2));
console.log(`Browser artifacts: ${outputRoot}`);
