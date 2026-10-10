# 👋 Hallo, ich bin Bayram Dökmeci

**Digitaler Architekt | B2B Lead-Gen Experte | Full-Stack Entwickler**

Ich unterstütze Unternehmen und Agenturen in Deutschland, Österreich und der Schweiz (DACH) bei der digitalen Skalierung. Da ich remote aus der Türkei arbeite, biete ich meinen Kunden höchste Qualität und reibungslose, deutschsprachige Kommunikation zu unschlagbaren Konditionen.

💡 **Mein USP für dich:** DACH-Agentur-Qualität + Remote-Preise + Fließendes Deutsch (Keine Sprachbarrieren in Meetings!).

---

## 🚀 Meine Kernkompetenzen & Services

Ich biete nicht nur isolierte Einzelleistungen, sondern greife auf ein breites Spektrum an digitalen Lösungen zurück, um dein Business ganzheitlich voranzubringen:

### 1. 🌐 Full Stack Web-Infrastrukturen & pSEO
*   **Webentwicklung:** Frontend & Backend (HTML5, Tailwind CSS, Alpine.js, PHP, MySQL, JavaScript).
*   **CMS & Systeme:** Tiefe Expertise in WordPress (Custom Directory/Business Sites) und statischen Site-Generatoren (Astro.js, HTMX).
*   **Infrastruktur:** Betreuung kompletter Self-Hosted-Umgebungen, Server-Deployments, Cloudflare-Architekturen (R2, Page Rules) und DNS-Management.
*   **Programmatic SEO (pSEO):** Aufbau skalierbarer, KI-gestützter Landingpage-Systeme für maximale organische Reichweite.

### 2. 🎯 B2B Leadgenerierung & Outreach
*   **Organic Growth:** Strategische B2B-Leadgenerierung und Personal Profile Optimization (Fokus auf LinkedIn & Sales Navigator).
*   **Automatisierung:** Aufbau hocheffizienter Workflows mit **n8n** zur automatisierten Datenverarbeitung, Content-Generierung und Lead-Nurturing.
*   **CRM & Marketing:** Einrichtung und Management von HubSpot, Mailchimp und gezielten Ads-Kampagnen.

### 3. 🎬 Visual Content & 2D Animationen
*   **Erklärvideos & Animationen:** Konzeption und Erstellung von 2D-Animationen, die komplexe B2B-Produkte oder Dienstleistungen verständlich und konversionsstark erklären.
*   **Creative Sourcing:** Effizientes Management von Visuals und Web-Assets zur Steigerung der User Experience.

### 4. 📈 Business Development & Strategie
*   **Consulting:** Jahrelange Erfahrung als Business Development Consultant (Fokus auf B2B-Sales-Maschinen und Markteintrittsstrategien).
*   **Mehrsprachig:** Ich verhandle und kommuniziere fließend in Deutsch, Englisch, Niederländisch und Türkisch.

---

## 🛠 Mein Tech-Stack & Tools
`Tailwind CSS` | `Alpine.js` | `PHP` | `MySQL` | `WordPress` | `Cloudflare` | `n8n` | `Docker` | `HubSpot` | `LinkedIn Sales Navigator`

---

## 📬 Lass uns dein Projekt besprechen

Egal ob es um eine neue Web-Infrastruktur, einen automatisierten Lead-Gen-Funnel oder 2D-Animationen geht – ich bin direkt erreichbar. Keine Zwischenhändler, kein Projektmanager-Flaschenhals.

*   📧 **E-Mail:** [bayramdokmeci@gmail.com](mailto:bayramdokmeci@gmail.com)
*   💬 **WhatsApp:** [+90 507 882 7795](https://wa.me/905078827795)
*   💬 **LinkedIn:** https://www.linkedin.com/in/bayramdoekmeci

> *"Maximale Performance und direkte Kommunikation – Remote aus der Türkei für die DACH-Region."*

## Startseite lokal ansehen

Die Startseite benötigt keinen Build-Schritt. Layout und Interaktionen liegen in `assets/landing.css` und `assets/landing.js`; die Unterseiten bleiben eigenständige HTML-Seiten.

```sh
python -m http.server 4173 --bind 127.0.0.1
```

Anschließend `http://127.0.0.1:4173` im Browser öffnen. Die Seite nutzt lokale Assets, native FAQ-Elemente und berücksichtigt reduzierte Bewegung.

## Strukturierte Daten prüfen

Vor der Veröffentlichung alle Seiten lokal prüfen (Python 3.9 oder neuer, keine Zusatzpakete):

```sh
python scripts/validate_structured_data.py
```

Die Prüfung erkennt ungültiges JSON-LD, doppelte JSON-Schlüssel, fehlerhafte Breadcrumbs, fehlende Pflichtangaben für LocalBusiness sowie Abweichungen zwischen FAQ-Markup und Seitentext. Anbieter werden als `LocalBusiness` mit der im Impressum veröffentlichten Anschrift ausgezeichnet. Die Startseite hat keinen Breadcrumb; Unterseiten verwenden mindestens zwei Einträge.

Nach dem Deployment die betroffenen URLs im [Google Rich Results Test](https://search.google.com/test/rich-results) erneut prüfen. Die lokale Prüfung ersetzt den Google-Test nicht und garantiert keine Darstellung als Rich Result. [FAQ-Rich-Results werden seit Mai 2026 nicht mehr angezeigt](https://developers.google.com/search/updates#may-2026); das vorhandene FAQ-Markup beschreibt weiterhin die sichtbaren Fragen und Antworten.
