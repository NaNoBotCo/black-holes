#!/bin/bash
# Build the site into docs/, checked. GitHub Pages serves docs/ from main.
#
#   ./publish.sh            # figures + pages, into docs/ (the ray-traced pictures are kept)
#   ./publish.sh --render   # also redo the ray-traced pictures (about four minutes)
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONUTF8=1
SITE_URL="${SITE_URL:-https://nanobotco.github.io/black-holes}"

STYLE="$HOME/.claude/bin/stylecheck.py"
if [ -f "$STYLE" ]; then
  python3 "$STYLE" tools js README.md NOTICE.txt || { echo "REFUSED: style. See ~/.claude/STYLE.md"; exit 4; }
fi

if [ "${1:-}" = "--render" ] || [ ! -f build/img/hero.jpg ]; then
  python3 tools/render.py
fi
python3 tools/figures.py
SITE_URL="$SITE_URL" python3 tools/site.py
python3 tools/links.py --quiet || { echo "REFUSED: broken internal links"; exit 3; }
python3 tests/test_site.py

# nothing that names this machine may be published
if grep -rl "/Users/" build/site >/dev/null 2>&1; then
  echo "REFUSED: host paths found in build/site"; exit 2
fi

rm -rf docs
cp -R build/site docs
touch docs/.nojekyll
echo "docs/ ← $(find docs -name 'index.html' | wc -l | tr -d ' ') pages, $(du -sh docs | cut -f1)"
