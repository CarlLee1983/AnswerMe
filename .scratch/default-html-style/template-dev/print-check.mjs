import { withOfflinePage } from '../../../tests/answer-me/browser/cdp.mjs';
import { writeFile } from 'node:fs/promises';
const path = 'skills/answer-me/assets/article.html';
const result = await withOfflinePage(path, async ({ send, evaluate }) => {
  await send('Emulation.setEmulatedMedia', { media: 'print' });
  const widths = await evaluate(`(() => {
    document.querySelector('pre code').textContent = 'very-long-code-'.repeat(80);
    document.querySelector('table td').textContent = 'very-long-table-cell-'.repeat(80);
    const pre = document.querySelector('pre');
    const table = document.querySelector('table');
    return {
      pre: [pre.scrollWidth, pre.clientWidth],
      table: [table.scrollWidth, table.clientWidth],
      viewport: document.documentElement.scrollWidth,
      printInk: getComputedStyle(document.documentElement).getPropertyValue('--ink').trim()
    };
  })()`);
  const pdf = await send('Page.printToPDF', { printBackground: true, paperWidth: 8.27, paperHeight: 11.69 });
  await writeFile('.scratch/default-html-style/template-dev/article-long-print.pdf', Buffer.from(pdf.data, 'base64'));
  return widths;
});
console.log(JSON.stringify(result));
