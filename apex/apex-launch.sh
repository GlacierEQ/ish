#!/usr/bin/env bash
# =============================================================================
# APEX apex-launch.sh
# Launch or reattach the canonical APEX tmux session with SSH to Codex host.
# Usage: apex [host-alias]   (default host: codex-host from SSH config)
# =============================================================================
set -euo pipefail

SESSION="APEX"
DEFAULT_HOST="codex-host"       # Must match Host entry in ~/.ssh/config
REMOTE_REPO_PATH="~/repo"       # Path to project repo on remote host
CODEX_CMD="codex"               # Command to start Codex on remote

HOST="${1:-$DEFAULT_HOST}"

# ---------------------------------------------------------------------------
# If session already exists — reattach
# ---------------------------------------------------------------------------
if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "[APEX] Reattaching to existing session: $SESSION"
  exec tmux attach-session -t "$SESSION"
fi

# ---------------------------------------------------------------------------
# Create new detached session with window layout
# ---------------------------------------------------------------------------
echo "[APEX] Starting session: $SESSION → $HOST"

# Window 1: codex — SSH + auto-start Codex
tmux new-session -d -s "$SESSION" -n "codex" \
  "ssh -t $HOST 'cd $REMOTE_REPO_PATH && $CODEX_CMD || bash'"

# Window 2: shell — SSH interactive shell
tmux new-window -t "$SESSION" -n "shell" \
  "ssh $HOST"

# Window 3: monitor — SSH + htop
tmux new-window -t "$SESSION" -n "monitor" \
  "ssh -t $HOST 'htop || top'"

# Focus window 1 (codex)
tmux select-window -t "$SESSION:1"

# ---------------------------------------------------------------------------
# Attach
# ---------------------------------------------------------------------------
exec tmux attach-session -t "$SESSION"
