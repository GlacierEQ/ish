#!/usr/bin/env bash
# =============================================================================
# APEX bootstrap.sh
# iPhone (iSH) → remote host one-time setup
# Run once per fresh iSH install or new remote server.
# =============================================================================
set -euo pipefail

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log()  { echo -e "${BLUE}[APEX]${NC} $*"; }
ok()   { echo -e "${GREEN}[OK]${NC}   $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
die()  { echo -e "${RED}[FAIL]${NC} $*"; exit 1; }

# ---------------------------------------------------------------------------
# 0. Detect environment (iSH local vs. remote Linux)
# ---------------------------------------------------------------------------
if [ -f /proc/ish ]; then
  ENV="ish"
  log "Detected iSH (iPhone local)"
else
  ENV="remote"
  log "Detected remote Linux host"
fi

# ---------------------------------------------------------------------------
# 1. Package dependencies
# ---------------------------------------------------------------------------
install_packages() {
  if command -v apk &>/dev/null; then
    apk add --no-cache tmux openssh-client git curl vim bash coreutils
  elif command -v apt-get &>/dev/null; then
    sudo apt-get update -qq && sudo apt-get install -y tmux openssh-client git curl vim
  elif command -v brew &>/dev/null; then
    brew install tmux git curl vim
  else
    die "No supported package manager found (apk/apt/brew)"
  fi
}

log "Installing packages..."
install_packages
ok "Packages installed"

# ---------------------------------------------------------------------------
# 2. Deploy .tmux.conf
# ---------------------------------------------------------------------------
APEX_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$APEX_DIR/.tmux.conf" ]; then
  cp "$APEX_DIR/.tmux.conf" "$HOME/.tmux.conf"
  ok ".tmux.conf deployed"
else
  warn ".tmux.conf not found in $APEX_DIR — skipping"
fi

# ---------------------------------------------------------------------------
# 3. Deploy SSH config template
# ---------------------------------------------------------------------------
mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"

if [ -f "$APEX_DIR/ssh-config.template" ]; then
  if [ ! -f "$HOME/.ssh/config" ]; then
    cp "$APEX_DIR/ssh-config.template" "$HOME/.ssh/config"
    chmod 600 "$HOME/.ssh/config"
    ok "SSH config deployed — edit $HOME/.ssh/config with your host details"
  else
    warn "$HOME/.ssh/config already exists — not overwriting. Merge $APEX_DIR/ssh-config.template manually."
  fi
fi

# ---------------------------------------------------------------------------
# 4. Make apex-launch.sh executable and symlink to PATH
# ---------------------------------------------------------------------------
if [ -f "$APEX_DIR/apex-launch.sh" ]; then
  chmod +x "$APEX_DIR/apex-launch.sh"
  # Try to symlink into a directory on PATH
  for BIN_DIR in "$HOME/.local/bin" "/usr/local/bin" "/usr/bin"; do
    if [ -d "$BIN_DIR" ] && [ -w "$BIN_DIR" ]; then
      ln -sf "$APEX_DIR/apex-launch.sh" "$BIN_DIR/apex"
      ok "apex command linked → $BIN_DIR/apex"
      break
    fi
  done
  # Ensure ~/.local/bin exists and is on PATH
  mkdir -p "$HOME/.local/bin"
  grep -qxF 'export PATH="$HOME/.local/bin:$PATH"' "$HOME/.profile" 2>/dev/null ||
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.profile"
fi

# ---------------------------------------------------------------------------
# 5. iSH-specific: minimal prompt setup
# ---------------------------------------------------------------------------
if [ "$ENV" = "ish" ]; then
  PROFILE="$HOME/.profile"
  if ! grep -q 'APEX minimal prompt' "$PROFILE" 2>/dev/null; then
    cat >> "$PROFILE" <<'PROFILE_BLOCK'
# APEX minimal prompt (iSH)
export PS1='$(pwd | sed "s|$HOME|~|") $ '
export HISTSIZE=5000
export HISTFILESIZE=10000
alias ll='ls -lah'
alias gs='git status -sb'
alias gd='git diff --stat'
alias gl='git log --oneline -10'
alias v='vim'
alias apex='~/.local/bin/apex'
PROFILE_BLOCK
    ok "Minimal iSH profile written to $PROFILE"
  else
    warn "APEX profile block already present in $PROFILE"
  fi
fi

# ---------------------------------------------------------------------------
# 6. Done
# ---------------------------------------------------------------------------
echo ""
log "=== APEX bootstrap complete ==="
echo ""
echo "  Next steps:"
echo "  1. Edit ~/.ssh/config with your remote host details"
echo "  2. Copy your private key to ~/.ssh/ (chmod 600)"
echo "  3. Run: apex       (launches tmux + SSH session)"
echo "  4. On remote: cd into your repo and run: codex"
echo ""
