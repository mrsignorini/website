#!/usr/bin/env python3
"""MCP server for analyzing signorini.cloud Hugo site layout."""

import json
import re
import subprocess
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP

SITE_ROOT = Path(__file__).parent.parent
DEFAULT_BASE_URL = "http://localhost:1313"

mcp = FastMCP("signorini-layout")


def _fetch(url: str, base_url: str = DEFAULT_BASE_URL) -> tuple[str, BeautifulSoup]:
    full = urljoin(base_url, url) if not url.startswith("http") else url
    r = requests.get(full, timeout=10)
    r.raise_for_status()
    return r.text, BeautifulSoup(r.text, "html.parser")


def _heading_hierarchy(soup: BeautifulSoup) -> list[dict]:
    issues = []
    headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    prev_level = 0
    h1_count = 0
    for h in headings:
        level = int(h.name[1])
        if level == 1:
            h1_count += 1
        if prev_level > 0 and level > prev_level + 1:
            issues.append({
                "tag": h.name,
                "text": h.get_text(strip=True)[:60],
                "issue": f"skipped from h{prev_level} to h{level}",
            })
        prev_level = level
    if h1_count > 1:
        issues.append({"tag": "h1", "text": "", "issue": f"multiple h1 tags ({h1_count})"})
    if h1_count == 0:
        issues.append({"tag": "h1", "text": "", "issue": "no h1 found"})
    return issues


def _image_issues(soup: BeautifulSoup) -> list[dict]:
    issues = []
    for img in soup.find_all("img"):
        src = img.get("src", "")
        alt = img.get("alt")
        entry: dict[str, Any] = {"src": src}
        if alt is None:
            entry["issue"] = "missing alt attribute"
            issues.append(entry)
        elif alt.strip() == "" and not img.get("role") == "presentation":
            entry["issue"] = "empty alt (ok only if decorative)"
            issues.append(entry)
        if not img.get("width") or not img.get("height"):
            entry["issue"] = entry.get("issue", "") + "; missing width/height (CLS risk)"
            if entry not in issues:
                issues.append(entry)
    return issues


def _meta_tags(soup: BeautifulSoup) -> dict:
    result: dict[str, Any] = {"present": [], "missing": []}
    expected = {
        "description": lambda s: s.find("meta", attrs={"name": "description"}),
        "og:title": lambda s: s.find("meta", attrs={"property": "og:title"}),
        "og:description": lambda s: s.find("meta", attrs={"property": "og:description"}),
        "og:image": lambda s: s.find("meta", attrs={"property": "og:image"}),
        "twitter:card": lambda s: s.find("meta", attrs={"name": "twitter:card"}),
        "viewport": lambda s: s.find("meta", attrs={"name": "viewport"}),
        "charset": lambda s: s.find("meta", attrs={"charset": True}),
        "canonical": lambda s: s.find("link", attrs={"rel": "canonical"}),
    }
    for name, finder in expected.items():
        tag = finder(soup)
        if tag:
            result["present"].append(name)
        else:
            result["missing"].append(name)
    return result


def _link_issues(soup: BeautifulSoup) -> list[dict]:
    issues = []
    for a in soup.find_all("a"):
        text = a.get_text(strip=True)
        href = a.get("href", "")
        if not text and not a.find("img"):
            issues.append({"href": href, "issue": "empty link text (no text, no img)"})
        if text.lower() in {"click here", "here", "read more", "learn more"}:
            issues.append({"href": href, "text": text, "issue": "non-descriptive link text"})
    return issues


def _button_issues(soup: BeautifulSoup) -> list[dict]:
    issues = []
    for btn in soup.find_all("button"):
        text = btn.get_text(strip=True)
        aria = btn.get("aria-label", "")
        if not text and not aria:
            issues.append({"issue": "button has no text and no aria-label"})
    return issues


def _contrast_hints(soup: BeautifulSoup) -> list[str]:
    hints = []
    style_tags = soup.find_all("style")
    inline_styles = [tag.get("style", "") for tag in soup.find_all(style=True)]
    all_css = " ".join(s.get_text() for s in style_tags) + " ".join(inline_styles)
    if re.search(r"color\s*:\s*#[89abcdef]{3,6}", all_css, re.I):
        hints.append("light grey text detected — verify contrast ratio ≥4.5:1")
    if "opacity" in all_css:
        hints.append("opacity usage found — check effective contrast of faded text")
    return hints


def _responsive_hints(soup: BeautifulSoup) -> list[str]:
    hints = []
    vp = soup.find("meta", attrs={"name": "viewport"})
    if not vp:
        hints.append("missing viewport meta tag — site won't scale on mobile")
    else:
        content = vp.get("content", "")
        if "user-scalable=no" in content or "maximum-scale=1" in content:
            hints.append("viewport disables user zoom — accessibility issue")
    tables = soup.find_all("table")
    if tables:
        hints.append(f"{len(tables)} table(s) found — verify horizontal scroll on mobile")
    fixed_px = re.findall(r"width\s*:\s*(\d{3,4})px", str(soup))
    if fixed_px:
        big = [p for p in fixed_px if int(p) > 600]
        if big:
            hints.append(f"large fixed widths ({', '.join(big[:5])}px) — may overflow on mobile")
    return hints


@mcp.tool()
def analyze_page(path: str = "/", base_url: str = DEFAULT_BASE_URL) -> dict:
    """Full layout analysis of a page: headings, images, meta tags, links, responsiveness.

    Args:
        path: URL path to analyze (e.g. "/" or "/en/")
        base_url: Hugo server base URL (default: http://localhost:1313)
    """
    try:
        _, soup = _fetch(path, base_url)
    except Exception as e:
        return {"error": str(e), "hint": "Is `make start` running?"}

    return {
        "url": urljoin(base_url, path),
        "title": soup.title.string if soup.title else None,
        "heading_issues": _heading_hierarchy(soup),
        "image_issues": _image_issues(soup),
        "meta_tags": _meta_tags(soup),
        "link_issues": _link_issues(soup),
        "button_issues": _button_issues(soup),
        "responsive_hints": _responsive_hints(soup),
        "contrast_hints": _contrast_hints(soup),
    }


@mcp.tool()
def list_pages(base_url: str = DEFAULT_BASE_URL) -> list[str]:
    """Discover all internal page links from the homepage.

    Args:
        base_url: Hugo server base URL (default: http://localhost:1313)
    """
    try:
        _, soup = _fetch("/", base_url)
    except Exception as e:
        return [f"error: {e}"]

    seen = set()
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        parsed = urlparse(href)
        if parsed.netloc and parsed.netloc not in urlparse(base_url).netloc:
            continue
        path = parsed.path
        if path and path not in seen and not path.endswith((".css", ".js", ".png", ".jpg", ".svg", ".ico", ".xml")):
            seen.add(path)
            links.append(path)
    return sorted(links)


@mcp.tool()
def analyze_scss(relative_path: str = "assets/scss/main.scss") -> dict:
    """Analyze a SCSS file for layout-related patterns and potential issues.

    Args:
        relative_path: path relative to site root (default: assets/scss/main.scss)
    """
    target = SITE_ROOT / relative_path
    if not target.exists():
        return {"error": f"{relative_path} not found"}

    css_text = target.read_text()
    lines = css_text.splitlines()

    findings: dict[str, Any] = {
        "file": str(target),
        "lines": len(lines),
        "issues": [],
        "patterns": {},
    }

    media_queries = re.findall(r"@media[^{]+", css_text)
    findings["patterns"]["media_queries"] = len(media_queries)
    findings["patterns"]["breakpoints"] = list(set(re.findall(r"\d+px", " ".join(media_queries))))

    if re.search(r"!important", css_text):
        count = len(re.findall(r"!important", css_text))
        findings["issues"].append(f"!important used {count}x — may cause specificity battles")

    fixed_heights = re.findall(r"height\s*:\s*(\d+)px", css_text)
    big_fixed = [h for h in fixed_heights if int(h) > 200]
    if big_fixed:
        findings["issues"].append(f"large fixed heights ({', '.join(big_fixed[:5])}px) — may clip content")

    if not re.search(r"overflow\s*:\s*(auto|scroll)", css_text):
        findings["issues"].append("no overflow:auto/scroll — horizontal overflow may go unhandled")

    if not re.search(r"@media.*max-width|@media.*min-width", css_text):
        findings["issues"].append("no responsive media queries found")

    var_defs = re.findall(r"--[\w-]+\s*:", css_text)
    findings["patterns"]["css_custom_properties"] = len(var_defs)

    z_indexes = re.findall(r"z-index\s*:\s*(-?\d+)", css_text)
    if z_indexes:
        findings["patterns"]["z_index_values"] = sorted(set(int(z) for z in z_indexes))

    return findings


@mcp.tool()
def check_hugo_server(base_url: str = DEFAULT_BASE_URL) -> dict:
    """Check if the Hugo dev server is running and accessible.

    Args:
        base_url: Hugo server base URL (default: http://localhost:1313)
    """
    try:
        r = requests.get(base_url, timeout=5)
        return {
            "running": True,
            "status_code": r.status_code,
            "url": base_url,
            "content_length": len(r.text),
        }
    except requests.ConnectionError:
        return {
            "running": False,
            "url": base_url,
            "hint": "Run `make start` in the website directory to start Hugo server",
        }
    except Exception as e:
        return {"running": False, "error": str(e)}


@mcp.tool()
def suggest_layout_improvements(path: str = "/", base_url: str = DEFAULT_BASE_URL) -> dict:
    """Run full analysis and return prioritized improvement suggestions.

    Args:
        path: URL path to analyze
        base_url: Hugo server base URL (default: http://localhost:1313)
    """
    analysis = analyze_page(path, base_url)
    if "error" in analysis:
        return analysis

    suggestions = []

    for issue in analysis["heading_issues"]:
        suggestions.append({
            "priority": "high",
            "category": "accessibility",
            "issue": issue["issue"],
            "element": f"{issue['tag']}: {issue['text']}",
        })

    for issue in analysis["image_issues"]:
        priority = "high" if "alt" in issue.get("issue", "") else "medium"
        suggestions.append({
            "priority": priority,
            "category": "accessibility",
            "issue": issue.get("issue", "image issue"),
            "element": issue.get("src", ""),
        })

    for missing in analysis["meta_tags"]["missing"]:
        priority = "high" if missing in {"description", "viewport", "canonical"} else "medium"
        suggestions.append({
            "priority": priority,
            "category": "seo",
            "issue": f"missing <meta {missing}>",
            "element": "head",
        })

    for issue in analysis["link_issues"]:
        suggestions.append({
            "priority": "medium",
            "category": "accessibility",
            "issue": issue["issue"],
            "element": issue.get("href", ""),
        })

    for hint in analysis["responsive_hints"]:
        suggestions.append({
            "priority": "high",
            "category": "responsive",
            "issue": hint,
            "element": "layout",
        })

    for hint in analysis["contrast_hints"]:
        suggestions.append({
            "priority": "medium",
            "category": "contrast",
            "issue": hint,
            "element": "css",
        })

    suggestions.sort(key=lambda x: {"high": 0, "medium": 1, "low": 2}[x["priority"]])

    return {
        "url": analysis["url"],
        "title": analysis["title"],
        "total_issues": len(suggestions),
        "suggestions": suggestions,
    }


if __name__ == "__main__":
    mcp.run()
