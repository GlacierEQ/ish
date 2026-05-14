# APEX — iPhone → tmux → SSH → Codex Stack

> **Case:** `1FDV-23-0001009` | **Branch:** `apex-config` | **Operator:** GlacierEQ

This branch holds the complete APEX configuration layer — optimized for driving OpenAI Codex CLI from an iPhone via iSH, through a persistent tmux session, over SSH to a remote Linux host. All files in `apex/` are self-contained; they do not touch upstream iSH source files and can be rebased onto any future iSH upstream cleanly.

---

## Architecture

```
 iPhone (iSH)
   └─ tmux (APEX session)
        ├─ window 1: codex   ← SSH -t → remote host → codex CLI
        ├─ window 2: shell   ← SSH   → remote host → bash/zsh
        └─ window 3: monitor ← SSH -t → remote host → htop
```

**Why this layout:**
- tmux survives cellular drops — reconnect with `apex` and every window is intact
- Three dedicated windows prevent context-switching overhead on a small screen
- The Codex window auto-starts `codex` on SSH connect; the shell window is for git/file ops
- Monitor window keeps an eye on CPU/memory during long Codex inference jobs

---

## Files in this branch

| Path | Purpose |
|------|---------|
| `apex/bootstrap.sh` | One-time setup: installs packages, deploys configs, symlinks `apex` command |
| `apex/.tmux.conf` | tmux config: Ctrl-a prefix, mouse, vi keys, APEX color scheme, 3-window layout |
| `apex/apex-launch.sh` | Launch/reattach APEX session; creates the 3-window SSH layout |
| `apex/ssh-config.template` | SSH config with ControlMaster, keepalive, compression — copy to `~/.ssh/config` |
| `APEX-README.md` | This file |
| `prompts/codex-apex.md` | Standing Codex system prompt seeded for case `1FDV-23-0001009` |

---

## Quick Start

### 1. On iPhone (iSH)

```bash
# Install git if not already present
apk add git

# Clone your fork
git clone https://github.com/GlacierEQ/ish.git ~/ish
cd ~/ish
git checkout apex-config

# Run bootstrap (installs tmux, openssh, deploys configs)
bash apex/bootstrap.sh
```

### 2. Configure SSH

```bash
# Generate a dedicated key for APEX
ssh-keygen -t ed25519 -f ~/.ssh/apex_ed25519 -C "apex-ish"

# Edit the deployed SSH config with your server details
vi ~/.ssh/config
# Fill in: HostName, User

# Copy the public key to your remote host
cat ~/.ssh/apex_ed25519.pub
# → paste into ~/.ssh/authorized_keys on remote host
```

### 3. Launch

```bash
apex
# or
apex codex-host
```

This creates (or reattaches to) the APEX tmux session with all three windows.

### 4. On the remote host

```bash
# Install Codex CLI (Node 22+ required)
npm install -g @openai/codex

# Set your key
export OPENAI_API_KEY=sk-...

# Run with the APEX system prompt
codex --system-prompt "$(cat ~/ish/prompts/codex-apex.md)"
```

---

## iPhone-Specific Tips

- **Landscape mode** — more horizontal terminal space; critical for diffs and Codex output
- **External keyboard** — Full Keyboard Access in iOS Settings → Accessibility for full tmux keybinding support
- **Minimal prompt** — bootstrap.sh writes a stripped PS1 to `~/.profile`; keeps screen clean
- **Reconnect pattern** — cellular drops are common; just run `apex` again to reattach instantly
- **Ctrl-a shortcuts** — the tmux prefix is Ctrl-a (not Ctrl-b); easier to reach on iPhone external keyboards

### Key tmux shortcuts

| Action | Keys |
|--------|------|
| New window | `Ctrl-a c` |
| Switch window | `Ctrl-a 1/2/3` |
| Split horizontal | `Ctrl-a \|` |
| Split vertical | `Ctrl-a -` |
| Navigate panes | `Ctrl-a h/j/k/l` |
| Detach session | `Ctrl-a d` |
| Reload config | `Ctrl-a r` |
| Copy mode | `Ctrl-a Enter` |

---

## Branch Strategy

This branch (`apex-config`) contains **only** the `apex/`, `prompts/`, and `APEX-README.md` files. It does not modify any upstream iSH C source, build scripts, or iOS-specific files.

**To pull upstream iSH patches without conflicts:**

```bash
git checkout master
git fetch upstream
git merge upstream/master
git checkout apex-config
git rebase master
# apex/ and prompts/ files will reapply cleanly on top
```

**To tag a stable APEX config point:**

```bash
git tag -a apex-v1.0 -m "APEX iPhone Codex stack v1.0 — case 1FDV-23-0001009"
git push origin apex-v1.0
```

---

## Case Context

Case `1FDV-23-0001009` — Hawaii Family Court. The Codex system prompt in `prompts/codex-apex.md` seeds all Codex sessions with relevant statutes, case posture, and APEX operational context. All Codex output should be treated as attorney-review-required draft material, not legal advice.
