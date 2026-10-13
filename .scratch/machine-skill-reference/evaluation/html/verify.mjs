import { withOfflinePage } from '/Users/carl/Dev/CMG/AnswerMe/tests/answer-me/browser/cdp.mjs';
import { writeFile } from 'node:fs/promises';
const base = '/var/folders/mp/2hbmdcp15qjfn3fhgctttgl40000gn/T/answerme-machine-eval-apm58us9/html/';
const result = await withOfflinePage(base + 'cache-latency.html', async ({send,evaluate,screenshot}) => {
  const states=[];
  const get=()=>evaluate(`({value:document.querySelector('#hit-rate').value,rate:document.querySelector('#rate-value').textContent,latency:document.querySelector('#latency').textContent,equation:document.querySelector('#equation').textContent,caption:document.querySelector('#chart-caption').textContent,markerX:Number(document.querySelector('#marker').getAttribute('cx')),markerY:Number(document.querySelector('#marker').getAttribute('cy')),guideX:Number(document.querySelector('#guide-x').getAttribute('x1')),guideY:Number(document.querySelector('#guide-y').getAttribute('y1'))})`);
  const check=(name,s,rate,latency)=>{ if(s.rate!==rate||s.latency!==latency||s.guideX!==s.markerX||s.guideY!==s.markerY) throw Error(`${name}: ${JSON.stringify(s)}`); states.push({name,...s}); };
  check('initial',await get(),'75%','33 ms');
  for(const [value,expected] of [[50,'62 ms'],[0,'120 ms'],[100,'4 ms']]) {
    await evaluate(`(()=>{const s=document.querySelector('#hit-rate');s.value=${value};s.dispatchEvent(new Event('input',{bubbles:true}));})()`);
    check(`${value}%`,await get(),`${value}%`,expected);
  }
  await evaluate(`document.querySelector('#reset').click()`);
  check('reset',await get(),'75%','33 ms');
  await screenshot(base+'desktop.png');
  await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
  const mobile=await evaluate(`({viewport:innerWidth,scroll:document.documentElement.scrollWidth,body:document.body.scrollWidth,rangeWidth:document.querySelector('#hit-rate').getBoundingClientRect().width})`);
  if(mobile.scroll>mobile.viewport||mobile.body>mobile.viewport) throw Error('horizontal overflow: '+JSON.stringify(mobile));
  await screenshot(base+'mobile.png');
  return {states,mobile};
});
if(result.runtimeErrors.length||result.remoteRequests.length) throw Error(JSON.stringify({runtimeErrors:result.runtimeErrors,remoteRequests:result.remoteRequests}));
const record={file:'cache-latency.html',method:'Headless Chrome opened local file with network emulation offline; slider input, reset, and 390 px layout checked.',...result};
await writeFile(base+'verification.json',JSON.stringify(record,null,2)+'\n');
console.log(JSON.stringify({states:result.states.map(({name,rate,latency})=>({name,rate,latency})),mobile:result.mobile,runtimeErrors:result.runtimeErrors,remoteRequests:result.remoteRequests},null,2));
