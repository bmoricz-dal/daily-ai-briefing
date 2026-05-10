import datetime as dt
import email.utils
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


# ============================================================
# Daily AI Briefing Source Collector
# ============================================================
# Purpose:
# Pull a balanced daily source pack for the Daily AI, BI & Research Briefing.
#
# Source layers:
# 1. AI / BI primary company sources
# 2. Official UK policy / government sources
# 3. FMCG / retail / logistics / supply-chain sources
# 4. Professional analyst / management insight sources
# 5. Reputable independent news sources
# 6. Academic paper discovery sources
# 7. Manual watchlist entries for sources that are important but not easy to scrape
#
# Uses only Python standard library.
# No paid APIs.
# No API keys.
# ============================================================


TODAY = dt.datetime.utcnow().date().isoformat()
NOW_UTC = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc)

OUT_DIR = Path("data/source_packs")
OUT_DIR.mkdir(parents=True, exist_ok=True)

MAX_ITEMS_PER_SOURCE = 5
MAX_RSS_AGE_DAYS = 60
MAX_ACADEMIC_AGE_DAYS = 900


# ============================================================
# RSS / Atom feeds
# ============================================================

RSS_FEEDS = [
    # --------------------------------------------------------
    # Frontier AI / primary company sources
    # --------------------------------------------------------
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
        "name": "Microsoft Power BI Blog",
        "type": "bi_tooling",
        "url": "https://powerbi.microsoft.com/en-us/blog/feed/",
    },
    {
        "name": "AWS Machine Learning Blog",
        "type": "ai_data_tooling",
        "url": "https://aws.amazon.com/blogs/machine-learning/feed/",
    },

    # --------------------------------------------------------
    # Independent / reputable news
    # --------------------------------------------------------
    {
        "name": "BBC Business",
        "type": "independent_news",
        "url": "http://feeds.bbci.co.uk/news/business/rss.xml",
    },
    {
        "name": "The Guardian Business",
        "type": "independent_news",
        "url": "https://www.theguardian.com/uk/business/rss",
    },

    # --------------------------------------------------------
    # FMCG / retail / logistics / supply chain
    # --------------------------------------------------------
    {
        "name": "Supply Chain Dive",
        "type": "fmcg_supply_chain_news",
        "url": "https://www.supplychaindive.com/feeds/news/",
    },
    {
        "name": "Retail Gazette",
        "type": "retail_fmcg_news",
        "url": "https://www.retailgazette.co.uk/blog/feed/",
    },
    {
        "name": "Logistics Manager",
        "type": "logistics_distribution_news",
        "url": "https://www.logisticsmanager.com/feed/",
    },

    # --------------------------------------------------------
    # Professional analyst / management insight
    # --------------------------------------------------------
    {
        "name": "MIT Sloan Management Review",
        "type": "professional_insight",
        "url": "https://sloanreview.mit.edu/feed/",
    },
    {
        "name": "McKinsey Insights",
        "type": "professional_insight",
        "url": "https://www.mckinsey.com/insights/rss",
    },
]


# ============================================================
# GOV.UK official search API
# ============================================================

GOVUK_SEARCHES = [
    {
        "name": "GOV.UK AI business adoption",
        "type": "official_policy",
        "url": "https://www.gov.uk/api/search.json?q=artificial%20intelligence%20business%20adoption&count=5&order=updated-newest",
    },
    {
        "name": "GOV.UK DSIT AI",
        "type": "official_policy",
        "url": "https://www.gov.uk/api/search.json?q=DSIT%20artificial%20intelligence%20business&count=5&order=updated-newest",
    },
    {
        "name": "GOV.UK SMEs digital adoption",
        "type": "official_policy",
        "url": "https://www.gov.uk/api/search.json?q=SME%20digital%20adoption%20artificial%20intelligence&count=5&order=updated-newest",
    },
    {
        "name": "GOV.UK business productivity technology",
        "type": "official_policy",
        "url": "https://www.gov.uk/api/search.json?q=business%20productivity%20technology%20SME&count=5&order=updated-newest",
    },
]


# ============================================================
# Google News RSS searches
# ============================================================
# These are useful for current signals, but they are not primary sources.
# The briefing should treat them as news-discovery feeds.

NEWS_SEARCH_RSS = [
    {
        "name": "Google News - UK SME AI adoption",
        "type": "news_search",
        "url": "https://news.google.com/rss/search?q=UK%20SME%20AI%20adoption&hl=en-GB&gl=GB&ceid=GB:en",
    },
    {
        "name": "Google News - West Midlands AI business",
        "type": "news_search",
        "url": "https://news.google.com/rss/search?q=West%20Midlands%20AI%20business%20SME&hl=en-GB&gl=GB&ceid=GB:en",
    },
    {
        "name": "Google News - FMCG AI supply chain UK",
        "type": "news_search",
        "url": "https://news.google.com/rss/search?q=UK%20FMCG%20AI%20supply%20chain&hl=en-GB&gl=GB&ceid=GB:en",
    },
    {
        "name": "Google News - retail distribution AI UK",
        "type": "news_search",
        "url": "https://news.google.com/rss/search?q=UK%20retail%20distribution%20AI%20data&hl=en-GB&gl=GB&ceid=GB:en",
    },
    {
        "name": "Google News - business intelligence AI workflow",
        "type": "news_search",
        "url": "https://news.google.com/rss/search?q=business%20intelligence%20AI%20workflow%20automation&hl=en-GB&gl=GB&ceid=GB:en",
    },
]


# ============================================================
# Academic sources
# ============================================================

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
        "name": "arXiv AI workflow automation",
        "type": "academic_preprint",
        "url": "http://export.arxiv.org/api/query?search_query=all:%22AI%22%20AND%20all:%22workflow%20automation%22&start=0&max_results=5&sortBy=submittedDate&sortOrder=descending",
    },
    {
        "name": "OpenAlex SME AI adoption",
        "type": "academic_metadata",
        "url": "https://api.openalex.org/works?search=SME%20AI%20adoption%20dynamic%20capabilities%20business%20value&per-page=8&sort=publication_date:desc",
    },
    {
        "name": "OpenAlex generative AI SMEs",
        "type": "academic_metadata",
        "url": "https://api.openalex.org/works?search=generative%20AI%20SMEs%20strategic%20decision%20making&per-page=8&sort=publication_date:desc",
    },
    {
        "name": "OpenAlex AI business value",
        "type": "academic_metadata",
        "url": "https://api.openalex.org/works?search=artificial%20intelligence%20business%20value%20digital%20transformation%20SME&per-page=8&sort=publication_date:desc",
    },
    {
        "name": "Crossref AI adoption SMEs",
        "type": "academic_metadata",
        "url": "https://api.crossref.org/works?query=AI%20adoption%20SMEs%20business%20value%20dynamic%20capabilities&rows=8",
    },
    {
        "name": "Crossref AI business value",
        "type": "academic_metadata",
        "url": "https://api.crossref.org/works?query=artificial%20intelligence%20business%20value%20digital%20transformation%20SMEs&rows=8",
    },
]


# ============================================================
# Manual watchlist entries
# ============================================================
# These sources are important but may not have reliable free RSS/API access.
# Including them in the source pack reminds the briefing system to search/check them manually if needed.

MANUAL_WATCHLIST = [
    {
        "source": "ONS",
        "type": "official_watchlist",
        "title": "ONS business, economy and technology statistics",
        "url": "https://www.ons.gov.uk/",
        "summary": "Official UK statistics source. Use for business conditions, labour market, productivity, technology adoption, inflation, retail and economy context. Search manually when the briefing needs official evidence.",
    },
    {
        "source": "OECD AI and SMEs",
        "type": "official_watchlist",
        "title": "OECD AI, SMEs, productivity and digital adoption",
        "url": "https://www.oecd.org/",
        "summary": "High-quality international source for AI diffusion, SME productivity, digital adoption, policy and business transformation context. Use as official/professional evidence, not daily news.",
    },
    {
        "source": "Bank of England",
        "type": "official_watchlist",
        "title": "Bank of England business and economy context",
        "url": "https://www.bankofengland.co.uk/",
        "summary": "Use for UK macroeconomic context, inflation, interest rates, business conditions and financial stability signals.",
    },
    {
        "source": "West Midlands Combined Authority",
        "type": "regional_watchlist",
        "title": "West Midlands regional growth, innovation and business support",
        "url": "https://www.wmca.org.uk/",
        "summary": "Regional source for West Midlands productivity, innovation, clusters, business support and AI adoption context.",
    },
    {
        "source": "Business.gov.uk West Midlands",
        "type": "regional_watchlist",
        "title": "Business.gov.uk West Midlands investment and regional sector context",
        "url": "https://www.business.gov.uk/",
        "summary": "Use for regional sector strengths, investment context and UK government-backed regional business evidence.",
    },
    {
        "source": "The Grocer",
        "type": "fmcg_watchlist",
        "title": "The Grocer - UK FMCG and grocery sector",
        "url": "https://www.thegrocer.co.uk/",
        "summary": "Specialist UK FMCG/grocery source. Useful for suppliers, wholesalers, brands, pricing, inflation, retail pressure and distribution signals.",
    },
    {
        "source": "IGD",
        "type": "fmcg_watchlist",
        "title": "IGD - grocery, retail and supply-chain insight",
        "url": "https://www.igd.com/",
        "summary": "Specialist grocery and retail insight source. Useful for food, grocery, retail, wholesale and supply-chain context.",
    },
    {
        "source": "Kantar",
        "type": "fmcg_watchlist",
        "title": "Kantar retail and FMCG insights",
        "url": "https://www.kantar.com/uki/industries/retail",
        "summary": "Professional market insight source for FMCG, retail, consumers and brand performance. Use carefully as professional insight.",
    },
    {
        "source": "NielsenIQ",
        "type": "fmcg_watchlist",
        "title": "NielsenIQ retail and FMCG insights",
        "url": "https://nielseniq.com/global/en/insights/",
        "summary": "Professional retail/FMCG data and insight source. Useful for market trends, consumer behaviour and category performance.",
    },
    {
        "source": "British Retail Consortium",
        "type": "retail_watchlist",
        "title": "British Retail Consortium",
        "url": "https://brc.org.uk/",
        "summary": "Use for UK retail conditions, policy, costs, consumer demand and retail industry pressure.",
    },
    {
        "source": "BCG Henderson Institute",
        "type": "professional_watchlist",
        "title": "BCG Henderson Institute",
        "url": "https://bcghendersoninstitute.com/",
        "summary": "Professional strategy insight source. Use for business model, AI, organisational capability and strategic management framing.",
    },
    {
        "source": "Deloitte AI Institute",
        "type": "professional_watchlist",
        "title": "Deloitte AI Institute",
        "url": "https://www2.deloitte.com/us/en/pages/deloitte-analytics/solutions/deloitte-ai-institute.html",
        "summary": "Professional services source for AI adoption, governance, risk, enterprise transformation and value realisation.",
    },
    {
        "source": "PwC AI insights",
        "type": "professional_watchlist",
        "title": "PwC AI and emerging technology insights",
        "url": "https://www.pwc.com/gx/en/issues/artificial-intelligence.html",
        "summary": "Professional services source for AI adoption, workforce, risk, productivity and enterprise transformation trends.",
    },
]


# ============================================================
# Utility functions
# ============================================================

def fetch_url(url):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "daily-ai-briefing/0.3 personal research workflow"
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def clean_text(text):
    if not text:
        return ""
    text = str(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&quot;", '"', text)
    text = re.sub(r"&#39;", "'", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_date_to_utc(date_text):
    """
    Tries to parse common RSS/Atom/API date formats into timezone-aware UTC datetime.
    Returns None if parsing fails.
    """
    if not date_text:
        return None

    date_text = str(date_text).strip()

    # RSS style, e.g. Fri, 08 May 2026 12:30:00 GMT
    try:
        parsed = email.utils.parsedate_to_datetime(date_text)
        if parsed:
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=dt.timezone.utc)
            return parsed.astimezone(dt.timezone.utc)
    except Exception:
        pass

    # ISO style, e.g. 2026-05-04T18:47:29Z or 2026-05-04
    try:
        iso_text = date_text.replace("Z", "+00:00")
        parsed = dt.datetime.fromisoformat(iso_text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.timezone.utc)
        return parsed.astimezone(dt.timezone.utc)
    except Exception:
        pass

    # Year-only values are not useful for recency filtering
    return None


def is_future_date(date_text):
    parsed = parse_date_to_utc(date_text)
    if not parsed:
        return False
    return parsed > NOW_UTC + dt.timedelta(days=1)


def is_too_old(date_text, max_age_days):
    parsed = parse_date_to_utc(date_text)
    if not parsed:
        return False
    return parsed < NOW_UTC - dt.timedelta(days=max_age_days)


def should_keep_item(item, max_age_days):
    """
    Filters out future-dated items and very stale items where a usable date exists.
    If no usable date exists, keep the item because many official/professional sources
    have inconsistent metadata.
    """
    published = item.get("published") or item.get("year") or ""

    if is_future_date(published):
        return False

    if is_too_old(published, max_age_days):
        return False

    return True


def openalex_abstract_to_text(inverted_index):
    """
    OpenAlex stores some abstracts as an inverted index:
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


def relevance_score(item):
    """
    Rough rule-based relevance score.
    This does not decide the final briefing; it helps ChatGPT see which items
    are probably worth attention.
    """
    text = " ".join(
        [
            str(item.get("title", "")),
            str(item.get("summary", "")),
            str(item.get("source", "")),
            str(item.get("type", "")),
        ]
    ).lower()

    high_value_terms = [
        "ai adoption",
        "artificial intelligence",
        "generative ai",
        "business value",
        "sme",
        "small business",
        "medium-sized",
        "workflow",
        "automation",
        "business intelligence",
        "power bi",
        "fabric",
        "data quality",
        "supply chain",
        "logistics",
        "retail",
        "fmcg",
        "grocery",
        "distribution",
        "productivity",
        "west midlands",
        "digital adoption",
        "dynamic capabilities",
        "absorptive capacity",
        "decision-making",
        "responsible ai",
    ]

    medium_value_terms = [
        "agent",
        "agents",
        "analytics",
        "dashboard",
        "data",
        "customer",
        "sales",
        "operations",
        "governance",
        "risk",
        "strategy",
        "transformation",
        "innovation",
    ]

    score = 1

    for term in high_value_terms:
        if term in text:
            score += 2

    for term in medium_value_terms:
        if term in text:
            score += 1

    return min(score, 5)


def add_quality_notes(item):
    source_type = item.get("type", "")

    if source_type.startswith("company") or source_type in {"bi_tooling", "ai_data_tooling"}:
        item["quality_note"] = "Company/vendor source: useful primary signal, but not neutral evidence."
    elif source_type in {"official_policy", "official_watchlist", "regional_watchlist"}:
        item["quality_note"] = "Official/regional source: high credibility, but may be slower-moving than daily news."
    elif source_type in {"academic_preprint"}:
        item["quality_note"] = "Academic preprint: useful early signal, but not peer-reviewed."
    elif source_type in {"academic_metadata"}:
        item["quality_note"] = "Academic metadata: verify relevance and publication details before relying on it."
    elif source_type in {"independent_news", "news_search"}:
        item["quality_note"] = "News source/search result: useful for current signals, but verify details."
    elif "professional" in source_type:
        item["quality_note"] = "Professional insight source: useful for framing, but may reflect consulting/vendor positioning."
    elif "fmcg" in source_type or "retail" in source_type or "logistics" in source_type:
        item["quality_note"] = "Industry specialist source: useful for sector context, but verify with official or independent sources where possible."
    else:
        item["quality_note"] = "Use with normal source-checking caution."

    item["relevance_score"] = relevance_score(item)
    return item


# ============================================================
# Parsers
# ============================================================

def parse_feed(raw, source_name, source_type):
    """
    Handles normal RSS feeds and Atom feeds.
    """
    root = ET.fromstring(raw)
    items = []

    # RSS format
    for item in root.findall(".//item")[:MAX_ITEMS_PER_SOURCE * 2]:
        title = clean_text(item.findtext("title", default=""))
        link = item.findtext("link", default="")
        pub_date = item.findtext("pubDate", default="")
        description = clean_text(item.findtext("description", default=""))

        parsed_item = {
            "source": source_name,
            "type": source_type,
            "title": title,
            "published": pub_date,
            "url": link,
            "summary": description[:1200],
        }

        if should_keep_item(parsed_item, MAX_RSS_AGE_DAYS):
            items.append(add_quality_notes(parsed_item))

        if len(items) >= MAX_ITEMS_PER_SOURCE:
            break

    # Atom format fallback
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    for entry in root.findall("atom:entry", ns)[:MAX_ITEMS_PER_SOURCE * 2]:
        title = clean_text(entry.findtext("atom:title", default="", namespaces=ns))
        published = entry.findtext("atom:published", default="", namespaces=ns)
        summary = clean_text(entry.findtext("atom:summary", default="", namespaces=ns))

        link = ""
        link_el = entry.find("atom:link", ns)
        if link_el is not None:
            link = link_el.attrib.get("href", "")

        parsed_item = {
            "source": source_name,
            "type": source_type,
            "title": title,
            "published": published,
            "url": link,
            "summary": summary[:1200],
        }

        if should_keep_item(parsed_item, MAX_RSS_AGE_DAYS):
            items.append(add_quality_notes(parsed_item))

        if len(items) >= MAX_ITEMS_PER_SOURCE:
            break

    return items


def parse_govuk_search(raw, source_name, source_type):
    data = json.loads(raw.decode("utf-8"))
    items = []

    for result in data.get("results", [])[:MAX_ITEMS_PER_SOURCE * 2]:
        link = result.get("link", "")
        if link and link.startswith("/"):
            link = "https://www.gov.uk" + link

        published = (
            result.get("public_timestamp")
            or result.get("updated_at")
            or result.get("display_date")
            or ""
        )

        parsed_item = {
            "source": source_name,
            "type": source_type,
            "title": clean_text(result.get("title", "")),
            "published": published,
            "url": link,
            "summary": clean_text(result.get("description", ""))[:1200],
        }

        # GOV.UK search can surface old but still important policy pages.
        # Use a wider window than normal RSS.
        if should_keep_item(parsed_item, 365):
            items.append(add_quality_notes(parsed_item))

        if len(items) >= MAX_ITEMS_PER_SOURCE:
            break

    return items


def parse_arxiv(raw, source_name):
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(raw)
    items = []

    for entry in root.findall("atom:entry", ns)[:MAX_ITEMS_PER_SOURCE * 2]:
        title = clean_text(entry.findtext("atom:title", default="", namespaces=ns))
        summary = clean_text(entry.findtext("atom:summary", default="", namespaces=ns))
        published = entry.findtext("atom:published", default="", namespaces=ns)
        link = entry.findtext("atom:id", default="", namespaces=ns)

        authors = []
        for author in entry.findall("atom:author", ns):
            name = author.findtext("atom:name", default="", namespaces=ns)
            if name:
                authors.append(name)

        parsed_item = {
            "source": source_name,
            "type": "academic_preprint",
            "title": title,
            "authors": authors,
            "published": published,
            "url": link,
            "summary": summary[:1200],
        }

        if should_keep_item(parsed_item, MAX_ACADEMIC_AGE_DAYS):
            items.append(add_quality_notes(parsed_item))

        if len(items) >= MAX_ITEMS_PER_SOURCE:
            break

    return items


def parse_openalex(raw, source_name):
    data = json.loads(raw.decode("utf-8"))
    items = []

    for work in data.get("results", [])[:MAX_ITEMS_PER_SOURCE * 2]:
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

        published = work.get("publication_date", "")
        year = work.get("publication_year", "")

        parsed_item = {
            "source": source_name,
            "type": "academic_metadata",
            "title": clean_text(work.get("title", "")),
            "authors": authors,
            "year": year,
            "published": published,
            "url": work.get("id", ""),
            "doi": work.get("doi", ""),
            "summary": abstract[:1200],
            "concepts": concepts,
        }

        # Filter future-dated OpenAlex records and very old records.
        if should_keep_item(parsed_item, MAX_ACADEMIC_AGE_DAYS):
            items.append(add_quality_notes(parsed_item))

        if len(items) >= MAX_ITEMS_PER_SOURCE:
            break

    return items


def parse_crossref(raw, source_name):
    data = json.loads(raw.decode("utf-8"))
    items = []

    for work in data.get("message", {}).get("items", [])[:MAX_ITEMS_PER_SOURCE * 2]:
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
            year = str(date_parts[0][0])

        parsed_item = {
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

        # Crossref often only gives year, so date filtering is weaker here.
        if parsed_item["title"] and not is_future_date(parsed_item["published"]):
            items.append(add_quality_notes(parsed_item))

        if len(items) >= MAX_ITEMS_PER_SOURCE:
            break

    return items


# ============================================================
# Collection logic
# ============================================================

def collect_sources():
    results = []

    # RSS / Atom feeds
    for feed in RSS_FEEDS:
        try:
            raw = fetch_url(feed["url"])
            parsed = parse_feed(raw, feed["name"], feed["type"])
            results.extend(parsed)
        except Exception as e:
            results.append(
                add_quality_notes(
                    {
                        "source": feed["name"],
                        "type": feed["type"],
                        "error": str(e),
                        "url": feed["url"],
                    }
                )
            )

    # GOV.UK official searches
    for search in GOVUK_SEARCHES:
        try:
            raw = fetch_url(search["url"])
            parsed = parse_govuk_search(raw, search["name"], search["type"])
            results.extend(parsed)
        except Exception as e:
            results.append(
                add_quality_notes(
                    {
                        "source": search["name"],
                        "type": search["type"],
                        "error": str(e),
                        "url": search["url"],
                    }
                )
            )

    # Google News RSS searches
    for search in NEWS_SEARCH_RSS:
        try:
            raw = fetch_url(search["url"])
            parsed = parse_feed(raw, search["name"], search["type"])
            results.extend(parsed)
        except Exception as e:
            results.append(
                add_quality_notes(
                    {
                        "source": search["name"],
                        "type": search["type"],
                        "error": str(e),
                        "url": search["url"],
                    }
                )
            )

    # Academic sources
    for source in ACADEMIC_SOURCES:
        try:
            raw = fetch_url(source["url"])

            if "arxiv.org" in source["url"]:
                parsed = parse_arxiv(raw, source["name"])
            elif "openalex.org" in source["url"]:
                parsed = parse_openalex(raw, source["name"])
            elif "crossref.org" in source["url"]:
                parsed = parse_crossref(raw, source["name"])
            else:
                parsed = [
                    {
                        "source": source["name"],
                        "type": source["type"],
                        "error": "No parser available for this source.",
                        "url": source["url"],
                    }
                ]

            results.extend(parsed)

        except Exception as e:
            results.append(
                add_quality_notes(
                    {
                        "source": source["name"],
                        "type": source["type"],
                        "error": str(e),
                        "url": source["url"],
                    }
                )
            )

    # Manual watchlist sources
    for entry in MANUAL_WATCHLIST:
        results.append(add_quality_notes(entry))

    # Sort roughly by source usefulness and relevance.
    # High relevance first; manual watchlist stays included but may not dominate.
    results.sort(
        key=lambda item: (
            item.get("relevance_score", 0),
            0 if "watchlist" not in item.get("type", "") else -1,
        ),
        reverse=True,
    )

    return results


# ============================================================
# Output writers
# ============================================================

def write_outputs(results):
    output = {
        "date": TODAY,
        "generated_utc": dt.datetime.utcnow().isoformat(),
        "purpose": "Daily source pack for AI, BI, Research & Reflection briefing.",
        "source_quality_rule": (
            "Prioritise official/primary sources, academic sources, professional insight, "
            "reputable news, and specialist industry sources. Company/vendor blogs are useful "
            "primary signals but are not neutral. Preprints are not peer-reviewed. News-search "
            "results require verification. Manual watchlist entries are reminders to check important "
            "sources when the daily feed is thin."
        ),
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
        "## Source quality rule",
        "",
        "- Official / primary sources are strongest for facts and policy context.",
        "- Academic sources are useful for research themes, but preprints are not settled evidence.",
        "- Professional insight sources are useful for framing, but may be consulting/vendor-led.",
        "- Reputable news sources are useful for current signals, but should be verified.",
        "- Specialist FMCG, retail and logistics sources add sector context.",
        "- Company blogs are useful primary signals but are not neutral.",
        "- Manual watchlist entries are included to remind the briefing system what to check when feeds are thin.",
        "",
        "## Items",
        "",
    ]

    for i, item in enumerate(results, start=1):
        lines.append(f"### {i}. {item.get('title', 'Untitled')}")
        lines.append(f"- Source: {item.get('source', '')}")
        lines.append(f"- Type: {item.get('type', '')}")
        lines.append(f"- Relevance score: {item.get('relevance_score', '')}/5")
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

        if item.get("quality_note"):
            lines.append(f"- Quality note: {item.get('quality_note', '')}")

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
