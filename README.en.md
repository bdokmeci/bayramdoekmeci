# 👋 Hello, I’m Bayram Dökmeci

The homepage is a service directory with 25 offerings, individual SVG icons and search. It works as static HTML even without JavaScript. Styles and interactions live in `assets/home.css` and `assets/home.js`; the existing subpages retain their own assets.

Services, icon drawings and German homepage content are maintained in `scripts/build_home.py`. Run `python scripts/build_home.py` to generate both homepages, English subpages, Markdown counterparts, icons and URL inventories. Run `python scripts/validate_structured_data.py` to check structured data and `python scripts/validate_home.py` to check navigation, links, icons, language metadata and the sitemap. Start a local preview with `python -m http.server 5173 --bind 127.0.0.1`.

**Digital architect | B2B lead generation expert | Full-stack developer**

I help businesses and agencies in Germany, Austria and Switzerland (DACH) scale digitally. Working remotely from Türkiye allows me to offer my clients outstanding quality and straightforward communication in German at highly competitive rates.

💡 **What sets my service apart:** DACH agency quality + remote pricing + fluent German (no language barriers in meetings!).

## 🚀 My core skills and services

I offer more than individual services: I draw on a broad range of digital solutions to help your business progress as a whole.

### 1. 🌐 Full-stack web infrastructure & pSEO

- **Web development:** Frontend and backend (HTML5, Tailwind CSS, Alpine.js, PHP, MySQL, JavaScript).
- **CMS & systems:** Extensive expertise in WordPress (custom directory and business sites) and static site generators (Astro.js, HTMX).
- **Infrastructure:** Management of complete self-hosted environments, server deployments, Cloudflare architectures (R2, Page Rules) and DNS.
- **Programmatic SEO (pSEO):** Building scalable, AI-assisted landing page systems for maximum organic reach.

### 2. 🎯 B2B lead generation & outreach

- **Organic growth:** Strategic B2B lead generation and personal profile optimisation (focusing on LinkedIn and Sales Navigator).
- **Automation:** Building highly efficient workflows with **n8n** for automated data processing, content generation and lead nurturing.
- **CRM & marketing:** Setting up and managing HubSpot, Mailchimp and targeted advertising campaigns.

### 3. 🎬 Visual content & 2D animation

- **Explainer videos & animation:** Planning and creating 2D animations that explain complex B2B products or services clearly and encourage conversions.
- **Creative sourcing:** Efficient management of visuals and web assets to improve the user experience.

### 4. 📈 Business development & strategy

- **Consulting:** Years of experience as a business development consultant (focusing on B2B sales systems and market entry strategies).
- **Multilingual:** I negotiate and communicate fluently in German, English, Dutch and Turkish.

## 🛠 My technology stack & tools

`Tailwind CSS` | `Alpine.js` | `PHP` | `MySQL` | `WordPress` | `Cloudflare` | `n8n` | `Docker` | `HubSpot` | `LinkedIn Sales Navigator`

## 📬 Let’s discuss your project

Whether you need new web infrastructure, an automated lead generation funnel or 2D animation, you can reach me directly. No intermediaries or project management bottlenecks.

- 📧 **Email:** [bayramdokmeci@gmail.com](mailto:bayramdokmeci@gmail.com)
- 💬 **WhatsApp:** [+90 507 882 7795](https://wa.me/905078827795)
- 💬 **LinkedIn:** https://www.linkedin.com/in/bayramdoekmeci

> “Maximum performance and direct communication — working remotely from Türkiye for the DACH region.”

## Maintaining the English website

German routes remain unchanged. English pages use `/en/` followed by the same slug. `scripts/translations/routes.json` is the explicit generated mapping of all 28 page pairs. An English page is a translation of the existing offering; it does not change the target markets or the German-speaking service.

The German subpage HTML files are the layout and content source. Reviewed translations live in `scripts/translations/<slug>.json`; shared labels are in `common.json`, and the homepage catalogue is `home.json`. Keys are exact, decoded German text segments. Values are natural English, including the same punctuation or spacing needed by inline text. Keep FAQ answers identical between visible text and JSON-LD. Include dynamic strings from inline JavaScript and Alpine attributes when adding new content.

`scripts/localise.py` renders English HTML, handles locale URLs and metadata, creates English icons with translated titles and derives the English Markdown body from the translated page. Do not edit generated English HTML or Markdown directly: update the catalogue or German source, then rebuild. English Markdown retains headings, body content and links; it excludes site navigation, scripts and SVG drawings. German Markdown files are preserved (the original homepage generator continues to generate the German homepage Markdown).

English pages share language-neutral CSS and fonts. `assets/home.js` and `assets/landing.js` select messages using the HTML language. Other page scripts retain their behaviour while their display literals are translated at build time. The small language selector is styled by `assets/locale.css`.

`en/llms.txt`, this README and `landingpage-notizen.en.txt` are maintained English documentation. The German originals remain available. Font licences and third-party code are not translated. `_headers` and `robots.txt` retain their hosting behaviour. `.github/sync-on-change.ps1` is operational tooling, not website copy; do not run it during review because it commits and pushes automatically.

After editing, run:

```powershell
python scripts/build_home.py
python scripts/validate_home.py
python scripts/validate_structured_data.py
python scripts/validate_locales.py
python scripts/validate_javascript.py
```

Preview `/en/` and representative subpages on desktop and mobile. Check search, filters, empty results, navigation, language switching, chart controls, FAQs, keyboard use, reduced motion and JavaScript-disabled rendering. Build a second time and verify that generated files remain identical.

The optional JavaScript validator requires Node.js. It compiles inline scripts and Alpine expressions, exercises the actual homepage search/filter script against a small DOM fixture in both languages, and verifies translated chart state changes, template interpolation and number formatting. These source-level checks do not replace real browser testing.

## Source discrepancies retained for review

- The privacy policy says there are no analytics, while some source pages contain a Cloudflare Insights beacon. The translation preserves both the original wording and script; it does not resolve the policy discrepancy.
- The README uses `bayramdokmeci@gmail.com`; public page contact links use `kontakt@bayramdoekmeci.de`. Both original addresses are preserved.
- Language capabilities differ across structured data: the homepage lists German, English, Dutch and Turkish; several subpages list German and Turkish; the full-stack page also lists English. Translation does not add or remove capabilities.
- The German editorial notes describe historical homepage styling and past checks. Their English counterpart translates those notes; those historical checks are not evidence of validation performed during this translation.
- Two existing links from customer success and digital marketing pointed to the nonexistent `/customer-success/business-development/`; they now point to `/business-development/` in the German HTML and Markdown, and to its English equivalent in translated output. Empty-fragment menu links are also guarded against invalid selectors in the shared landing script and customer-care page.
- The web-development Markdown counterpart had a performance link pointing to a removed homepage section. It now links to `/webentwicklung/#performance`.
