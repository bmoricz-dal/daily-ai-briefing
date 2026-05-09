# Source Watchlist

Purpose: This file tells the daily briefing system which sources matter, why they matter, and how they should be treated. It prevents the briefing from becoming a random AI/news digest.

## Source priority rule

1. Official / primary sources
2. Academic sources
3. Professional insight sources
4. Reputable news sources
5. Specialist industry sources
6. Vendor/company blogs

Company blogs are useful but biased. Academic preprints are useful but not necessarily peer reviewed. News sources are timely but may lack depth. Vendor blogs should not be treated as neutral evidence.

---

## Core source categories

### 1. Frontier AI / AI company primary sources

Current:
- OpenAI News
- Google DeepMind Blog
- AWS Machine Learning Blog

Add / consider:
- Anthropic News
- Microsoft Azure AI Blog
- Google Cloud AI Blog

Use for:
- AI model releases
- AI agents
- AI engineering concepts
- enterprise AI deployment patterns
- responsible AI and safety updates

Caution:
These are company sources and should be treated as primary but not neutral.

---

### 2. Business intelligence / data workflow sources

Current:
- Microsoft Power BI Blog
- AWS Machine Learning Blog

Add / consider:
- Microsoft Fabric Blog
- Alteryx Blog
- Alteryx Community
- Snowflake Blog
- Databricks Blog
- dbt Blog

Use for:
- BI workflows
- dashboards
- semantic models
- dataflows
- automation
- SQL/data engineering concepts
- FMCG / sales & distribution-style workflow improvement

Caution:
Vendor blogs are useful for practical learning but should not be treated as independent market evidence.

---

### 3. Academic paper sources

Current:
- arXiv
- OpenAlex
- Crossref

Add / consider:
- Semantic Scholar
- CORE
- Google Scholar manually
- SSRN manually

Priority search themes:
- SME AI adoption
- generative AI adoption in SMEs
- AI adoption and dynamic capabilities
- absorptive capacity and AI
- digital transformation in SMEs
- responsible AI in SMEs
- AI and strategic decision-making
- AI business value measurement
- workflow embedding and organisational capability

Use for:
- daily academic paper brief
- Research literature building
- research gap refinement

Caution:
arXiv is not peer reviewed. OpenAlex and Crossref can return irrelevant results, so papers must be filtered for relevance.

---

### 4. Official / policy / economic sources

Add next:
- ONS
- GOV.UK / DSIT
- OECD
- Bank of England
- Companies House
- West Midlands Combined Authority
- European Commission / EU AI Office

Use for:
- UK business context
- AI adoption policy
- SME productivity
- labour market
- West Midlands relevance
- regulatory context

Caution:
Official data may be slower-moving than news, but it gives the briefing credibility.

---

### 5. FMCG / retail / sales / distribution sources

Add next:
- The Grocer
- Retail Gazette
- IGD
- Kantar
- NielsenIQ
- British Retail Consortium
- Supply Chain Dive
- Logistics Manager
- Food Manufacture

Use for:
- FMCG industry context
- retail and wholesale trends
- sales/distribution relevance
- supply chain pressures
- FMCG / sales & distribution practical implications

Caution:
Some sources may be paywalled or have weak RSS/API access.

---

### 6. Professional senior-analyst sources

Add / consider:
- McKinsey
- BCG
- Bain
- Deloitte AI Institute
- PwC AI
- MIT Sloan Management Review
- Harvard Business Review

Use for:
- senior analyst insight
- frameworks
- adoption patterns
- strategic implications

Caution:
Consulting and professional services content is useful but can be marketing-led. Do not treat it as neutral evidence.

---

## Relevance scoring

Each source item should be mentally scored:

5 = directly relevant to AI adoption, BI workflows, FMCG/distribution, SME capability, or research theme topic  
4 = strong AI/business relevance  
3 = useful background  
2 = weak relevance  
1 = ignore unless no better sources exist

---

## Current source issues to fix

- Microsoft AI Blog feed may be stale and return old items.
- OpenAlex queries may return irrelevant papers.
- OpenAlex may return future-dated or weakly matched records.
- arXiv is useful but too technical if used alone.
- The system still needs official, FMCG, and professional insight sources.
