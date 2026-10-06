# SAP Icon Extractor Agent

AI agent that discovers, downloads, deduplicates, and catalogs SAP icons from Google Images, maintaining a continuously growing library of unique icons.

## Business Challenge

Teams working with SAP applications spend significant time manually searching for SAP icons across the web. There is no automated way to discover, collect, and maintain an up-to-date, deduplicated library of SAP icons sourced from various online locations. The agent addresses this by autonomously searching Google Images (filtered to clipart/large images) for SAP icons, downloading them, deduplicating them by hash or URL, and appending new unique icons to a persistent catalog — accessible via a conversational chat interface and a command-line tool.

## Business Goals & Success Criteria

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| Unique SAP icons in catalog | 0 | 500+ | Ongoing | Icon discovery & cataloging | user |
| New icons discovered per run | — | 100+ | Per execution | Automated icon extraction | user |
| Catalog growth | Static | Continuously growing | Ongoing | Deduplication & append | user |

## Key Milestones

1. **Search** — Agent queries Google Images for SAP icons using configurable search parameters
2. **Extract** — Agent extracts image URLs and metadata from search results
3. **Download** — Agent downloads icon images to local storage
4. **Deduplicate** — Agent compares new icons against existing catalog (by image hash or URL) and discards duplicates
5. **Catalog** — Agent appends new unique icons (image file + metadata) to the persistent catalog
6. **Query** — User can ask the agent conversational questions about the catalog (e.g., "find icons related to Finance")

## Business Architecture (RBA)

### End-to-End Process

Plan to Fulfill for Digital Assets

### Process Hierarchy

```
Plan to Fulfill for Digital Assets
└── Make to Release (software product)
    └── Operate production of digital products (BPS-347_009)
        └── Develop, build and integrate digital assets
        └── Prepare digital asset operations
```

### Summary

The challenge maps to the digital asset production operations sub-process within the Plan to Fulfill for Digital Assets E2E, specifically around building and integrating digital assets (icons) into an accessible catalog.

## Fit Gap Analysis

| Requirement (business) | Standard asset(s) found | API ORD ID | MCP Server ORD ID | MCP Server Version | Webhook API ORD ID | Data Product ORD ID | Gap? | Notes / assumptions |
|------------------------|------------------------|------------|-------------------|--------------------|--------------------|---------------------|------|---------------------|
| Search Google Images for SAP icons | None | — | — | — | — | — | Yes | No standard SAP product covers web scraping of Google Images; custom agent required |
| Download icon images from URLs | None | — | — | — | — | — | Yes | Custom HTTP download logic needed |
| Deduplicate icons by hash/URL | None | — | — | — | — | — | Yes | Custom deduplication logic needed |
| Persist and query icon catalog | None | — | — | — | — | — | Yes | Local file-based catalog (JSON/CSV); no SAP standard covers this |
| Conversational chat interface for icon queries | None | — | — | — | — | — | Yes | Custom AI agent (A2A protocol) required |

### Key findings

- No standard SAP product or API covers web-based icon discovery and cataloging — full custom development is required.
- Google Images search with clipart/large image filters is the primary source, accessed via HTTP scraping or the Google Custom Search API.
- Deduplication is best achieved via perceptual image hashing (e.g., `imagehash` library) combined with URL tracking.
- The catalog should be a persistent local store (JSON or SQLite) that the agent reads and writes across runs.
- The agent needs two interaction modes: a conversational A2A chat interface and a CLI entry point.
- Python is the recommended implementation language; tools like `requests`, `Pillow`, and `imagehash` cover the core needs.

## Recommendations

### SAP Icon Extractor — Autonomous Discovery & Catalog Agent

#### Executive Summary

Custom Python AI agent that scrapes, deduplicates, and catalogs SAP icons.

#### Recommended Solution

A pro-code Python AI agent following the A2A protocol. The agent uses Google Images search (via HTTP scraping or Google Custom Search API) to find SAP icon images, downloads them locally, deduplicates them using perceptual image hashing, and appends new unique entries to a persistent JSON catalog. Users interact with the agent via a conversational chat interface (A2A) or directly via CLI. The catalog stores icon images, source URLs, discovery timestamps, and tags.

#### Problem Statement

Designers and developers waste time manually hunting for SAP icons across disparate websites. There is no automated, deduplicated, and queryable library of SAP icons available.

#### Affected User Roles

- UX/UI Designers working on SAP applications
- Frontend developers building SAP Fiori or SAPUI5 interfaces
- Content managers maintaining SAP documentation

#### Important factors

##### Continuous catalog growth
Every run discovers new icons and appends them — the catalog improves over time without manual effort.

##### Deduplication quality
Perceptual hashing catches visually identical icons even when downloaded from different URLs or at different resolutions.

##### Dual interaction modes
Both conversational chat (ask "show me icons for HR") and CLI (run `python main.py --search "SAP Finance icons"`) are supported.

#### Potential risks

##### Google Images scraping reliability
Google's HTML structure may change, breaking the scraper. Mitigation: use the official Google Custom Search JSON API with an API key for stability.

##### Copyright and licensing of scraped images
Extracted icons may have varying licenses. Mitigation: catalog the source URL so users can verify licensing.

#### Recommended solution category

AI Agent

#### Intent fit
88%
