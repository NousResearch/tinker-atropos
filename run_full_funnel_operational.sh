#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/heomin/.hermes/hermes-agent/tinker-atropos"
VENV="/Users/heomin/.hermes/hermes-agent/venv/bin/activate"
ENV_FILE="$HOME/.hermes/.env"
PAPERCLIP_BASE_URL="${PAPERCLIP_API_URL:-http://127.0.0.1:3100}"

can_run_local_trusted_sync() {
  python3 - "$PAPERCLIP_BASE_URL" <<'PY'
import json
import sys
import urllib.parse
import urllib.request

base = sys.argv[1].rstrip('/')
parsed = urllib.parse.urlparse(base)
if (parsed.hostname or '').strip().lower() not in {'127.0.0.1', 'localhost', '::1'}:
    raise SystemExit(1)

health_url = f"{base}/health" if base.endswith('/api') else f"{base}/api/health"
try:
    with urllib.request.urlopen(health_url, timeout=5) as response:
        payload = json.loads(response.read().decode('utf-8'))
except Exception:
    raise SystemExit(1)

raise SystemExit(0 if payload.get('deploymentMode') == 'local_trusted' else 1)
PY
}

INPUT_PATH="${1:-$ROOT/sample_research_strategy.txt}"
PROJECT_SLUG="${2:-ordinarybiz-daily}"
PRESET="${3:-ordinarybiz}"
BUSINESS_COUNT="${4:-3}"
X_COUNT="${5:-3}"
LANDING_COUNT="${6:-3}"
RETENTION_COUNT="${7:-3}"

STAMP="$(date +%Y%m%d-%H%M%S)"
DATE_FOLDER="$(date +%Y-%m-%d)"
OPS_DIR="$ROOT/outputs/$DATE_FOLDER/$PROJECT_SLUG/ops"
mkdir -p "$OPS_DIR"

RUN_LOG="$OPS_DIR/full-funnel-operational-$STAMP.log"
PIPELINE_JSON="$OPS_DIR/full-funnel-payload-$STAMP.json"
EXPORT_LOG="$OPS_DIR/publish-ready-$STAMP.log"
STATUS_JSON="$OPS_DIR/full-funnel-status-$STAMP.json"
SYNC_JSON="$OPS_DIR/paperclip-sync-$STAMP.json"

exec > >(tee -a "$RUN_LOG") 2>&1

echo "[full-funnel-operational] start $STAMP"
echo "input=$INPUT_PATH"
echo "project=$PROJECT_SLUG"
echo "preset=$PRESET"

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
  --save \
  --json > "$PIPELINE_JSON"

echo "saved_pipeline_json=$PIPELINE_JSON"

python publish_ready_exporter.py "$PIPELINE_JSON" --save --preset "$PRESET" | tee "$EXPORT_LOG"
python ops/run_full_funnel_status.py --root "$ROOT" > "$STATUS_JSON"
echo "saved_status_json=$STATUS_JSON"

if [[ -n "${PAPERCLIP_API_KEY:-}" ]] || can_run_local_trusted_sync; then
  python ops/paperclip_tinker_atropos_sync.py --root "$ROOT" > "$SYNC_JSON"
  echo "saved_sync_json=$SYNC_JSON"
else
  printf '{\n  "skipped": true,\n  "reason": "paperclip auth required",\n  "base_url": "%s"\n}\n' "$PAPERCLIP_BASE_URL" > "$SYNC_JSON"
  echo "saved_sync_json=$SYNC_JSON"
  echo "paperclip_sync=skipped_auth_required"
fi

echo "[full-funnel-operational] done $STAMP"