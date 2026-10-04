import { spawn, spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { mkdtemp, readFile, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const sleep = ms => new Promise(r => setTimeout(r, ms));
function chromeExecutable() {
  if (process.env.CHROME_BIN) return process.env.CHROME_BIN;
  const paths = [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser',
  ];
  const installed = paths.find(existsSync);
  if (installed) return installed;
  for (const name of ['google-chrome', 'chromium', 'chromium-browser']) {
    const found = spawnSync('which', [name], { encoding: 'utf8' });
    if (found.status === 0) return found.stdout.trim();
  }
  throw new Error('Chrome/Chromium not found; set CHROME_BIN to its executable');
}
export async function withOfflinePage(filename, action) {
  const executable = chromeExecutable();
  const profile = await mkdtemp(join(tmpdir(), 'answer-me-chrome-'));
  const child = spawn(executable,
    ['--headless=new', '--no-first-run', '--no-default-browser-check',
     '--remote-debugging-port=0', '--user-data-dir=' + profile, 'about:blank'],
    { stdio: ['ignore', 'ignore', 'pipe'] });
  let closed = false;
  const childClosed = new Promise(resolve => child.once('close', () => { closed = true; resolve(); }));
  let log = ''; child.stderr.on('data', c => { log += c.toString(); });
  let launchError; child.on('error', error => { launchError = error; });
  let socket;
  try {
    let port;
    for (let i = 0; i < 100; i++) {
      try { port = (await readFile(join(profile, 'DevToolsActivePort'), 'utf8')).split('\n')[0]; break; }
      catch { if (launchError) throw launchError; if (closed) throw new Error(log); await sleep(100); }
    }
    if (!port) throw new Error('Chrome startup timed out: ' + log.slice(-2000));
    const targets = await (await fetch('http://127.0.0.1:' + port + '/json/list')).json();
    const target = targets.find(t => t.type === 'page');
    if (!target) throw new Error('No isolated Chrome page target');
    socket = new WebSocket(target.webSocketDebuggerUrl);
    await new Promise((ok, fail) => { socket.addEventListener('open', ok, { once: true }); socket.addEventListener('error', fail, { once: true }); });
    let id = 0;
    const pending = new Map();
    const events = [];
    socket.addEventListener('message', event => {
      const msg = JSON.parse(event.data);
      if (msg.id) {
        const p = pending.get(msg.id); if (!p) return;
        pending.delete(msg.id); clearTimeout(p.timer);
        if (msg.error) p.reject(new Error(JSON.stringify(msg.error))); else p.resolve(msg.result);
      } else events.push(msg);
    });
    const send = (method, params = {}) => new Promise((resolve, reject) => {
      const n = ++id;
      const timer = setTimeout(() => { pending.delete(n); reject(new Error('CDP timeout: ' + method)); }, 10000);
      pending.set(n, { resolve, reject, timer });
      socket.send(JSON.stringify({ id: n, method, params }));
    });
    const evaluate = async expression => {
      const result = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
      if (result.exceptionDetails) throw new Error(JSON.stringify(result.exceptionDetails));
      return result.result.value;
    };
    await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable');
    await send('Network.setCacheDisabled', { cacheDisabled: true });
    await send('Network.setBypassServiceWorker', { bypass: true });
    await send('Network.emulateNetworkConditions', { offline: true, latency: 0, downloadThroughput: 0, uploadThroughput: 0 });
    await send('Emulation.setDeviceMetricsOverride', { width: 1200, height: 900, deviceScaleFactor: 1, mobile: false });
    const nav = await send('Page.navigate', { url: pathToFileURL(resolve(filename)).href });
    if (nav.errorText) throw new Error(nav.errorText);
    for (let i = 0; i < 100; i++) {
      if (await evaluate('document.readyState === "complete" && location.protocol === "file:"')) break;
      await sleep(50);
      if (i === 99) throw new Error('file page did not load');
    }
    const screenshot = async destination => {
      const result = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
      await writeFile(destination, Buffer.from(result.data, 'base64'));
    };
    const answer = await action({ send, evaluate, screenshot, events, sleep });
    return { ...answer, runtimeErrors: events.filter(e => e.method === 'Runtime.exceptionThrown').map(e => e.params.exceptionDetails),
      remoteRequests: events.filter(e => e.method === 'Network.requestWillBeSent' && /^https?:/.test(e.params.request.url)).map(e => e.params.request.url) };
  } finally {
    if (socket?.readyState === WebSocket.OPEN) socket.close();
    if (!closed) {
      child.kill('SIGTERM');
      await Promise.race([childClosed, sleep(2000)]);
      if (!closed) { child.kill('SIGKILL'); await childClosed; }
    }
    await rm(profile, { recursive: true, force: true });
  }
}
