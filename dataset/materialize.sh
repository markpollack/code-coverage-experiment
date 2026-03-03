#!/usr/bin/env bash
#
# Materialize dataset workspaces from Spring guide repos.
# Clones each guide repo (shallow) into workspaces/ and copies the complete/
# subdirectory into items/{id}/before/ for the experiment framework.
#
# Usage: ./dataset/materialize.sh [--verify]
#   --verify  Also runs ./mvnw clean compile test in each before/ directory

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACES_DIR="$SCRIPT_DIR/workspaces"
ITEMS_DIR="$SCRIPT_DIR/items"

GUIDES=(
  gs-rest-service
  gs-accessing-data-jpa
  gs-securing-web
  gs-reactive-rest-service
  gs-messaging-stomp-websocket
)

VERIFY=false
if [[ "${1:-}" == "--verify" ]]; then
  VERIFY=true
fi

echo "=== Materializing dataset workspaces ==="
echo "Workspaces: $WORKSPACES_DIR"
echo "Items:      $ITEMS_DIR"
echo ""

# Step 1: Clone repos
mkdir -p "$WORKSPACES_DIR"
for guide in "${GUIDES[@]}"; do
  if [[ -d "$WORKSPACES_DIR/$guide" ]]; then
    echo "[$guide] Already cloned, skipping"
  else
    echo "[$guide] Cloning..."
    git clone --depth 1 "https://github.com/spring-guides/${guide}.git" "$WORKSPACES_DIR/$guide"
  fi
done

echo ""

# Step 2: Copy complete/ into items/{id}/before/
for guide in "${GUIDES[@]}"; do
  BEFORE_DIR="$ITEMS_DIR/$guide/before"
  SOURCE_DIR="$WORKSPACES_DIR/$guide/complete"

  if [[ ! -d "$SOURCE_DIR" ]]; then
    echo "[$guide] ERROR: $SOURCE_DIR not found"
    exit 1
  fi

  if [[ -d "$BEFORE_DIR" ]]; then
    echo "[$guide] Removing existing before/"
    rm -rf "$BEFORE_DIR"
  fi

  echo "[$guide] Copying complete/ -> before/"
  cp -r "$SOURCE_DIR" "$BEFORE_DIR"
  FILE_COUNT=$(find "$BEFORE_DIR" -type f | wc -l)
  echo "[$guide] $FILE_COUNT files copied"
done

echo ""

# Step 2a: Save reference tests (Spring developers' gold standard)
echo "=== Saving reference tests ==="
for guide in "${GUIDES[@]}"; do
  BEFORE_DIR="$ITEMS_DIR/$guide/before"
  REF_DIR="$ITEMS_DIR/$guide/reference"

  if [[ -d "$REF_DIR" ]]; then
    rm -rf "$REF_DIR"
  fi

  if [[ -d "$BEFORE_DIR/src/test" ]]; then
    mkdir -p "$REF_DIR/src"
    cp -r "$BEFORE_DIR/src/test" "$REF_DIR/src/test"
    REF_COUNT=$(find "$REF_DIR" -name "*.java" -type f | wc -l)
    echo "[$guide] Saved $REF_COUNT reference test files"
  else
    echo "[$guide] WARNING: No src/test/ found — skipping reference save"
  fi
done

echo ""

# Step 2b: Strip tests from before/ (agent writes from scratch)
echo "=== Stripping tests from before/ ==="
for guide in "${GUIDES[@]}"; do
  BEFORE_DIR="$ITEMS_DIR/$guide/before"
  TEST_JAVA_DIR="$BEFORE_DIR/src/test/java"

  if [[ -d "$TEST_JAVA_DIR" ]]; then
    rm -rf "$TEST_JAVA_DIR"
    mkdir -p "$TEST_JAVA_DIR"
    echo "[$guide] Stripped test sources (kept src/test/resources/)"
  else
    echo "[$guide] No src/test/java/ to strip"
  fi
done

echo ""

# Step 3: Optional verification
if [[ "$VERIFY" == true ]]; then
  echo "=== Verifying builds ==="
  for guide in "${GUIDES[@]}"; do
    BEFORE_DIR="$ITEMS_DIR/$guide/before"
    echo "[$guide] Running ./mvnw clean compile..."
    if (cd "$BEFORE_DIR" && ./mvnw clean compile -q); then
      echo "[$guide] BUILD SUCCESS"
    else
      echo "[$guide] BUILD FAILED"
      exit 1
    fi
  done
fi

echo ""
echo "=== Materialization complete ==="
