#!/usr/bin/env bash
# Checks the local development environment for the Praktikum course (week 1).
# Usage: bash check_env.sh

passed=0; failed=0
ok()   { echo "OK    $1"; passed=$((passed+1)); }
fail() { echo "FAIL  $1"; failed=$((failed+1)); }

echo "== System =="
if grep -qi microsoft /proc/version 2>/dev/null; then ok "WSL ($(uname -r))"
else ok "$(uname -s) $(uname -r)"; fi

echo "== Git =="
if command -v git >/dev/null; then ok "$(git --version)"; else fail "git is not installed"; fi
[ -n "$(git config --global user.name)" ]  && ok "user.name = $(git config --global user.name)"   || fail "git user.name is not set"
[ -n "$(git config --global user.email)" ] && ok "user.email = $(git config --global user.email)" || fail "git user.email is not set"

echo "== GitHub CLI =="
if command -v gh >/dev/null; then
  ok "$(gh --version | head -1)"
  if gh auth status >/dev/null 2>&1; then ok "logged in as $(gh api user -q .login)"; else fail "gh is not logged in (run: gh auth login)"; fi
else fail "gh is not installed"; fi

echo "== Python =="
if command -v python3 >/dev/null; then
  py_version=$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')
  python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)' && ok "Python $py_version" || fail "Python $py_version (3.10+ required)"
else fail "python3 is not installed"; fi
if [ -n "$VIRTUAL_ENV" ]; then ok "active venv: $VIRTUAL_ENV"; else fail "no active venv (run: source .venv/bin/activate)"; fi
[ -f requirements.txt ] && ok "requirements.txt exists" || fail "requirements.txt is missing"

echo "== Repository =="
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  ok "git repository: $(git remote get-url origin 2>/dev/null || echo 'no remote')"
  grep -qx '.venv/' .gitignore 2>/dev/null && ok ".venv/ is in .gitignore" || fail ".venv/ is not in .gitignore"
  grep -qx '.env'   .gitignore 2>/dev/null && ok ".env is in .gitignore"   || fail ".env is not in .gitignore"
else fail "current directory is not a git repository"; fi

echo
echo "Result: $passed OK, $failed FAILED"
[ "$failed" -eq 0 ]