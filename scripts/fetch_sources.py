import datetime as dt
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

TODAY = dt.datetime.utcnow().date().isoformat()
OUT_DIR = Path("data/source_packs")
OUT_DIR.mkdir(parents=True, exist_ok=True)

MAX_ITEMS_PER_SOURCE = 5

RSS_FEEDS = [
    {
        "name": "OpenAI News",
        "type": "company_primary_ai",
        "url": "https://openai.com/news/rss.xml",
    },
    {
        "name": "Google DeepMind Blog",
        "type": "company_primary_ai",
        "url": "https://deepmind.google/blog/rss.xml",
    },
    {
        "name": "Microsoft AI Blog",
        "type": "company_primary_ai",
        "url": "https://blogs.microsoft.com/ai/feed/",
    },
    {
        "name": "Microsoft Power BI Blog",
        "type": "bi_tooling",
        "url": "https://powerbi.microsoft.com/en-us/blog/feed/",
    },
    {
        "name": "AWS Machine Learning Blog",
        "type": "ai_data_tooling",
        "url": "https://aws.amazon.com/blogs/machine-learning/feed/",
    },
]

ACADEMIC_SOURCES = [
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
    {
        "name": "OpenAlex SME AI adoption",
        "type": "academic_metadata",
        "url": "https://api.openalex.org/works?search=SME%20AI%20adoption%20dynamic%20capabilities%20business%20value&per-page=5&sort=publication_date:desc",
    },
    {
        "name": "OpenAlex generative AI SMEs",
        "type": "academic_metadata",
        "url": "https://api.openalex.org/works?search=generative%20AI%20SMEs%20strategic%20decision%20making&per-page=5&sort=publication_date:desc",
    },
    {
        "name": "Crossref AI adoption SMEs",
        "type": "academic_metadata",
        "url": "https://api.crossref.org/works?query=AI%20adoption%20SMEs%20business%20value%20dynamic%20capabilities&rows=5",
    },
]


def fetch_url(url):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "daily-ai-briefing/0.2 personal research workflow"
        },
    )
    with urllib.request.urlopen(request, timeout=25) as response:
        return response.read()


def clean_text(text):
    if not text:
        return ""
    text = str(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def openalex_abstract_to_text(inverted_index):
    """
    OpenAlex stores some abstracts as an 'inverted index':
    {"word": [positions]}.
    This converts it back into readable text.
    """
    if not inverted_index or not isinstance(inverted_index, dict):
        return ""

    position_to_word = {}
    for word, positions in inverted_index.items():
        for pos in positions:
            position_to_word[pos] = word

    words = [position_to_word[i] for i in sorted(position_to_word)]
    return " ".join(words)


def parse_feed(raw, source_name, source_type):
    """
    Handles normal RSS feeds and Atom feeds.
    """
    root = ET.fromstring(raw)
    items = []

    # RSS format
    for item in root.findall(".//item")[:MAX_ITEMS_PER_SOURCE]:
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
                "summary": description[:1200],
            }
        )

    # Atom format fallback
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    for entry in root.findall("atom:entry", ns)[:MAX_ITEMS_PER_SOURCE]:
        title = clean_text(entry.findtext("atom:title", default="", namespaces=ns))
        published = entry.findtext("atom:published", default="", namespaces=ns)
        summary = clean_text(entry.findtext("atom:summary", default="", namespaces=ns))

        link = ""
        link_el = entry.find("atom:link", ns)
        if link_el is not None:
            link = link_el.attrib.get("href", "")

        items.append(
            {
                "source": source_name,
                "type": source_type,
                "title": title,
                "published": published,
                "url": link,
                "summary": summary[:1200],
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


def parse_openalex(raw, source_name):
    data = json.loads(raw.decode("utf-8"))
    items = []

    for work in data.get("results", [])[:MAX_ITEMS_PER_SOURCE]:
        authors = []
        for authorship in work.get("authorships", [])[:5]:
            author = authorship.get("author", {})
            if author.get("display_name"):
                authors.append(author["display_name"])

        abstract = openalex_abstract_to_text(work.get("abstract_inverted_index"))

        concepts = []
        for concept in work.get("concepts", [])[:5]:
            if concept.get("display_name"):
                concepts.append(concept["display_name"])

        items.append(
            {
                "source": source_name,
                "type": "academic_metadata",
                "title": clean_text(work.get("title", "")),
                "authors": authors,
                "year": work.get("publication_year", ""),
                "published": work.get("publication_date", ""),
                "url": work.get("id", ""),
                "doi": work.get("doi", ""),
                "summary": abstract[:1200],
                "concepts": concepts,
            }
        )

    return items


def parse_crossref(raw, source_name):
    data = json.loads(raw.decode("utf-8"))
    items = []

    for work in data.get("message", {}).get("items", [])[:MAX_ITEMS_PER_SOURCE]:
        title = clean_text(" ".join(work.get("title", [""])))

        authors = []
        for author in work.get("author", [])[:5]:
            given = author.get("given", "")
            family = author.get("family", "")
            full_name = f"{given} {family}".strip()
            if full_name:
                authors.append(full_name)

        year = ""
        date_parts = (
            work.get("published-print", {}).get("date-parts")
            or work.get("published-online", {}).get("date-parts")
            or work.get("created", {}).get("date-parts")
        )
        if date_parts and date_parts[0]:
            year = date_parts[0][0]

        items.append(
            {
                "source": source_name,
                "type": "academic_metadata",
                "title": title,
                "authors": authors,
                "year": year,
                "published": year,
                "url": work.get("URL", ""),
                "doi": work.get("DOI", ""),
                "container": clean_text(" ".join(work.get("container-title", [""]))),
                "summary": clean_text(work.get("abstract", ""))[:1200],
            }
        )

    return items


def collect_sources():
    results = []

    for feed in RSS_FEEDS:
        try:
            raw = fetch_url(feed["url"])
            results.extend(parse_feed(raw, feed["name"], feed["type"]))
        except Exception as e:
            results.append(
                {
                    "source": feed["name"],
                    "type": feed["type"],
                    "error": str(e),
                    "url": feed["url"],
                }
            )

    for source in ACADEMIC_SOURCES:
        try:
            raw = fetch_url(source["url"])

            if "arxiv.org" in source["url"]:
                results.extend(parse_arxiv(raw, source["name"]))
            elif "openalex.org" in source["url"]:
                results.extend(parse_openalex(raw, source["name"]))
            elif "crossref.org" in source["url"]:
                results.extend(parse_crossref(raw, source["name"]))
            else:
                results.append(
                    {
                        "source": source["name"],
                        "type": source["type"],
                        "error": "No parser available for this source.",
                        "url": source["url"],
                    }
                )

        except Exception as e:
            results.append(
                {
                    "source": source["name"],
                    "type": source["type"],
                    "error": str(e),
                    "url": source["url"],
                }
            )

    return results


def write_outputs(results):
    output = {
        "date": TODAY,
        "generated_utc": dt.datetime.utcnow().isoformat(),
        "purpose": "Daily source pack for AI, BI, Research and Reflection briefing.",
        "source_quality_rule": "Primary company sources and academic metadata are useful, but must be interpreted critically. Company blogs are not neutral. Preprints are not peer-reviewed.",
        "items": results,
    }

    json_path = OUT_DIR / f"source_pack_{TODAY}.json"
    md_path = OUT_DIR / f"source_pack_{TODAY}.md"

    json_path.write_text(
        json.dumps(output, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    lines = [
        f"# Daily Source Pack — {TODAY}",
        "",
        "Purpose: source pack for Daily AI, BI, Research & Reflection Briefing.",
        "",
        "Source quality rule: company blogs are useful primary signals but are not neutral; academic preprints are useful early signals but not necessarily peer-reviewed.",
        "",
        "## Items",
        "",
    ]

    for i, item in enumerate(results, start=1):
        lines.append(f"### {i}. {item.get('title', 'Untitled')}")
        lines.append(f"- Source: {item.get('source', '')}")
        lines.append(f"- Type: {item.get('type', '')}")
        lines.append(f"- Published: {item.get('published', item.get('year', ''))}")
        lines.append(f"- URL: {item.get('url', '')}")

        if item.get("doi"):
            lines.append(f"- DOI: {item.get('doi')}")

        if item.get("authors"):
            lines.append(f"- Authors: {', '.join(item.get('authors', []))}")

        if item.get("container"):
            lines.append(f"- Journal/source: {item.get('container')}")

        if item.get("concepts"):
            lines.append(f"- Concepts: {', '.join(item.get('concepts', []))}")

        if item.get("summary"):
            lines.append(f"- Summary: {item.get('summary', '')}")

        if item.get("error"):
            lines.append(f"- Error: {item.get('error', '')}")

        lines.append("")

    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(f"Collected {len(results)} items")


def main():
    results = collect_sources()
    write_outputs(results)


if __name__ == "__main__":
    main()
