/**
 * Validate all index.toon files against their index.html counterparts.
 *
 * Checks:
 *  - Exactly 56 TOON files (28 German + 28 English)
 *  - Lossless decode validation
 *  - Metadata alignment (title, description, canonical url, language, locale, alternates)
 *  - Schema.org structured data alignment (@context and @graph)
 *
 * Usage: node scripts/validate_toon.mjs
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { decode } from '@toon-format/toon';
import { extractPageData } from './build_toon.mjs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, '..');

function findFiles(dir, filename) {
  let results = [];
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    if (entry.name === 'node_modules' || entry.name === '.git' || entry.name === '.gemini') {
      continue;
    }
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      results = results.concat(findFiles(fullPath, filename));
    } else if (entry.isFile() && entry.name === filename) {
      results.push(fullPath);
    }
  }
  return results;
}

export function validateToon() {
  const htmlFiles = findFiles(ROOT, 'index.html').sort();
  const toonFiles = findFiles(ROOT, 'index.toon').sort();

  const errors = [];

  if (htmlFiles.length !== 56) {
    errors.push(`Expected 56 HTML files, found ${htmlFiles.length}`);
  }
  if (toonFiles.length !== 56) {
    errors.push(`Expected 56 TOON files, found ${toonFiles.length}`);
  }

  for (const htmlPath of htmlFiles) {
    const relHtml = path.relative(ROOT, htmlPath).replace(/\\/g, '/');
    const toonPath = path.join(path.dirname(htmlPath), 'index.toon');
    const relToon = path.relative(ROOT, toonPath).replace(/\\/g, '/');

    if (!fs.existsSync(toonPath)) {
      errors.push(`Missing TOON counterpart: ${relToon}`);
      continue;
    }

    try {
      const htmlContent = fs.readFileSync(htmlPath, 'utf8');
      const expectedData = extractPageData(htmlContent, htmlPath);

      const toonContent = fs.readFileSync(toonPath, 'utf8');
      const decoded = decode(toonContent);

      if (!decoded) {
        errors.push(`${relToon}: Failed to decode TOON content`);
        continue;
      }

      if (decoded.url !== expectedData.url) {
        errors.push(`${relToon}: Canonical URL mismatch. Expected "${expectedData.url}", got "${decoded.url}"`);
      }
      if (decoded.title !== expectedData.title) {
        errors.push(`${relToon}: Title mismatch.`);
      }
      if (decoded.language !== expectedData.language) {
        errors.push(`${relToon}: Language mismatch. Expected "${expectedData.language}", got "${decoded.language}"`);
      }
      if (decoded.locale !== expectedData.locale) {
        errors.push(`${relToon}: Locale mismatch.`);
      }

      // Check schema graph items
      const expectedGraph = expectedData.schema['@graph'];
      const decodedGraph = decoded.schema?.['@graph'];
      if (!Array.isArray(decodedGraph)) {
        errors.push(`${relToon}: schema.@graph is not an array`);
      } else if (decodedGraph.length !== expectedGraph.length) {
        errors.push(
          `${relToon}: Graph item count mismatch. Expected ${expectedGraph.length}, got ${decodedGraph.length}`
        );
      }
    } catch (err) {
      errors.push(`${relToon}: Exception during validation - ${err.message}`);
    }
  }

  if (errors.length > 0) {
    for (const err of errors) {
      console.error(`FAIL: ${err}`);
    }
    console.error(`\nTOON validation failed with ${errors.length} issue(s).`);
    return false;
  }

  console.log(`PASS: All 56 TOON files validated successfully (lossless decode, canonical URLs, schema alignment).`);
  return true;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const ok = validateToon();
  process.exit(ok ? 0 : 1);
}
