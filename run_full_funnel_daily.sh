#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/heomin/.hermes/hermes-agent/tinker-atropos"
VENV="/Users/heomin/.hermes/hermes-agent/venv/bin/activate"
ENV_FILE="$HOME/.hermes/.env"

INPUT_PATH="${1:-$ROOT/sample_research_strategy.txt}"
PROJECT_SLUG="${2:-ordinarybiz-daily}"
PRESET="${3:-ordinarybiz}"
BUSINESS_COUNT="${4:-3}"
X_COUNT="${5:-3}"
LANDING_COUNT="${6:-3}"
RETENTION_COUNT="${7:-3}"

cd "$ROOT"
source "$VENV"
if [[ -f "$ENV_FILE" ]]; then
  set +u
  set -a
  source "$ENV_FILE"
  set +a
  set -u
fi

python run_research_to_full_funnel.py "$INPUT_PATH" \
  --project "$PROJECT_SLUG" \
  --preset "$PRESET" \
  --business-count "$BUSINESS_COUNT" \
  --x-count "$X_COUNT" \
  --landing-count "$LANDING_COUNT" \
  --retention-count "$RETENTION_COUNT" \
  --selection-mode reward \
  --save
