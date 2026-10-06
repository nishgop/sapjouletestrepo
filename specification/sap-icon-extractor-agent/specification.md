# Specification: sap-icon-extractor-agent

> **Guidelines**: Read all applicable guidelines before executing ANY tasks below:
> - [guidelines.md](../guidelines.md) — Universal execution rules
> - [guidelines-agent.md](../guidelines-agent.md) — Universal agent patterns
> - [guidelines-agent-python.md](../guidelines-agent-python.md) — Python implementation details
> - [guidelines-agent-skills.md](../guidelines-agent-skills.md) — Runtime skills patterns
> - [guidelines-agent-mcp.md](../guidelines-agent-mcp.md) — MCP integration patterns

---

## Basic Setup

- [ ] Read `product-requirements-document.md` and `intent.md` at the solution root for full context
- [ ] Bootstrap agent code in `assets/sap-icon-extractor-agent/` using instructions from the `sap-agent-bootstrap` section (invoke from inside `assets/sap-icon-extractor-agent/`, use copy commands — do NOT create files manually)
- [ ] Install dependencies, validate the agent starts and responds at `/.well-known/agent.json`

---

## Runtime Skills

No runtime skills are required. The agent logic is straightforward (search → download → deduplicate → catalog → query) and does not involve complex multi-step workflows or domain-specific reference material that would bloat the system prompt.

---

## Project-Specific Tasks

### Google Images Search

- [ ] Add `requests`, `beautifulsoup4`, `lxml` to `requirements.txt` for HTTP search and HTML parsing
- [ ] Implement `search_google_images` tool in `app/tools/search_google_images.py`:
  - Accepts a `query` string and optional `max_results` integer (default 100)
  - Queries Google Images filtered to large clipart images using the URL pattern:
    `https://www.google.com/search?q={query}&udm=2&tbs=itp:clipart,isz:i`
  - Parses the HTML response to extract image URLs (src from `<img>` tags or data-src attributes)
  - Returns a list of dicts: `[{"url": str, "query": str, "discovered_at": ISO-timestamp}]`
  - Sets a browser-like User-Agent header to avoid trivial blocking
  - Handles request errors gracefully (logs and returns empty list on failure)
- [ ] Register `search_google_images` in `app/agent.py` tool list

### Icon Download

- [ ] Add `Pillow` to `requirements.txt`
- [ ] Implement `download_icon` tool in `app/tools/download_icon.py`:
  - Accepts a `url` string and `output_dir` string (default `icons/`)
  - Downloads the image to `output_dir` with a sanitized filename derived from the URL
  - Validates the file is a valid image using `Pillow` (reject non-images)
  - Returns a dict: `{"success": bool, "filepath": str|None, "error": str|None}`
  - Handles 404s, timeouts, and non-image content gracefully — logs and returns `success: false`
  - Creates `output_dir` if it does not exist
- [ ] Register `download_icon` in `app/agent.py` tool list

### Deduplication Engine

- [ ] Add `imagehash` to `requirements.txt`
- [ ] Implement `compute_hash` tool in `app/tools/compute_hash.py`:
  - Accepts a `filepath` string
  - Computes a perceptual hash (pHash) of the image using `imagehash`
  - Returns a dict: `{"hash": str, "filepath": str}`
  - Handles corrupt or unreadable image files gracefully
- [ ] Implement `is_duplicate` helper (not a tool) in `app/catalog.py`:
  - Accepts a hash string and URL string, and the current catalog list
  - Returns `True` if an entry with the same hash or URL already exists in the catalog
- [ ] Register `compute_hash` in `app/agent.py` tool list

### Persistent Catalog

- [ ] Implement `read_catalog` tool in `app/tools/read_catalog.py`:
  - Reads `icons/catalog.json` (creates empty catalog `[]` if file does not exist)
  - Returns the catalog as a list of dicts
- [ ] Implement `update_catalog` tool in `app/tools/update_catalog.py`:
  - Accepts a new icon entry dict: `{"filename": str, "source_url": str, "perceptual_hash": str, "discovered_at": str, "tags": [str]}`
  - Reads the current catalog from `icons/catalog.json`
  - Checks for duplicates using `is_duplicate` helper (skips if duplicate found)
  - Appends the new entry and writes back to `icons/catalog.json`
  - Returns `{"added": bool, "reason": str}`
- [ ] Register `read_catalog` and `update_catalog` in `app/agent.py` tool list
- [ ] Ensure catalog path is configurable via environment variable `ICON_CATALOG_PATH` (default: `icons/catalog.json`)

### Agent System Prompt

- [ ] In `app/agent.py`, implement `get_system_prompt()` with the following instructions:
  ```
  You are the SAP Icon Extractor Agent. Your job is to discover, download, deduplicate, and catalog SAP icons from Google Images.

  When asked to extract or find SAP icons:
  1. Use the search_google_images tool to search for SAP icons with the given query (or "SAP icons" by default).
  2. For each discovered image URL, use the download_icon tool to download it locally.
  3. For each successfully downloaded icon, use the compute_hash tool to get its perceptual hash.
  4. Read the current catalog using read_catalog.
  5. If the icon is not a duplicate (same hash or URL not already in catalog), use update_catalog to append it.
  6. Report a summary: total discovered, downloaded, added, skipped as duplicates.

  When asked questions about the catalog (e.g., "how many icons do we have?", "find icons related to Finance"):
  - Use read_catalog to retrieve the current catalog and answer the question directly.

  IMPORTANT:
  - Never fabricate or invent icon data. Always use tools.
  - If a download fails, skip and continue — do not stop the run.
  - Set max_results to 100 maximum per search to avoid context overflow.
  - Relay tool errors verbatim without embellishment.
  ```

### CLI Entry Point

- [ ] Implement `app/cli.py` as a standalone CLI script:
  - Accepts `--query` (default: "SAP icons"), `--max-results` (default: 100), `--output-dir` (default: `icons/`)
  - Runs the full discovery pipeline: search → download → deduplicate → catalog update
  - Prints a summary to stdout: `Discovered: N | Downloaded: N | Added: N | Skipped (duplicates): N`
  - Uses the same tool functions as the agent (not a separate implementation)
  - Entry point: `python -m app.cli`
- [ ] Add `click` to `requirements.txt` for CLI argument parsing

---

## Business Instrumentation

- [ ] Implement business step instrumentation for all 6 milestones from the PRD using structured logging and OpenTelemetry spans:
  - `M1` — Search Executed: `M1.achieved: Google Images search completed, {n} image URLs discovered` / `M1.missed: Google Images search returned no results or failed`
  - `M2` — Icons Extracted: `M2.achieved: {n} image URLs extracted from search results` / `M2.missed: No valid image URLs could be extracted from search results`
  - `M3` — Icons Downloaded: `M3.achieved: {n} icons downloaded to local storage` / `M3.missed: No icons could be downloaded — all downloads failed or were skipped`
  - `M4` — Deduplication Complete: `M4.achieved: deduplication complete — {n} unique, {m} duplicates skipped` / `M4.missed: deduplication could not be completed`
  - `M5` — Catalog Updated: `M5.achieved: {n} new icons appended to catalog (total: {total})` / `M5.missed: no new icons added to catalog this run`
  - `M6` — Query Responded: `M6.achieved: catalog query answered for query="{query}"` / `M6.missed: catalog query could not be resolved`
  - Use `@tracer.start_as_current_span("name")` decorator on regular async methods; use context manager form only inside non-generator async functions; NEVER inside async generators
  - Extract all business logic from `stream()` into a plain `_run_agent()` async helper; instrument that helper and call it from `stream()`
- [ ] Verify `bootstrap(app)` is called after `app = server.build()` in `main.py`

---

## MCP Tool Integration

No SAP API MCP servers are required for this agent. All tools are implemented as local Python functions. Skip all Path A/B/C MCP wiring steps.

- [ ] Confirm `asset.yaml` has no `requires` entries pointing to SAP MCP servers
- [ ] Skip `mcp-translation-file`, `setup-solution` (MCP wiring), and `mcp-mock-config` skill invocations — no external MCP servers are used

---

## Testing

- [ ] `conftest.py` only sets `IBD_TESTING=true`
- [ ] Write unit tests in `assets/sap-icon-extractor-agent/tests/`:
  - `test_search_google_images.py` — mock `requests.get`; verify URL construction and result parsing
  - `test_download_icon.py` — mock `requests.get` and `Pillow`; verify file saving, error handling
  - `test_compute_hash.py` — use a real small test image; verify hash is returned
  - `test_read_catalog.py` — use a temp file; verify empty catalog creation and reading
  - `test_update_catalog.py` — verify deduplication (by hash and URL) and successful append
  - `test_cli.py` — mock all tool functions; verify CLI output summary
- [ ] Write one integration test `test_integration.py` executing the full pipeline end-to-end with all external calls mocked (requests, Pillow, imagehash)
- [ ] Mock all LLM calls in tests — AI Core credentials are NOT available in test environment
- [ ] Run `pytest` from `assets/sap-icon-extractor-agent/` (no args)
- [ ] If coverage < 70%, add targeted tests until threshold met
- [ ] Run `pytest` again (no args) to generate final `test_report.json`
- [ ] Verify `test_report.json` exists in `assets/sap-icon-extractor-agent/`
