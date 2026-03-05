#!/usr/bin/env bash
set -euo pipefail

# Rerun Qwen items that hit the 80-turn limit (now 300 turns, 45min timeout)
# Requires LM Studio running qwen3-coder-30b on rutherford:1234

ITEMS=("gs-rest-service" "gs-reactive-rest-service" "spring-petclinic")
LOG_DIR="results"

for item in "${ITEMS[@]}"; do
    echo "=== Starting $item at $(date) ==="
    env -u ANTHROPIC_API_KEY \
        ./mvnw -q compile exec:java \
        -Dexec.args="--variant loopy-qwen3-coder --item $item" \
        2>&1 | tee "$LOG_DIR/qwen-rerun-$item.log"
    echo "=== Finished $item at $(date) ==="
done

echo "All reruns complete."
