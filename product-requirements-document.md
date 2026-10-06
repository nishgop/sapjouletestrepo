# Product Requirements Document (PRD)

**Title:** SAP Icon Extractor Agent
**Date:** 2026-10-01
**Owner:** Product Owner
**Solution Category:** AI Agent

---

## Product Purpose & Value Proposition

**Elevator Pitch:**
Designers and developers waste time manually hunting for SAP icons across disparate websites. This agent automates the discovery, download, deduplication, and cataloging of SAP icons found on Google Images — so teams always have an up-to-date, queryable icon library at their fingertips.

**Business Need:**
There is no automated, deduplicated, and queryable library of SAP icons available. Teams must manually search, evaluate, and collect icons one by one, leading to duplicated effort, missed icons, and inconsistent design assets.

**Expected Value:**
- A continuously growing catalog of unique SAP icons, growing from 0 to 500+ over time
- 100+ new unique icons discovered per agent run
- Elimination of manual icon search effort

**Product Objectives (Prioritized):**
1. Continuously discover and download new unique SAP icons from Google Images
2. Maintain a deduplicated, persistent catalog that grows across runs
3. Enable users to query the catalog conversationally ("find me icons related to Finance")

---

## Business Metrics

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| Unique SAP icons in catalog | 0 | 500+ | Ongoing | Icon discovery & cataloging | user |
| New icons discovered per run | — | 100+ | Per execution | Automated icon extraction | user |
| Catalog growth | Static | Continuously growing | Ongoing | Deduplication & append | user |

---

## User Profiles & Personas

### Primary Persona: Alex — UX/UI Designer

Alex is a 31-year-old UX designer working on SAP Fiori applications. They spend 20–30 minutes per project searching for the right SAP icons across SAP UI5 Explorer, GitHub, and Google Images. Alex is frustrated by the fragmented nature of icon sources and the risk of using duplicate or outdated icons. They want a single, searchable icon library they can query in natural language — without wasting half their morning on Google.

### Secondary Persona: Jordan — Frontend Developer

Jordan is a 27-year-old frontend developer building SAPUI5 interfaces. They need quick access to SAP icons for buttons, menus, and status indicators. Jordan is comfortable with command-line tools and wants to run a quick CLI command to refresh the icon catalog before starting a sprint.

### Other User Types

- Content managers maintaining SAP documentation who need consistent icon assets.

---

## User Goals & Tasks

### For Alex (Designer):

**Goals:**
- Find relevant SAP icons by category or keyword without manual searching
- Know the icon is unique and hasn't already been collected

**Key Tasks:**
- Ask the agent "show me icons related to HR" via chat
- Browse the catalog for a specific icon set

### For Jordan (Developer):

**Goals:**
- Keep the local icon catalog up to date before each sprint
- Download new icons without manual work

**Key Tasks:**
- Run the agent via CLI to trigger a fresh discovery and download run
- Review the summary of newly added icons

---

## Goals and Non-Goals

### Goals (In Scope)

- Search Google Images for SAP icons using configurable keyword queries
- Download and store icon images locally
- Deduplicate icons using perceptual image hashing and URL tracking
- Append new unique icons to a persistent catalog (JSON) with metadata
- Expose a conversational A2A chat interface for catalog queries
- Expose a CLI entry point for on-demand extraction runs

### Non-Goals (Out of Scope)

- Licensing verification or legal compliance for downloaded icons
- Integration with SAP product systems (S/4HANA, SuccessFactors, etc.)
- UI application frontend beyond the agent's A2A chat interface
- Uploading icons to any external system or DAM platform

---

## Requirements

### Must-Have Requirements

**R1: Google Images Icon Search**
- **Problem to Solve**: Users have no automated way to discover SAP icons from the web.
- **User Story**: As a designer, I need the agent to search Google Images for SAP icons so that I don't have to do it manually.
- **Acceptance Criteria**:
  - Given a search query (e.g., "SAP icons"), when the agent runs, then it retrieves image URLs from Google Images filtered to clipart/large images.
  - The agent supports configurable search terms via CLI argument and chat prompt.
- **Maps to Objective**: 1
- **Priority Rank**: 1

**R2: Icon Download & Local Storage**
- **Problem to Solve**: Discovered icons must be saved locally for reuse.
- **User Story**: As a developer, I need discovered icons downloaded to a local folder so that I can use them in my projects.
- **Acceptance Criteria**:
  - Given a set of discovered image URLs, when the agent processes them, then each valid image is downloaded and saved with a consistent filename.
  - Failed downloads are logged and skipped without stopping the run.
- **Maps to Objective**: 1
- **Priority Rank**: 2

**R3: Deduplication**
- **Problem to Solve**: Without deduplication, the same icon would be stored multiple times across runs.
- **User Story**: As a designer, I need the agent to detect and skip duplicate icons so that my catalog stays clean.
- **Acceptance Criteria**:
  - Given an existing catalog, when a newly downloaded image matches an existing entry by perceptual hash or URL, then it is discarded and not added again.
  - Deduplication works across runs (persistent state).
- **Maps to Objective**: 2
- **Priority Rank**: 3

**R4: Persistent Catalog**
- **Problem to Solve**: Without a persistent catalog, all discovered icons are lost between runs.
- **User Story**: As a designer, I need a catalog that grows over time so that each run adds to my library rather than starting from scratch.
- **Acceptance Criteria**:
  - The catalog is stored as a JSON file with fields: filename, source URL, discovery timestamp, perceptual hash, and tags.
  - Each run appends new unique entries without overwriting existing ones.
- **Maps to Objective**: 2
- **Priority Rank**: 4

**R5: Conversational Chat Interface (A2A)**
- **Problem to Solve**: Users need a natural language interface to query the catalog.
- **User Story**: As a designer, I need to ask the agent "find icons related to Finance" so that I can find relevant icons without knowing exact filenames.
- **Acceptance Criteria**:
  - The agent responds to natural language queries about the catalog (search by keyword, count, source).
  - The agent can also trigger a new discovery run from chat.
- **Maps to Objective**: 3
- **Priority Rank**: 5

**R6: CLI Entry Point**
- **Problem to Solve**: Developers prefer command-line tools for on-demand runs.
- **User Story**: As a developer, I need to run the agent via CLI so that I can integrate it into my workflow before a sprint.
- **Acceptance Criteria**:
  - A CLI command triggers a discovery, download, deduplication, and catalog update run.
  - The CLI outputs a summary: icons found, icons added, icons skipped as duplicates.
- **Maps to Objective**: 1, 2
- **Priority Rank**: 6

---

## Solution Architecture

**Architecture Overview:**
A Python AI agent (A2A protocol) with two interaction modes — conversational chat and CLI. The agent uses the Google Custom Search JSON API (or HTTP scraping as fallback) to find SAP icons, downloads them, deduplicates using `imagehash`, and persists entries to a local JSON catalog.

**Key Components:**

- **Agent Core (Python, A2A)**: Orchestrates search, download, deduplication, and catalog operations; handles conversational queries.
- **Google Images Search Module**: Queries Google Images (via Google Custom Search API or HTTP) with configurable search terms.
- **Icon Downloader**: Downloads image files from discovered URLs and stores them locally.
- **Deduplication Engine**: Computes perceptual hashes (using `imagehash`/`Pillow`) and compares against the catalog to detect duplicates.
- **Catalog Store (JSON)**: Persistent flat-file catalog storing icon metadata (filename, URL, hash, timestamp, tags).
- **CLI Interface**: Entry point for on-demand runs via command line.

**Integration Points:**

- Google Images / Google Custom Search API: read-only, HTTP, on-demand per run.

---

### Agent Extensibility & Instrumentation

**Agent Extensibility:**
- The agent is designed with extension points so new search sources (e.g., SAP UI5 GitHub, SAP Fiori Design Guidelines) can be added as modular search plugins without modifying the core logic.
- The catalog schema is versioned to support future field additions (e.g., license type, icon category, resolution).

**Business Step Instrumentation:**
- All six key milestones (see Milestones section) are instrumented with structured log statements following the pattern: `[MILESTONE_ID].[achieved|missed]: [description]`.
- Logs are emitted to stdout in structured format for observability and debugging in production.

---

### Automation & Agent Behaviour

**Automation Level:** Autonomous agent

**Actions the system performs without human approval:**
- Searching Google Images for SAP icons
- Downloading icon images to local storage
- Deduplicating and appending entries to the catalog

**Actions that require human review or approval:**
- None — the agent is fully autonomous; users review results after the run via chat or CLI output.

**Model or engine used:** GPT-4o (or equivalent) via SAP Generative AI Hub for conversational query handling.

**Knowledge & data sources accessed:**
- Google Images (public web): icon discovery, read-only
- Local catalog (JSON file): persistent icon storage, read/write

**Tools or connectors invoked:**
- `search_google_images`: searches Google Images for SAP icons by keyword (read-only)
- `download_icon`: downloads an image from a URL to local storage (write)
- `compute_hash`: computes perceptual hash of an image for deduplication (read-only)
- `read_catalog`: reads the current catalog from the JSON file (read-only)
- `update_catalog`: appends new unique icon entries to the catalog (write)

**Guardrails & fail-safes:**
- The agent never deletes existing catalog entries; it only appends.
- If a download fails (e.g., 404, timeout), the icon is logged as skipped and the run continues.
- If the Google Search API quota is exceeded, the agent logs the error and exits gracefully with a summary of what was completed.
- The agent does not store or transmit personal data.

---

## Milestones

### M1: Search Executed

- **Description**: The agent has submitted a search query to Google Images and received results.
- **Achieved when**: At least one image URL is returned from the search.
- **Log on achievement**: `M1.achieved: Google Images search completed, {n} image URLs discovered`
- **Log on miss**: `M1.missed: Google Images search returned no results or failed`

### M2: Icons Extracted

- **Description**: The agent has extracted all valid image URLs from the search results.
- **Achieved when**: Image URLs are parsed and validated from the search response.
- **Log on achievement**: `M2.achieved: {n} image URLs extracted from search results`
- **Log on miss**: `M2.missed: No valid image URLs could be extracted from search results`

### M3: Icons Downloaded

- **Description**: The agent has downloaded icon images to local storage.
- **Achieved when**: At least one image file is successfully saved locally.
- **Log on achievement**: `M3.achieved: {n} icons downloaded to local storage`
- **Log on miss**: `M3.missed: No icons could be downloaded — all downloads failed or were skipped`

### M4: Deduplication Complete

- **Description**: The agent has compared downloaded icons against the existing catalog and identified unique ones.
- **Achieved when**: Deduplication check has run against all downloaded images.
- **Log on achievement**: `M4.achieved: deduplication complete — {n} unique, {m} duplicates skipped`
- **Log on miss**: `M4.missed: deduplication could not be completed`

### M5: Catalog Updated

- **Description**: The agent has appended new unique icons to the persistent catalog.
- **Achieved when**: The catalog JSON file is updated with at least one new entry.
- **Log on achievement**: `M5.achieved: {n} new icons appended to catalog (total: {total})`
- **Log on miss**: `M5.missed: no new icons added to catalog this run`

### M6: Query Responded

- **Description**: The agent has answered a user's conversational query about the catalog.
- **Achieved when**: A natural language query is processed and a response is returned.
- **Log on achievement**: `M6.achieved: catalog query answered for query="{query}"`
- **Log on miss**: `M6.missed: catalog query could not be resolved`

---

## Risks, Assumptions, and Dependencies

### Risks

- **Google Images scraping reliability**: Google's HTML structure may change, breaking the scraper. Mitigation: use the official Google Custom Search JSON API with an API key.
- **Icon licensing**: Extracted icons may have varying licenses. Mitigation: catalog the source URL so users can verify licensing independently.
- **Search result quality**: Google Images results may include non-SAP icons. Mitigation: use specific search terms and allow keyword configuration.

### Assumptions

- The agent runs in an environment with internet access to reach Google Images.
- A Google Custom Search API key is available or can be configured by the user.
- Local file system write access is available for icon storage and catalog persistence.

### Dependencies

- Google Custom Search JSON API (or public Google Images access)
- Python libraries: `requests`, `Pillow`, `imagehash`, `aiohttp`
