"""Build the static navigation homepage and its original SVG icons.

Run from any directory: python scripts/build_home.py
The delivered HTML works without JavaScript or a build step on the server.
"""

import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://bayramdoekmeci.de"

# slug, title, short description, searchable terms, custom SVG drawing
GROUPS = [
    ("entwicklung", "Web & Entwicklung", "Von der ersten Website bis zur individuellen Anwendung.", "#147ce5", "#65c6ff", [
        ("webentwicklung", "Webentwicklung", "Websites und digitale Systeme, die zu deinem Business passen.", "Website Homepage Frontend Backend HTML CSS", '<rect x="3" y="4" width="18" height="16" rx="2.5"/><path d="M3 9h18m-12 3-3 3 3 3m6-6 3 3-3 3M6 6.5h.01M9 6.5h.01"/>'),
        ("full-stack-entwickler", "Full-Stack-Entwicklung", "Frontend, Backend und Schnittstellen aus einer Hand.", "API PHP JavaScript Entwickler Programmierung", '<path d="m12 3 10 5-10 5L2 8Zm-9 9 9 4.5 9-4.5m-18 5 9 4.5 9-4.5"/>'),
        ("wordpress-cms-entwickler", "WordPress & CMS", "Individuelle Themes, Plugins und flexible Content-Systeme.", "Content Management Website Blog", '<circle cx="12" cy="12" r="9.5"/><path d="m5.5 8 3.2 9 3.3-9 3.3 9 3.2-9M4.5 8h4m1.5 0h4m2.5 0h3"/>'),
        ("web-app", "Web-Apps", "Interne Tools, Kundenportale und individuelle Software.", "Anwendung Dashboard SaaS Programmierung", '<rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><path d="M17.5 14v7M14 17.5h7"/>'),
        ("shopware", "Shopware & E-Commerce", "Shop-Wartung, Qualitätssicherung und Shopify-Betreuung.", "Onlineshop Shop Test QA Shopify", '<path d="M4 8h16l1 12H3ZM8 8V6a4 4 0 0 1 8 0v2"/><path d="m9 14 2 2 4-4"/>'),
    ]),
    ("marketing", "Marketing & Sichtbarkeit", "Die richtigen Menschen erreichen. Und in Verbindung bleiben.", "#ed7621", "#ffc75a", [
        ("digitales-marketing", "Digitales Marketing", "Strategie, Performance und MarTech für dein Wachstum.", "Growth Online Marketing Kampagnen", '<path d="m3 10 14-5v14L3 14Zm14-1 4 1v3l-4 1M6 15l2 6h4l-2-5"/><path d="M21 4 19 6m2 14-2-2"/>'),
        ("programmatic", "Programmatic SEO", "Skalierbare Landingpages mit durchdachter Seitenarchitektur.", "Suchmaschinenoptimierung pSEO Google Suchmaschine", '<rect x="3" y="3" width="13" height="15" rx="2"/><path d="M8 21h11a2 2 0 0 0 2-2V8M7 7h5M7 11h5M7 15h2"/>'),
        ("sea", "SEA & Google Ads", "Suchanzeigen, Conversion-Tracking und Kampagnenoptimierung.", "Werbung Microsoft Ads Suchmaschinenwerbung PPC", '<circle cx="11" cy="11" r="8"/><circle cx="11" cy="11" r="4"/><path d="m21 21-5-5M11 8v3l2 1"/>'),
        ("linkedin", "LinkedIn", "B2B-Positionierung, Content, Ads und Zielkundenrecherche.", "Sales Navigator Netzwerk Profil", '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M7 10v7m0-10v.01m4 10v-7m0 3a3 3 0 0 1 6 0v4"/>'),
        ("email-marketing", "E-Mail-Marketing", "Newsletter und automatisierte Strecken für deine Kontakte.", "Email Newsletter Mailchimp HubSpot Lead Nurturing", '<rect x="2.5" y="5" width="19" height="14" rx="2.5"/><path d="m3 6 9 7 9-7"/>'),
        ("social-media", "Social Media", "Content, Community und Paid Social mit klarem Plan.", "Instagram Facebook Socialmedia Redaktion", '<path d="M20 11.5a8 8 0 0 1-8 8H4l1.3-4A8 8 0 1 1 20 11.5Z"/><path d="M8.5 10.5c0-3 3.5-3 3.5-.5 0-2.5 3.5-2.5 3.5.5 0 2-3.5 4-3.5 4s-3.5-2-3.5-4Z"/>'),
        ("kartendienst", "Local SEO & Maps", "Standortprofile und konsistente Daten für lokale Sichtbarkeit.", "Google Business Profile Apple Maps Bing Places Kartendienst", '<path d="M19 10c0 5-7 11-7 11S5 15 5 10a7 7 0 0 1 14 0Z"/><circle cx="12" cy="10" r="2.5"/>'),
    ]),
    ("automation", "KI, Daten & Automation", "Weniger Handarbeit. Mehr Raum für das Wesentliche.", "#8655de", "#caa2ff", [
        ("ki", "KI-Automatisierung", "KI-Workflows, Wissenssuche und kontrollierte CRM-Übergaben.", "AI Künstliche Intelligenz RAG Chatbot Agent", '<path d="m12 2 2.8 7.2L22 12l-7.2 2.8L12 22l-2.8-7.2L2 12l7.2-2.8ZM20 2v4m-2-2h4"/>'),
        ("n8n", "n8n & Workflows", "Prozesse automatisieren und Tools sinnvoll verbinden.", "Automation API CRM Integration Schnittstellen", '<rect x="2" y="8" width="6" height="7" rx="2"/><rect x="16" y="2" width="6" height="6" rx="2"/><rect x="16" y="16" width="6" height="6" rx="2"/><path d="M8 11.5h3a2 2 0 0 0 2-2V7a2 2 0 0 1 2-2h1m-8 6.5h3a2 2 0 0 1 2 2V17a2 2 0 0 0 2 2h1"/>'),
        ("data-engineering", "Data Engineering", "Datenpipelines, Datenqualität und eine nutzbare KI-Basis.", "Datenbank ETL RAG SQL Datenmodellierung", '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v7c0 4 16 4 16 0V5M4 12v7c0 4 16 4 16 0v-7"/>'),
    ]),
    ("design", "Design & visuelle Geschichten", "Ideen sichtbar machen. Komplexes verständlich erzählen.", "#d94b79", "#ffa3be", [
        ("design-content", "Design & Content", "Visuelle Identität und Inhalte, die deine Marke weiterbringen.", "Grafik Branding Webdesign Creative", '<path d="m14 3 7 7-10 10-8 1 1-8ZM12 5l7 7M4 14l6 6M3 21l4-4"/><path d="m14 3 2-1 6 6-1 2"/>'),
        ("videoproduktion", "Videoproduktion", "Videos, Schnitt und VFX für Produkte, Marken und Social Media.", "Film Video Editing White Label", '<rect x="2" y="5" width="14" height="15" rx="2"/><path d="m16 10 6-4v13l-6-4M2 9h14m-10-4 4 4m2-4 4 4"/>'),
        ("motion-graphics", "Motion Graphics", "Erkläranimationen, Brand Motion und bewegte Typografie.", "2D Animation Motion Design Erklärvideo", '<path d="m10 5 11 7-11 7Z"/><path d="M3 5v14M6 8v8"/>'),
        ("3d", "3D-Visualisierung", "Architektur, Innenräume und virtuelle Rundgänge in 3D.", "Archviz Architektur Rendering Animation Visualisierung", '<path d="m12 2 9 5v10l-9 5-9-5V7Zm0 10 9-5M12 12 3 7m9 5v10M7.5 4.5l9 5"/>'),
    ]),
    ("business", "Business & Kundenbeziehungen", "Neue Verbindungen aufbauen. Bestehende Beziehungen stärken.", "#149979", "#65d9b1", [
        ("business-development", "Business Development", "B2B-Leadgenerierung und qualifizierte Vertriebsübergaben.", "Sales Vertrieb LinkedIn Leads Akquise", '<path d="M3 20h18M5 16v-4m6 4V8m6 8V4M3 8l6-4 5 2 6-4"/>'),
        ("international-sales", "International Sales", "Go-to-Market, Pipeline Reviews und Vertriebssteuerung.", "Vertrieb Export Account Sales Director", '<circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="4" ry="9"/><path d="M3 12h18M5 6.5h14M5 17.5h14"/>'),
        ("b2b", "B2B-Partnerschaften", "Partnerstrategie, Partnergewinnung und gemeinsames Wachstum.", "Partnership Manager Co-Selling Partner Operations", '<path d="m8 8 3-3 5 1 6 6-5 6-5 2-10-9 4-5 4 2m1-3-4 6 3 2 3-3 5 5M3 14l4 4m0-7 8 7"/>'),
        ("customer-success", "Customer Success", "Onboarding, Produktnutzung und langfristige Kundenentwicklung.", "Kundenerfolg User Adoption Account Management", '<path d="M12 21S2 15 2 8.5A5.5 5.5 0 0 1 12 5a5.5 5.5 0 0 1 10 3.5C22 15 12 21 12 21Z"/><path d="m8 11 3 3 5-5"/>'),
        ("deutschsprachiges-back-office", "Back-Office", "Tickets, CRM-Pflege und operative Unterstützung auf Deutsch.", "Deutschsprachig Support Administration Assistenz", '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M8 5V3h8v2M7 10h10M7 14h6M7 18h4"/>'),
        ("kundenbetreuer", "Kundenbetreuung", "Persönlicher Service und verlässliche Nachverfolgung für B2B.", "Kundenbetreuer Deutschsprachig Remote Service Support", '<path d="M3 13v-2a9 9 0 0 1 18 0v2M21 16v2a3 3 0 0 1-3 3h-4"/><rect x="2" y="11" width="5" height="7" rx="2"/><rect x="17" y="11" width="5" height="7" rx="2"/>'),
    ]),
]

LEGAL = [
    ("impressum", "Impressum", "Anbieterkennzeichnung und Kontakt.", "", '<circle cx="12" cy="12" r="9"/><path d="M12 11v6m0-10v.01"/>'),
    ("datenschutz", "Datenschutz", "Informationen zum Umgang mit personenbezogenen Daten.", "", '<path d="m12 2 9 4v6c0 6-9 10-9 10S3 18 3 12V6Z"/><rect x="8" y="10" width="8" height="7" rx="1.5"/><path d="M10 10V8a2 2 0 0 1 4 0v2"/>'),
]
EXTRA_ICONS = [
    ("alle", "Alle Leistungen", "", "", '<rect x="3" y="3" width="6" height="6" rx="1.5"/><rect x="15" y="3" width="6" height="6" rx="1.5"/><rect x="3" y="15" width="6" height="6" rx="1.5"/><rect x="15" y="15" width="6" height="6" rx="1.5"/>'),
]


def make_icon(entry, dark, light):
    slug, name, _, _, drawing = entry
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-labelledby="title">
<title id="title">{escape(name)}</title>
<defs><linearGradient id="bg" x1="0" y1="0" x2=".35" y2="1"><stop stop-color="{light}"/><stop offset="1" stop-color="{dark}"/></linearGradient><linearGradient id="shine" x2="0" y2="1"><stop stop-color="#fff" stop-opacity=".45"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>
<rect x="2" y="2" width="60" height="60" rx="16" fill="url(#bg)"/>
<rect x="2.5" y="2.5" width="59" height="59" rx="15.5" fill="none" stroke="url(#shine)"/>
<path d="M7 22C7 12 12 7 22 7h20c10 0 15 5 15 15v8C40 24 24 37 7 29Z" fill="#fff" opacity=".08"/>
<g transform="translate(13 13) scale(1.5833)" fill="none" stroke="#fff" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round">{drawing}</g></svg>\n'''


def arrow():
    return '<svg class="arrow" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M5 12h14m-6-6 6 6-6 6"/></svg>'


def main():
    icon_dir = ROOT / "assets" / "icons"
    icon_dir.mkdir(parents=True, exist_ok=True)
    entries = [entry for *_, items in GROUPS for entry in items]
    for _, _, _, dark, light, items in GROUPS:
        for entry in items:
            (icon_dir / f"{entry[0]}.svg").write_text(make_icon(entry, dark, light), encoding="utf-8")
    for entry in LEGAL + EXTRA_ICONS:
        (icon_dir / f"{entry[0]}.svg").write_text(make_icon(entry, "#40545c", "#92a9ae"), encoding="utf-8")

    filters = '<button type="button" class="filter is-active" data-filter="all" aria-pressed="true">Alle <span>25</span></button>'
    short_names = ["Entwicklung", "Marketing", "KI & Daten", "Design", "Business"]
    sections = []
    for index, (key, title, description, _, _, items) in enumerate(GROUPS):
        filters += f'<button type="button" class="filter" data-filter="{key}" aria-pressed="false">{escape(short_names[index])}</button>'
        cards = []
        for slug, name, summary, keywords, _ in items:
            cards.append(f'''<li class="service" data-search="{escape(name + ' ' + summary + ' ' + keywords, quote=True)}">
  <a class="service-link" href="/{slug}/"><img class="app-icon" src="assets/icons/{slug}.svg" width="64" height="64" alt="" loading="lazy" decoding="async">
    <span class="service-copy"><span class="service-title">{escape(name)}</span><span class="service-description">{escape(summary)}</span></span>
    {arrow()}
  </a>
</li>''')
        sections.append(f'''<section class="service-group" id="{key}" data-group="{key}" aria-labelledby="heading-{key}">
  <div class="group-heading"><div><p class="section-index">0{index + 1}</p><h3 id="heading-{key}">{escape(title)}</h3><p>{escape(description)}</p></div><span class="group-count" aria-label="{len(items)} Leistungen">{len(items):02d}</span></div>
  <ul class="service-grid">{''.join(cards)}</ul>
</section>''')

    lookup = {entry[0]: entry for entry in entries}
    dock = []
    for slug, label in [("webentwicklung", "Web"), ("digitales-marketing", "Marketing"), ("ki", "KI"), ("n8n", "Workflows"), ("design-content", "Design"), ("business-development", "Business")]:
        name = lookup[slug][1]
        dock.append(f'''<a class="dock-item" href="/{slug}/" aria-label="{escape(name)}"><span class="dock-tooltip" aria-hidden="true">{escape(name)}</span><img src="assets/icons/{slug}.svg" width="64" height="64" alt="" fetchpriority="high"><span class="dock-label" aria-hidden="true">{label}</span></a>''')
    dock.append('<span class="dock-divider" aria-hidden="true"></span><a class="dock-item dock-all" href="#leistungen" aria-label="Alle 25 Leistungen entdecken"><span class="dock-tooltip" aria-hidden="true">Alle Leistungen</span><img src="assets/icons/alle.svg" width="64" height="64" alt=""><span class="dock-label" aria-hidden="true">Alle</span></a>')

    title = "Digitale Leistungen für B2B | Bayram Dökmeci"
    description = "Webentwicklung, Marketing, KI, Design und Business Development: Alle Leistungen von Bayram Dökmeci für Unternehmen und Agenturen in DACH im Überblick."
    graph = {
        "@context": "https://schema.org", "@graph": [
            {"@type": "Person", "@id": ORIGIN + "/#person", "name": "Bayram Dökmeci", "url": ORIGIN + "/", "jobTitle": "Digitaler Architekt und Full-Stack-Entwickler", "knowsLanguage": ["de", "en", "nl", "tr"], "worksFor": {"@id": ORIGIN + "/#business"}, "sameAs": ["https://www.linkedin.com/in/bayramdoekmeci/", "https://github.com/bdokmeci"]},
            {"@type": "LocalBusiness", "@id": ORIGIN + "/#business", "name": "MeinB2B – Bayram Dökmeci", "url": ORIGIN + "/", "founder": {"@id": ORIGIN + "/#person"}, "address": {"@type": "PostalAddress", "streetAddress": "Konyaaltı Blv.", "postalCode": "07070", "addressLocality": "Antalya", "addressCountry": "TR"}, "telephone": "+905078827795", "email": "kontakt@bayramdoekmeci.de", "areaServed": ["Deutschland", "Österreich", "Schweiz"], "contactPoint": {"@type": "ContactPoint", "contactType": "Kundenservice", "email": "kontakt@bayramdoekmeci.de", "availableLanguage": ["German", "English", "Dutch", "Turkish"]}},
            {"@type": "WebSite", "@id": ORIGIN + "/#website", "url": ORIGIN + "/", "name": "Bayram Dökmeci – MeinB2B", "inLanguage": "de", "publisher": {"@id": ORIGIN + "/#business"}},
            {"@type": "CollectionPage", "@id": ORIGIN + "/#page", "url": ORIGIN + "/", "name": title, "description": description, "inLanguage": "de", "isPartOf": {"@id": ORIGIN + "/#website"}, "about": {"@id": ORIGIN + "/#person"}, "mainEntity": {"@id": ORIGIN + "/#leistungen"}},
            {"@type": "ItemList", "@id": ORIGIN + "/#leistungen", "name": "Digitale Leistungen für Unternehmen und Agenturen", "numberOfItems": len(entries), "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": entry[1], "description": entry[2], "url": f"{ORIGIN}/{entry[0]}/"} for i, entry in enumerate(entries)]},
        ]
    }
    legal_links = ''.join(f'<a href="/{entry[0]}/"><img src="assets/icons/{entry[0]}.svg" width="24" height="24" alt="" loading="lazy">{entry[1]}</a>' for entry in LEGAL)
    html = f'''<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(description)}">
  <meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large">
  <meta name="theme-color" content="#f6f8f7">
  <meta name="author" content="Bayram Dökmeci">
  <link rel="canonical" href="{ORIGIN}/">
  <link rel="icon" type="image/svg+xml" href="assets/icons/alle.svg">
  <link rel="alternate" type="text/markdown" href="index.md" title="Leistungsübersicht als Markdown">
  <link rel="preload" href="assets/fonts/inter-latin-variable.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="assets/home.css">
  <script src="assets/home.js" defer></script>
  <meta property="og:type" content="website">
  <meta property="og:locale" content="de_DE">
  <meta property="og:site_name" content="Bayram Dökmeci – MeinB2B">
  <meta property="og:title" content="{escape(title)}">
  <meta property="og:description" content="{escape(description)}">
  <meta property="og:url" content="{ORIGIN}/">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{escape(title)}">
  <meta name="twitter:description" content="{escape(description)}">
  <script type="application/ld+json">{json.dumps(graph, ensure_ascii=False, separators=(',', ':'))}</script>
</head>
<body>
  <a class="skip-link" href="#leistungen">Zur Leistungsübersicht springen</a>
  <div class="scroll-progress" aria-hidden="true"></div>
  <header class="site-header wrap">
    <a class="brand" href="/" aria-label="Bayram Dökmeci – Startseite"><span class="brand-symbol" aria-hidden="true">b<span>.</span></span><span>Bayram Dökmeci<span class="brand-subline">DIGITAL DENKEN. PERSÖNLICH MACHEN.</span></span></a>
    <nav class="header-nav" aria-label="Hauptnavigation"><a class="overview-link" href="#leistungen">Leistungen</a><a class="contact-link" href="#kontakt">Lass uns sprechen {arrow()}</a></nav>
  </header>
  <main id="main">
    <section class="hero" aria-labelledby="hero-title">
      <div class="hero-landscape" aria-hidden="true"><div class="landscape-orb"></div><div class="landscape-ridge ridge-back"></div><div class="landscape-ridge ridge-front"></div></div>
      <div class="wrap hero-content">
        <p class="eyebrow"><span></span> DEIN DIGITALER PARTNER FÜR B2B</p>
        <h1 id="hero-title">Ein guter Start.<br><span>Für dein digitales Business.</span></h1>
        <p class="hero-description">Webentwicklung, Marketing, KI und Design.<br class="desktop-break"> Entdecke, was dein Unternehmen weiterbringt.</p>
        <a class="hero-explore" href="#leistungen">Alle Leistungen entdecken {arrow()}</a>
        <div class="dock-anchor" id="dock-anchor">
          <nav class="dock" aria-label="Schnellnavigation zu ausgewählten Leistungen"><div class="dock-track">{''.join(dock)}</div></nav>
        </div>
        <p class="dock-caption"><span class="pointer-hint">Ein Icon. Dein nächster Schritt.</span><span class="touch-hint">Antippen & entdecken. Im Dock seitlich wischen.</span></p>
      </div>
      <div class="hero-bottom wrap"><span>25 Leistungen. Ein direkter Ansprechpartner.</span><span class="remote-note"><span></span> Remote aus Antalya · Für DACH</span></div>
    </section>
    <section class="directory wrap" id="leistungen" aria-labelledby="directory-title" tabindex="-1">
      <div class="directory-heading"><div><p class="eyebrow muted">DEIN WEG ZUR PASSENDEN LÖSUNG</p><h2 id="directory-title">Was hast du vor?</h2></div><p>Von der Idee bis zur Umsetzung.<br>Finde den Bereich, der zu dir passt.</p></div>
      <div class="directory-tools" hidden>
        <div class="filters" role="group" aria-label="Leistungen nach Bereich filtern">{filters}</div>
        <div class="search-field"><svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></svg><label class="sr-only" for="service-search">Leistungen durchsuchen</label><input id="service-search" type="search" placeholder="Leistung finden …" autocomplete="off" spellcheck="false" aria-controls="service-groups"><kbd aria-hidden="true">/</kbd></div>
      </div>
      <p id="filter-status" class="filter-status sr-only" role="status" aria-live="polite" aria-atomic="true"></p>
      <div id="service-groups">{''.join(sections)}</div>
      <div class="no-results" hidden><span aria-hidden="true">↗</span><h3>Gerade kein Treffer.</h3><p>Probiere einen anderen Begriff oder entdecke alle Leistungen.</p><button type="button" id="reset-search">Alle Leistungen anzeigen {arrow()}</button></div>
      <noscript><p class="noscript-note">Alle Leistungen sind direkt verlinkt. Suche, Filter und Dock-Animationen stehen mit JavaScript zur Verfügung.</p></noscript>
    </section>
    <section class="contact-section wrap" id="kontakt" aria-labelledby="contact-title">
      <div class="contact-panel"><div class="contact-copy"><p class="eyebrow">GUTE ZUSAMMENARBEIT BEGINNT MIT EINEM GESPRÄCH.</p><h2 id="contact-title">Vieles ist möglich.<br><span>Was ist deine Idee?</span></h2><p>Ich bin Bayram Dökmeci, digitaler Architekt und Full-Stack-Entwickler hinter MeinB2B. Ich unterstütze Unternehmen und Agenturen in Deutschland, Österreich und der Schweiz – remote aus Antalya, persönlich und auf Deutsch.</p><a class="primary-button" href="https://calendly.com/bayramdokmeci/b2b" target="_blank" rel="noopener noreferrer">Projekt besprechen {arrow()}<span class="sr-only"> (öffnet in einem neuen Tab)</span></a><a class="email-link" href="mailto:kontakt@bayramdoekmeci.de">Lieber per E-Mail? {arrow()}</a></div><div class="contact-art" aria-hidden="true"><div class="art-orbit orbit-one"></div><div class="art-orbit orbit-two"></div><span class="art-monogram">b.</span><span class="art-caption">IDEEN VERBINDEN.</span></div></div>
      <div class="contact-details"><span>Direkter Kontakt. Kurze Wege.</span><a href="mailto:kontakt@bayramdoekmeci.de">kontakt@bayramdoekmeci.de</a><a href="https://wa.me/905078827795" target="_blank" rel="noopener noreferrer">WhatsApp · +90 507 882 7795<span class="sr-only"> (öffnet in einem neuen Tab)</span></a></div>
    </section>
  </main>
  <footer class="site-footer wrap"><div><a class="footer-brand" href="/">Bayram Dökmeci<span>.</span></a><p>Digitale Lösungen. Persönlich verbunden.</p><small>© 2026 MeinB2B · Für Unternehmen & Agenturen.</small></div><nav aria-label="Weitere Seiten und Profile">{legal_links}<a href="https://www.linkedin.com/in/bayramdoekmeci/" target="_blank" rel="noopener noreferrer">LinkedIn {arrow()}<span class="sr-only"> (öffnet in einem neuen Tab)</span></a><a href="#main">Nach oben ↑</a></nav></footer>
</body>
</html>
'''
    (ROOT / "index.html").write_text(html, encoding="utf-8")
    markdown = f'''---
title: "{title}"
description: "{description}"
url: "{ORIGIN}/"
---

# Digitale Leistungen von Bayram Dökmeci

Bayram Dökmeci ist digitaler Architekt und Full-Stack-Entwickler hinter MeinB2B. Er unterstützt Geschäftskunden und Agenturen in Deutschland, Österreich und der Schweiz. Die Zusammenarbeit erfolgt remote aus Antalya, Türkiye, mit direkter Kommunikation auf Deutsch.

25 Leistungen in fünf Bereichen. Jede verlinkte Unterseite beschreibt das jeweilige Angebot.
'''
    for _, name, summary, _, _, items in GROUPS:
        markdown += f"\n## {name}\n\n{summary}\n\n"
        markdown += '\n'.join(f"- [{entry[1]}]({ORIGIN}/{entry[0]}/): {entry[2]}" for entry in items) + '\n'
    markdown += f"\n## Kontakt\n\n- [Projekt besprechen](https://calendly.com/bayramdokmeci/b2b)\n- E-Mail: [kontakt@bayramdoekmeci.de](mailto:kontakt@bayramdoekmeci.de)\n- Telefon und WhatsApp: +90 507 882 7795\n\n## Rechtliches\n\n- [Impressum]({ORIGIN}/impressum/)\n- [Datenschutz]({ORIGIN}/datenschutz/)\n"
    (ROOT / "index.md").write_text(markdown, encoding="utf-8")
    print(f"Built homepage with {len(entries)} services and {len(entries) + len(LEGAL) + len(EXTRA_ICONS)} SVG icons.")


if __name__ == "__main__":
    main()
