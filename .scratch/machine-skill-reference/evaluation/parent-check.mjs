import assert from 'node:assert/strict';
import { writeFile } from 'node:fs/promises';
import { withOfflinePage } from '/Users/carl/Dev/CMG/AnswerMe/tests/answer-me/browser/cdp.mjs';
const base = '/var/folders/mp/2hbmdcp15qjfn3fhgctttgl40000gn/T/answerme-machine-eval-apm58us9/';
const results = await withOfflinePage(base+'html/cache-latency.html',async ({evaluate,send})=>{
  const rows=[];
  for(const [h,expected] of [[0,120],[50,62],[75,33],[100,4]]){
    const row=await evaluate(`(()=>{const el=document.querySelector('#hit-rate');el.value=${h};el.dispatchEvent(new Event('input',{bubbles:true}));return {latency:document.querySelector('#latency').textContent,caption:document.querySelector('#chart-caption').textContent,explanation:document.querySelector('#result-text').textContent,equation:document.querySelector('#equation').textContent,x:Number(document.querySelector('#marker').getAttribute('cx')),y:Number(document.querySelector('#marker').getAttribute('cy'))}})()`);
    assert.equal(row.latency,expected+' ms');
    assert.ok(row.equation.endsWith('= '+expected+' ms'));
    assert.ok(row.caption.includes(h+'% → '+expected+' ms'));
    assert.equal(row.explanation,`${h}% 的請求走 4 ms 命中路徑；${100-h}% 走 120 ms 未命中路徑。`);
    assert.ok(Math.abs(row.x-(70+590*h/100))<0.001);
    assert.ok(Math.abs(row.y-(270-232*expected/120))<0.001);
    rows.push({h,expected,...row});
    const clip=await evaluate(`(()=>{const r=document.querySelector('.plot-wrap').getBoundingClientRect();return {x:r.x+scrollX,y:r.y+scrollY,width:r.width,height:r.height,scale:1}})()`);
    const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip});
    await writeFile(base+'state-'+h+'.png',Buffer.from(shot.data,'base64'));
  }
  await evaluate("document.querySelector('#reset').click();document.querySelector('#hit-rate').focus()");
  await send('Input.dispatchKeyEvent',{type:'keyDown',key:'ArrowRight',code:'ArrowRight',windowsVirtualKeyCode:39});
  await send('Input.dispatchKeyEvent',{type:'keyUp',key:'ArrowRight',code:'ArrowRight',windowsVirtualKeyCode:39});
  const keyboard=await evaluate("({h:document.querySelector('#hit-rate').value,L:document.querySelector('#latency').textContent})");
  assert.deepEqual(keyboard,{h:'76',L:'31.84 ms'});
  return {rows,keyboard};
});
assert.deepEqual(results.runtimeErrors,[]);assert.deepEqual(results.remoteRequests,[]);
await writeFile(base+'parent-check.json',JSON.stringify(results,null,2)+'\n');
console.log('PASS: numeric results, dynamic text, plot marker positions, keyboard input, offline and runtime checks');
