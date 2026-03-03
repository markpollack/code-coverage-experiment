#!/usr/bin/env bash
#
# Archive an experiment run as dated tarballs on a GitHub release.
#
# Usage:
#   ./scripts/archive-run.sh <run-name> <date> [--draft]
#
# Example:
#   ./scripts/archive-run.sh full-suite-v1 2026-03-03
#   ./scripts/archive-run.sh full-suite-v1 2026-03-03 --draft
#
# Creates:
#   code-coverage-results-<date>.tar.gz   — result JSON + workspaces (~22 MB compressed)
#   code-coverage-analysis-<date>.tar.gz  — analysis artifacts (tables, figures, cards, summary)
#   code-coverage-run-log-<date>.tar.gz   — execution log
#
# Publishes as GitHub release tagged <run-name>.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
RESULTS_DIR="$PROJECT_ROOT/results/code-coverage-experiment"
LOG_FILE="$PROJECT_ROOT/results/full-suite-run.log"
STAGING_DIR="$PROJECT_ROOT/.archive-staging"

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <run-name> <date> [--draft]"
    echo "Example: $0 full-suite-v1 2026-03-03"
    exit 1
fi

RUN_NAME="$1"
RUN_DATE="$2"
DRAFT_FLAG=""
if [[ "${3:-}" == "--draft" ]]; then
    DRAFT_FLAG="--draft"
fi

RESULTS_TARBALL="code-coverage-results-${RUN_DATE}.tar.gz"
ANALYSIS_TARBALL="code-coverage-analysis-${RUN_DATE}.tar.gz"
LOG_TARBALL="code-coverage-run-log-${RUN_DATE}.tar.gz"

echo "=== Archiving run: $RUN_NAME ($RUN_DATE) ==="

# Clean staging
rm -rf "$STAGING_DIR"
mkdir -p "$STAGING_DIR"

# Package results
echo "Packaging results..."
if [[ -d "$RESULTS_DIR" ]]; then
    tar czf "$STAGING_DIR/$RESULTS_TARBALL" -C "$RESULTS_DIR" .
    echo "  $RESULTS_TARBALL ($(du -h "$STAGING_DIR/$RESULTS_TARBALL" | cut -f1))"
else
    echo "  ERROR: $RESULTS_DIR not found"
    exit 1
fi

# Package analysis
echo "Packaging analysis..."
ANALYSIS_DIR="$PROJECT_ROOT/analysis"
if [[ -d "$ANALYSIS_DIR" ]]; then
    tar czf "$STAGING_DIR/$ANALYSIS_TARBALL" -C "$PROJECT_ROOT" analysis/
    echo "  $ANALYSIS_TARBALL ($(du -h "$STAGING_DIR/$ANALYSIS_TARBALL" | cut -f1))"
else
    echo "  WARNING: $ANALYSIS_DIR not found, skipping"
fi

# Package log
echo "Packaging run log..."
if [[ -f "$LOG_FILE" ]]; then
    tar czf "$STAGING_DIR/$LOG_TARBALL" -C "$(dirname "$LOG_FILE")" "$(basename "$LOG_FILE")"
    echo "  $LOG_TARBALL ($(du -h "$STAGING_DIR/$LOG_TARBALL" | cut -f1))"
else
    echo "  WARNING: $LOG_FILE not found, skipping"
fi

# Generate release notes
echo "Generating release notes..."
NOTES_FILE="$STAGING_DIR/release-notes.md"
cat > "$NOTES_FILE" << 'HEADER'
## Code Coverage Experiment — Full Suite Run
HEADER

echo "" >> "$NOTES_FILE"
echo "**Date**: ${RUN_DATE}" >> "$NOTES_FILE"
echo "**Model**: claude-sonnet-4-6" >> "$NOTES_FILE"
echo "**Dataset**: 5 Spring Getting Started guides (0% baseline)" >> "$NOTES_FILE"
echo "**Variants**: control, variant-a, variant-b, variant-c" >> "$NOTES_FILE"
echo "" >> "$NOTES_FILE"

cat >> "$NOTES_FILE" << 'BODY'
### Results Summary

| Variant | Pass Rate | Avg T3 | Avg Eff | Total Cost |
|---------|-----------|--------|---------|------------|
| Control | 100% | 0.62 | 0.878 | $4.57 |
| Variant-A (hardened prompt) | 100% | 0.80 | 0.937 | $4.17 |
| Variant-B (targeted KB) | 100% | 0.697 | 0.837 | $4.98 |
| Variant-C (deep KB) | 100% | 0.757 | 0.823 | $4.55 |

**Key finding**: Hardened prompt (variant-a) beats KB injection on simple Spring guides.

### Run IDs

| Variant | Run ID |
|---------|--------|
| control | `05aa20bb-5e04-42e7-acf6-e74276dcb1c2` |
| variant-a | `4f25dfd2-ba55-4add-96f8-2f9030f91a2f` |
| variant-b | `9c2d49af-8fc3-407c-aaf6-9b0b17c3b4b3` |
| variant-c | `d7926aaf-a2f7-4ab0-9c96-1fdd66ac5dd6` |

### Archives

| Archive | Contents |
|---------|----------|
BODY

echo "| \`${RESULTS_TARBALL}\` | Result JSON + workspaces (4 variants × 5 guides) |" >> "$NOTES_FILE"
echo "| \`${ANALYSIS_TARBALL}\` | Analysis artifacts (tables, figures, cards, findings summary) |" >> "$NOTES_FILE"
echo "| \`${LOG_TARBALL}\` | Execution log (1h39m run transcript) |" >> "$NOTES_FILE"

cat >> "$NOTES_FILE" << 'EXTRACT'

### Extraction

```bash
# Extract results to project directory
mkdir -p results/code-coverage-experiment
tar xzf code-coverage-results-*.tar.gz -C results/code-coverage-experiment/

# Extract analysis (frozen-in-time snapshot)
tar xzf code-coverage-analysis-*.tar.gz -C .

# Extract run log
tar xzf code-coverage-run-log-*.tar.gz -C results/
```

To regenerate analysis from extracted results (or after ETL changes):

```bash
uv venv && uv pip install -r requirements.txt
.venv/bin/python scripts/load_results.py
.venv/bin/python scripts/variant_comparison.py
.venv/bin/python scripts/plot_variant_radar.py
.venv/bin/python scripts/generate_item_cards.py
```
EXTRACT

# List assets to upload
ASSETS=("$STAGING_DIR/$RESULTS_TARBALL")
if [[ -f "$STAGING_DIR/$ANALYSIS_TARBALL" ]]; then
    ASSETS+=("$STAGING_DIR/$ANALYSIS_TARBALL")
fi
if [[ -f "$STAGING_DIR/$LOG_TARBALL" ]]; then
    ASSETS+=("$STAGING_DIR/$LOG_TARBALL")
fi

echo ""
echo "Ready to create release:"
echo "  Tag: $RUN_NAME"
echo "  Assets: ${ASSETS[*]}"
echo "  Draft: ${DRAFT_FLAG:-no}"
echo ""

# Create release
gh release create "$RUN_NAME" \
    --title "Full Suite Run: ${RUN_DATE} (4 variants × 5 guides)" \
    --notes-file "$NOTES_FILE" \
    $DRAFT_FLAG \
    "${ASSETS[@]}"

echo ""
echo "=== Release created: $RUN_NAME ==="
echo "View: gh release view $RUN_NAME"

# Clean up staging
rm -rf "$STAGING_DIR"
