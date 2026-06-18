# signorini.cloud — Claude Instructions

Hugo portfolio site for Ivens Signorini. Deployed to signorini.cloud via GitHub Pages (gh-pages branch).

## Project structure

- `config/_default/` — split config (hugo.toml + menus.*.toml)
- `content/` — multilingual pages: `.en.md` primary, `.it.md` / `.es.md` / `.pt.md` stubs
- `assets/scss/main.scss` — dark-first CSS
- `assets/js/main.js` — theme/accent/font switching, scroll reveal
- `data/` — flat YAML: contact, site, facts, experience, stack, projects, education
- `layouts/partials/` — hero, about, stack, experience, project, contact, footer
- `archetypes/blog.md` — blog post template

## Blog post rules

Every blog post must be created in at least **English** (`.en.md`) and **Italian** (`.it.md`).

### Required sections (in order)

1. **Hook** — 1–2 sentence opening that frames the tension or problem
2. **The problem** — what breaks or is misunderstood without this knowledge
3. **What [topic] is** — definition + mental model
4. **Diagrams** — include at minimum:
   - A `C4Context` diagram (system context, Mermaid)
   - A `sequenceDiagram` (protocol or request flow, Mermaid)
   - Optional: `C4Dynamic` for complex flows
5. **Core concept sections** — 2–4 H2 sections covering the substance
6. **History / adoption timeline** — bullet list with dates (when relevant)
7. **Design principles** — numbered list titled "What makes a good [topic]" (when relevant)
8. **Where it goes from here** — 1–2 forward-looking paragraphs
9. **Further reading** — 4–6 external links with one-line descriptions
10. **About the author** — fixed bio block (see below)

### Front matter

```yaml
---
title: ""
date: YYYY-MM-DD
description: ""  # one sentence, used in meta and listing cards
draft: false
---
```

### Diagrams

- Always use Mermaid fenced code blocks (` ```mermaid `)
- C4 diagrams: follow skill `c4-architecture` conventions
- Sequence diagrams: number steps in `Note over` blocks, show the full lifecycle
- Keep diagrams under 15 nodes — split if larger

### Tone

- Direct, technical, no filler
- First-person perspective ("I", "we") avoided — write as informed observer
- Code examples when the concept has an implementation dimension
- No trailing summaries ("In conclusion…", "As we've seen…")

### Author bio (fixed — do not modify)

**English:**
> **Ivens Signorini** is a Senior Backend Engineer focused on distributed systems, AI infrastructure, and high-performance APIs. He works primarily in Go and TypeScript, building systems that run at scale. His technical interests include protocol design, concurrency patterns, and the architecture of AI-native applications. He writes at [signorini.cloud](https://signorini.cloud).

**Italian:**
> **Ivens Signorini** è un Senior Backend Engineer specializzato in sistemi distribuiti, infrastruttura AI e API ad alte prestazioni. Lavora principalmente in Go e TypeScript, costruendo sistemi che operano su larga scala. I suoi interessi tecnici includono il design dei protocolli, i pattern di concorrenza e l'architettura delle applicazioni AI-native. Scrive su [signorini.cloud](https://signorini.cloud).

## Data patterns

- Translatable text lives in `content/_index.{lang}.md` front matter
- Structured data (experience, stack, projects) lives in `data/*.yaml` — flat, not language-keyed
- `{{ site.Data.X }}` pattern in partials

## Commands

```bash
hugo server -D          # dev server with drafts
hugo --minify           # production build
```
