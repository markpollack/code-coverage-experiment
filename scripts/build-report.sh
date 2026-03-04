#!/usr/bin/env bash
#
# Build the LaTeX report from Parquet data.
#
# Usage: ./scripts/build-report.sh
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "=== Generating LaTeX tables ==="
.venv/bin/python scripts/make_tables.py

echo ""
echo "=== Generating figures ==="
.venv/bin/python scripts/make_figures.py

echo ""
echo "=== Building PDF ==="
cd docs/latex
pdflatex -interaction=nonstopmode code-coverage-report.tex > /dev/null
pdflatex -interaction=nonstopmode code-coverage-report.tex > /dev/null

echo ""
echo "=== Done ==="
echo "PDF: docs/latex/code-coverage-report.pdf ($(du -h code-coverage-report.pdf | cut -f1))"
