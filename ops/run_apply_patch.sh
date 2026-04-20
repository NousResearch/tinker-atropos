#!/usr/bin/env bash
set -euo pipefail

cd /Users/heomin/.hermes/hermes-agent/tinker-atropos
python ops/run_apply_patch.py "$@"
