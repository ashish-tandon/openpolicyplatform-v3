#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="/workspace/external"
mkdir -p "$BASE_DIR"

declare -a REPOS=(
  "https://github.com/michaelmulley/openparliament.git"
  "https://github.com/rarewox/open-policy-infra.git"
  "https://github.com/rarewox/admin-open-policy.git"
  "https://github.com/rarewox/open-policy-app.git"
  "https://github.com/rarewox/open-policy-web.git"
  "https://github.com/rarewox/open-policy.git"
  "https://github.com/opencivicdata/scrapers-ca.git"
  "https://github.com/biglocalnews/civic-scraper.git"
)

pushd "$BASE_DIR" >/dev/null
for REPO in "${REPOS[@]}"; do
  NAME=$(basename "$REPO" .git)
  if [ -d "$NAME/.git" ]; then
    echo "Updating $NAME"
    git -C "$NAME" fetch --all --prune
    git -C "$NAME" checkout -q main || git -C "$NAME" checkout -q master || true
    git -C "$NAME" pull --ff-only || true
  else
    echo "Cloning $NAME"
    git clone --depth 1 "$REPO" "$NAME"
  fi
done
popd >/dev/null

echo "All repos ingested into $BASE_DIR"