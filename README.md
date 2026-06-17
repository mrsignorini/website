claude# signorini.cloud

Personal portfolio site for Ivens Signorini — Senior Backend Engineer. Built with [Hugo](https://gohugo.io/) and deployed to [signorini.cloud](https://signorini.cloud/) via GitHub Pages.

## Requirements

- Hugo Extended v0.147+ (a local `.deb` is included for convenience)

## Development

```sh
make          # start dev server with live reload
make build    # build to public/
make clean    # remove build artifacts
```

The dev server runs at `http://localhost:1313/`.

## Project structure

```
config/_default/   # split Hugo config (hugo.toml + menus.*.toml per language)
content/           # _index.{en,it,es,pt}.md — translatable front matter per language
data/              # flat YAML: experience, stack, projects, contact, education, facts
i18n/              # UI strings (en, it, es, pt)
layouts/partials/  # hero, about, stack, experience, project, contact, footer, etc.
assets/scss/       # main.scss — dark-first CSS
assets/js/         # main.js — theme/accent/font switching, scroll reveal, nav spy
static/            # images and other static assets
```

## Content

- **Translatable text** (hero copy, about body, contact labels) lives in `content/_index.{lang}.md` front matter.
- **Structured data** (experience, stack, projects) lives in `data/*.yaml` — these use proper nouns and dates so they are not language-keyed.

## i18n

The site supports four languages: English (primary), Italian, Spanish, and Portuguese. Language stubs are in `content/` and string translations in `i18n/`.

## Deploy

### Option A — `/docs` folder on `main` (recommended)

Build the site into `docs/` and push to `main`. GitHub Pages serves directly from that folder.

**One-time GitHub setup:**

1. Go to repo → **Settings → Pages**
2. Set **Branch:** `main`, **Folder:** `/docs`
3. Save.

**Publishing new content:**

```sh
hugo --config config.toml --destination docs --minify
touch docs/.nojekyll
git add docs/
git commit -m "Publish site"
git push origin main
```

Or with the Makefile shortcut:

```sh
make publish
```

> Never manually edit files inside `docs/` — it is fully regenerated on every build.
> The `CNAME` file is copied automatically from `static/CNAME`; make sure it lives there.

---

### Option B — `gh-pages` branch

```sh
./deploy.sh
```

Builds the site and pushes the output to the `gh-pages` branch, which GitHub Pages serves. The `CNAME` file and a `.nojekyll` marker are included automatically.

Environment variables:

| Variable | Default | Description |
|---|---|---|
| `PUBLISH_BRANCH` | `gh-pages` | Target branch for the built site |
| `HUGO_BIN` | `hugo` | Path to the Hugo binary |
