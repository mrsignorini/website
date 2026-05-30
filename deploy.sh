#!/usr/bin/env sh
set -eu

PUBLISH_BRANCH="${PUBLISH_BRANCH:-gh-pages}"
HUGO_BIN="${HUGO_BIN:-hugo}"
WORKTREE_DIR="${WORKTREE_DIR:-$(mktemp -d "${TMPDIR:-/tmp}/sig-gh-pages.XXXXXX")}"

cleanup() {
  git worktree remove --force "$WORKTREE_DIR" >/dev/null 2>&1 || true
  rm -rf "$WORKTREE_DIR"
}

prepare_worktree() {
  if git show-ref --verify --quiet "refs/heads/$PUBLISH_BRANCH"; then
    git worktree add "$WORKTREE_DIR" "$PUBLISH_BRANCH"
    return
  fi

  if git show-ref --verify --quiet "refs/remotes/origin/$PUBLISH_BRANCH"; then
    git worktree add -B "$PUBLISH_BRANCH" "$WORKTREE_DIR" "origin/$PUBLISH_BRANCH"
    return
  fi

  git worktree add --detach "$WORKTREE_DIR" HEAD
  (
    cd "$WORKTREE_DIR"
    git checkout --orphan "$PUBLISH_BRANCH"
  )
}

clear_worktree() {
  find "$WORKTREE_DIR" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
}

if ! command -v "$HUGO_BIN" >/dev/null 2>&1; then
  echo "Unable to find '$HUGO_BIN' in PATH."
  exit 1
fi

trap cleanup EXIT INT TERM

echo "Preparing $PUBLISH_BRANCH worktree"
prepare_worktree

echo "Cleaning published files"
clear_worktree

echo "Generating site"
"$HUGO_BIN" --config config.toml --destination "$WORKTREE_DIR" --minify

touch "$WORKTREE_DIR/.nojekyll"

if [ -f CNAME ]; then
  cp CNAME "$WORKTREE_DIR/CNAME"
fi

echo "Committing published files"
(
  cd "$WORKTREE_DIR"
  git add --all

  if git diff --cached --quiet; then
    echo "No changes to publish."
    exit 0
  fi

  git commit -m "Publish $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  git push origin "$PUBLISH_BRANCH"
)
