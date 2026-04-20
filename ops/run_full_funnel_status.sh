#!/usr/bin/env bash
set -euo pipefail

cd /Users/heomin/.hermes/hermes-agent/tinker-atropos
python ops/run_full_funnel_status.py "$@"
