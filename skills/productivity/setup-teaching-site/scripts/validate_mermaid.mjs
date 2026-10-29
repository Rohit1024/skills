#!/usr/bin/env node
// Read one batch from Python. Reuse a browser, retain per-diagram diagnostics,
// and return only actual SVG-render successes for the content cache.
import { renderMermaid } from '@mermaid-js/mermaid-cli';
import puppeteer from 'puppeteer';

async function main() {
  let input = '';
  for await (const chunk of process.stdin) input += chunk;
  const { diagrams, workers } = JSON.parse(input);
  const browser = await puppeteer.launch({ headless: 'shell' });
  try {
    const results = new Array(diagrams.length);
    let next = 0;
    await Promise.all(Array.from({ length: Math.min(workers, diagrams.length) }, async () => {
      while (next < diagrams.length) {
        const index = next++;
        const { id, source } = diagrams[index];
        try {
          const { data } = await renderMermaid(browser, source, 'svg');
          if (!Buffer.from(data).toString('utf8').includes('<svg')) {
            throw new Error('Mermaid returned success without an SVG.');
          }
          results[index] = { id, error: null };
        } catch (error) {
          results[index] = { id, error: error.message || String(error) };
        }
      }
    }));
    process.stdout.write(JSON.stringify(results));
  } finally {
    await browser.close();
  }
}

main().catch(error => {
  console.error(error.stack || String(error));
  process.exitCode = 1;
});
