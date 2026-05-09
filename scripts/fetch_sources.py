import datetime as dt
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

TODAY = dt.datetime.utcnow().date().isoformat()
OUT_DIR = Path("data/source_packs")
OUT_DIR.mkdir(parents=True, exist_ok=True)

RSS_FEEDS = [
    {
        "name": "OpenAI News",
        "type": "company_primary",
        "url": "https://openai.com/news/rss.xml",
    },
    {
        "name": "Google DeepMind Blog",
        "type": "company_primary",
        "url": "https://deepmind.google/blog/rss.xml",
    },
]

ARXIV_SOURCES = [
    {
        "name": "arXiv AI adoption",
        "type": "academic_preprint",
        "url": "http://export.arxiv.org/api/query?search_query=all:%22AI%20adoption%22&start=0&max_results=5&sortBy=submittedDate&sortOrder=descending",
    },
    {
        "name": "arXiv generative AI business value",
        "type": "academic_preprint",
        "url": "http://export.arxiv.org/api/query?search_query=all:%22generative%20AI%22%20AND%20all:%22business%20value%22&start=0&max_results=5&sortBy=submittedDate&sortOrder=descending",
    },
]


def fetch_url(url):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "daily-ai-briefing/0.1 personal research workflow"
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read()


def clean_text(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_rss(raw, source_name, source_type):
    root = ET.fromstring(raw)
    items = []

    for item in root.findall(".//item")[:5]:
        title = clean_text(item.findtext("title", default=""))
        link = item.findtext("link", default="")
        pub_date = item.findtext("pubDate", default="")
        description = clean_text(item.findtext("description", default=""))

        items.append(
            {
                "source": source_name,
                "type": source_type,
                "title": title,
                "published": pub_date,
                "url": link,
                "summary": description[:1000],
            }
        )

    return items


def parse_arxiv(raw, source_name):
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(raw)
    items = []

    for entry in root.findall("atom:entry", ns):
        title = clean_text(entry.findtext("atom:title", default="", namespaces=ns))
        summary = clean_text(entry.findtext("atom:summary", default="", namespaces=ns))
        published = entry.findtext("atom:published", default="", namespaces=ns)
        link = entry.findtext("atom:id", default="", namespaces=ns)

        authors = []
        for author in entry.findall("atom:author", ns):
            name = author.findtext("atom:name", default="", namespaces=ns)
            if name:
                authors.append(name)

        items.append(
            {
                "source": source_name,
                "type": "academic_preprint",
                "title": title,
                "authors": authors,
                "published": published,
                "url": link,
                "summary": summary[:1200],
            }
        )

    return items


def main():
    results = []

    for feed in RSS_FEEDS:
        try:
            raw = fetch_url(feed["url"])
            results.extend(parse_rss(raw, feed["name"], feed["type"]))
        except Exception as e:
            results.append(
                {
                    "source": feed["name"],
                    "type": feed["type"],
                    "error": str(e),
                    "url": feed["url"],
                }
            )

    for source in ARXIV_SOURCES:
        try:
            raw = fetch_url(source["url"])
            results.extend(parse_arxiv(raw, source["name"]))
        except Exception as e:
            results.append(
                {
                    "source": source["name"],
                    "type": source["type"],
                    "error": str(e),
                    "url": source["url"],
                }
            )

    output = {
        "date": TODAY,
        "generated_utc": dt.datetime.utcnow().isoformat(),
        "purpose": "Daily source pack for AI, BI, PhD and faith briefing.",
        "items": results,
    }

    json_path = OUT_DIR / f"source_pack_{TODAY}.json"
    md_path = OUT_DIR / f"source_pack_{TODAY}.md"

    json_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        f"# Daily Source Pack — {TODAY}",
        "",
        "Purpose: source pack for Daily AI, BI, PhD & Faith Briefing.",
        "",
        "## Items",
        "",
    ]

    for i, item in enumerate(results, start=1):
        lines.append(f"### {i}. {item.get('title', 'Untitled')}")
        lines.append(f"- Source: {item.get('source', '')}")
        lines.append(f"- Type: {item.get('type', '')}")
        lines.append(f"- Published: {item.get('published', '')}")
        lines.append(f"- URL: {item.get('url', '')}")

        if item.get("authors"):
            lines.append(f"- Authors: {', '.join(item.get('authors', []))}")

        if item.get("summary"):
            lines.append(f"- Summary: {item.get('summary', '')}")

        if item.get("error"):
            lines.append(f"- Error: {item.get('error', '')}")

        lines.append("")

    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
