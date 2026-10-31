"""Compile page scripts/Alpine expressions and exercise homepage filtering in Node.

This is a source-level regression check, not a substitute for browser QA.
Requires Node.js on PATH; the website build itself needs only Python.
"""
import json
import subprocess
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Scripts(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.scripts, self.expressions, self.active, self.text = [], [], False, ''
        self.feed(source)

    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        if tag == 'script':
            self.active = not attrs.get('src') and attrs.get('type') != 'application/ld+json'
        for key, value in pairs:
            if not value: continue
            if key in ('x-data', 'x-text', 'x-html', 'x-show') or key.startswith((':', 'x-bind:')):
                self.expressions.append('return (' + value + ');')
            elif key.startswith(('@', 'x-on:')) or key == 'x-init':
                self.expressions.append(value)

    def handle_endtag(self, tag):
        if tag == 'script':
            if self.active: self.scripts.append(self.text)
            self.active, self.text = False, ''

    def handle_data(self, data):
        if self.active: self.text += data


def main():
    snippets = []
    for path in sorted(ROOT.glob('**/index.html')):
        parser = Scripts(path.read_text(encoding='utf-8'))
        for number, source in enumerate(parser.scripts + parser.expressions):
            snippets.append({'file': str(path.relative_to(ROOT)), 'number': number, 'source': source})
    for path in (ROOT / 'assets').glob('*.js'):
        snippets.append({'file': str(path.relative_to(ROOT)), 'number': 0, 'source': path.read_text(encoding='utf-8')})
    runner = r'''
const fs = require('fs');
const vm = require('vm');
const assert = require('assert/strict');
const snippets = JSON.parse(fs.readFileSync(0, 'utf8'));
let failures = 0;
for (const item of snippets) {
  try { new Function(item.source); }
  catch (error) { failures++; console.error(`${item.file} #${item.number}: ${error.message}`); }
}
console.log(`${snippets.length} JavaScript blocks and Alpine expressions compiled; ${failures} issues.`);
// Exercise translated computed strings, preserving template interpolation.
for (const slug of ['programmatic', 'kundenbetreuer', 'data-engineering']) {
  const factories = {}, events = {};
  const context = vm.createContext({ document: { documentElement: { classList: { add() {} } }, addEventListener(name, fn) { events[name] = fn; } }, Alpine: { data(name, fn) { factories[name] = fn; } } });
  const relevant = snippets.filter(item => item.file.replaceAll('\\', '/') === `en/${slug}/index.html` && !item.source.startsWith('return ('));
  // The first blocks register a factory; skip Alpine event-handler expressions.
  for (const item of relevant.filter(item => item.source.includes('Alpine.data(') || item.source.includes('function dataPage('))) vm.runInContext(item.source, context);
  if (events['alpine:init']) events['alpine:init']();
  if (slug === 'programmatic') {
    const page = factories.pseo();
    assert.equal(page.chartLabel, 'Illustrative pilot example: 12 possible pages, with 8 approved and 4 on hold.');
    page.scenario = 'expansion';
    assert.equal(page.chartLabel, 'Illustrative expansion example: 48 possible pages, with 32 approved and 16 on hold.');
    assert.ok(page.caption.startsWith('32 pages'));
  } else if (slug === 'kundenbetreuer') {
    const page = factories.customerCare();
    assert.equal(page.chartSummary, 'Everyday service: 7 answered directly, 3 requiring clarification, 2 passed to the specialist team.');
    page.selectSample('project');
    assert.equal(page.chartSummary, 'Project phase: 4 answered directly, 5 requiring clarification, 3 passed to the specialist team.');
  } else {
    const page = context.dataPage();
    assert.equal(page.format(1000), '1,000');
    assert.equal(page.current.name, 'CRM records');
    page.mode = 'docs';
    assert.equal(page.current.name, 'Knowledge documents');
  }
}
console.log('Inline locale regression: chart state changes, template interpolation and English number formatting passed.');
process.exitCode = failures ? 1 : 0;
'''
    result = subprocess.run(['node', '-e', runner], input=json.dumps(snippets), text=True, encoding='utf-8', capture_output=True)
    print(result.stdout, end='')
    print(result.stderr, end='')
    test = subprocess.run(['node', str(ROOT / 'scripts/test_home_locale.cjs')], text=True, encoding='utf-8', capture_output=True)
    print(test.stdout, end='')
    print(test.stderr, end='')
    return bool(result.returncode or test.returncode)


if __name__ == '__main__':
    raise SystemExit(main())
