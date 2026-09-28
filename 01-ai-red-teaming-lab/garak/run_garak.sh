#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
garak_root="$project_root/garak"
results_dir="${RESULTS_DIR:-$project_root/results/garak}"
target_url="${TARGET_URL:-http://127.0.0.1:8000}"
probes="${GARAK_PROBES:-promptinject,encoding}"

if [[ "${1:-}" == "--list-probes" ]]; then
  if ! command -v garak >/dev/null 2>&1; then
    echo "Garak is not installed. Install the pinned version with: python -m pip install 'garak==0.15.1'" >&2
    exit 0
  fi
  garak --list_probes
  exit 0
fi

if ! command -v garak >/dev/null 2>&1; then
  echo "Garak is not installed. Install the pinned version with: python -m pip install 'garak==0.15.1'" >&2
  exit 1
fi

mkdir -p "$results_dir"
export NORTHWIND_CHATBOT_URL="$target_url"
export PYTHONPATH="$garak_root${PYTHONPATH:+:$PYTHONPATH}"

garak \
  --model_type generator.NorthwindGenerator \
  --model_name northwind \
  --probes "$probes" \
  --report_prefix "$results_dir/northwind" \
  --parallel_requests 1
