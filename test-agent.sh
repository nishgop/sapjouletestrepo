#!/usr/bin/env bash
# =============================================================================
# SAP Icon Extractor Agent — Test Script
# =============================================================================
# Usage:
#   chmod +x test-agent.sh
#   AGENT_URL=https://<your-agent-url> BEARER_TOKEN=<your-token> ./test-agent.sh
#
# Or inline:
#   AGENT_URL=https://... BEARER_TOKEN=eyJ... ./test-agent.sh
# =============================================================================

set -euo pipefail

AGENT_URL="${AGENT_URL:-https://e70b0034-41a7bbd6.60726259.canary-eu1.ca.ai.cloud.sap}"
BEARER_TOKEN="${BEARER_TOKEN:-}"

if [[ -z "$AGENT_URL" ]]; then
  echo "ERROR: AGENT_URL is not set. Example:"
  echo "  AGENT_URL=https://<your-agent-url> BEARER_TOKEN=<token> ./test-agent.sh"
  exit 1
fi

if [[ -z "$BEARER_TOKEN" ]]; then
  echo "ERROR: BEARER_TOKEN is not set."
  exit 1
fi

BASE_URL="${AGENT_URL%/}"
PASS=0
FAIL=0

# ── Helpers ──────────────────────────────────────────────────────────────────

check() {
  local label="$1"
  local result="$2"
  local expected="$3"
  if echo "$result" | grep -qi "$expected"; then
    echo "  ✅ PASS: $label"
    ((PASS++))
  else
    echo "  ❌ FAIL: $label"
    echo "     Expected to find: $expected"
    echo "     Got: $(echo "$result" | head -c 300)"
    ((FAIL++))
  fi
}

send_message() {
  local message="$1"
  local context_id="${2:-test-$(date +%s)}"
  curl -s -X POST "$BASE_URL/" \
    -H "Authorization: Bearer $BEARER_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"jsonrpc\": \"2.0\",
      \"id\": 1,
      \"method\": \"tasks/send\",
      \"params\": {
        \"message\": {
          \"role\": \"user\",
          \"parts\": [{\"type\": \"text\", \"text\": \"$message\"}]
        },
        \"contextId\": \"$context_id\"
      }
    }"
}

# ── Tests ─────────────────────────────────────────────────────────────────────

echo ""
echo "=============================="
echo " SAP Icon Extractor Agent Tests"
echo " URL: $BASE_URL"
echo "=============================="
echo ""

# 1. Agent card
echo "▶ Test 1: Agent card"
CARD=$(curl -s "$BASE_URL/.well-known/agent.json")
check "agent card returns name" "$CARD" "sap-icon-extractor-agent"
check "agent card has skills" "$CARD" "skills"

# 2. Catalog query (catalog may be empty on first run)
echo ""
echo "▶ Test 2: Catalog query"
RESULT=$(send_message "How many icons are in the catalog right now?")
check "catalog query responds" "$RESULT" "icon\|catalog\|0\|empty"

# 3. Icon search
echo ""
echo "▶ Test 3: Search for SAP icons"
RESULT=$(send_message "Search for SAP icons and report how many URLs you found. Do not download yet.")
check "search returns results" "$RESULT" "found\|discovered\|result\|URL\|icon"

# 4. Full extraction run (small)
echo ""
echo "▶ Test 4: Extract and catalog SAP icons (max 5)"
RESULT=$(send_message "Search for SAP icons using query 'SAP UI5 icons', download up to 5, deduplicate, and update the catalog. Report the summary.")
check "extraction completes" "$RESULT" "discover\|download\|added\|skipped\|catalog\|icon"

# 5. Category search
echo ""
echo "▶ Test 5: Find icons related to Finance"
RESULT=$(send_message "Find icons related to Finance in the catalog")
check "category query answered" "$RESULT" "Finance\|finance\|catalog\|icon\|found\|no"

echo ""
echo "=============================="
echo " Results: $PASS passed, $FAIL failed"
echo "=============================="
echo ""
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
