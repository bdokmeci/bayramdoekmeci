/**
 * Build index.toon (Token-Oriented Object Notation) for each index.html.
 *
 * TOON is a line-oriented, token-efficient serialization format designed for LLMs.
 * Each index.toon stores:
 *  - Page metadata (title, description, canonical url, language, locale, alternates)
 *  - Full Schema.org JSON-LD structured data (@context and @graph)
 *
 * Usage: node scripts/build_toon.mjs
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { encode, decode } from '@toon-format/toon';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, '..');

function unescapeHtml(text) {
  return text
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&uuml;/g, 'ü')
    .replace(/&Uuml;/g, 'Ü')
    .replace(/&auml;/g, 'ä')
    .replace(/&Auml;/g, 'Ä')
    .replace(/&ouml;/g, 'ö')
    .replace(/&Ouml;/g, 'Ö')
    .replace(/&szlig;/g, 'ß');
}

function findIndexHtmlFiles(dir) {
  let results = [];
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    if (entry.name === 'node_modules' || entry.name === '.git' || entry.name === '.gemini') {
      continue;
    }
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      results = results.concat(findIndexHtmlFiles(fullPath));
    } else if (entry.isFile() && entry.name === 'index.html') {
      results.push(fullPath);
    }
  }
  return results;
}

export function extractPageData(htmlContent, filePath) {
  const titleMatch = htmlContent.match(/<title>([\s\S]*?)<\/title>/i);
  const title = titleMatch ? unescapeHtml(titleMatch[1].trim()) : '';

  const descMatch =
    htmlContent.match(/<meta[^>]*name=["']description["'][^>]*content=["']([^"']*)["']/i) ||
    htmlContent.match(/<meta[^>]*content=["']([^"']*)["'][^>]*name=["']description["']/i);
  const description = descMatch ? unescapeHtml(descMatch[1].trim()) : '';

  const canonicalMatch =
    htmlContent.match(/<link[^>]*rel=["']canonical["'][^>]*href=["']([^"']*)["']/i) ||
    htmlContent.match(/<link[^>]*href=["']([^"']*)["'][^>]*rel=["']canonical["']/i);
  const canonical = canonicalMatch ? canonicalMatch[1].trim() : '';

  const langMatch = htmlContent.match(/<html[^>]*lang=["']([^"']*)["']/i);
  const language = langMatch ? langMatch[1].trim() : '';

  const localeMatch =
    htmlContent.match(/<meta[^>]*property=["']og:locale["'][^>]*content=["']([^"']*)["']/i) ||
    htmlContent.match(/<meta[^>]*content=["']([^"']*)["'][^>]*property=["']og:locale["']/i);
  const locale = localeMatch ? localeMatch[1].trim() : '';

  const alternates = {};
  const altRegex = /<link\b(?=[^>]*\brel=["']alternate["'])(?=[^>]*\bhreflang=["']([^"']+)["'])(?=[^>]*\bhref=["']([^"']+)["'])[^>]*>/gi;
  for (const m of htmlContent.matchAll(altRegex)) {
    alternates[m[1]] = m[2];
  }

  const schemaMatch = htmlContent.match(/<script[^>]*type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/i);
  if (!schemaMatch) {
    throw new Error(`Missing application/ld+json in ${filePath}`);
  }
  const rawSchema = JSON.parse(schemaMatch[1].trim());

  return {
    title,
    description,
    url: canonical,
    language,
    locale,
    alternates,
    schema: {
      '@context': rawSchema['@context'] || 'https://schema.org',
      '@graph': rawSchema['@graph'] || rawSchema,
    },
  };
}

export function buildToonFiles() {
  const htmlFiles = findIndexHtmlFiles(ROOT);
  htmlFiles.sort();

  let totalJsonBytes = 0;
  let totalToonBytes = 0;
  const builtFiles = [];

  for (const htmlPath of htmlFiles) {
    const htmlContent = fs.readFileSync(htmlPath, 'utf8');
    const pageData = extractPageData(htmlContent, htmlPath);

    const jsonString = JSON.stringify(pageData, null, 2);
    const toonString = encode(pageData);

    // Verify roundtrip decode
    const decoded = decode(toonString);
    if (!decoded || decoded.url !== pageData.url) {
      throw new Error(`Roundtrip verification failed for ${htmlPath}`);
    }

    const toonPath = path.join(path.dirname(htmlPath), 'index.toon');
    fs.writeFileSync(toonPath, toonString + '\n', 'utf8');

    totalJsonBytes += Buffer.byteLength(jsonString, 'utf8');
    totalToonBytes += Buffer.byteLength(toonString, 'utf8');
    builtFiles.push(toonPath);
  }

  const savingsPercent = ((1 - totalToonBytes / totalJsonBytes) * 100).toFixed(1);
  const deCount = builtFiles.filter((p) => !path.relative(ROOT, p).startsWith('en' + path.sep)).length;
  const enCount = builtFiles.length - deCount;

  console.log(`Built ${builtFiles.length} TOON files (${deCount} DE, ${enCount} EN).`);
  console.log(
    `Size reduction: ${(totalJsonBytes / 1024).toFixed(1)} KB (JSON) -> ${(totalToonBytes / 1024).toFixed(1)} KB (TOON) [-${savingsPercent}%]`
  );

  return builtFiles;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  buildToonFiles();
}
