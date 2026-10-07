#!/usr/bin/env bash
# setup_check.sh — checks everything premiere-edit needs and prints the exact command for anything missing.
# It installs NOTHING. Run:  bash ~/.claude/skills/premiere-edit/scripts/setup_check.sh
ok(){ printf "  [ok]      %s\n" "$1"; }; miss(){ printf "  [MISSING] %s\n            fix:  %s\n" "$1" "$2"; MISSING=1; }
MISSING=0; SKILL="$(cd "$(dirname "$0")/.." && pwd)"
echo "premiere-edit setup check  ($SKILL)"
[ "$(uname)" = "Darwin" ] && ok "macOS" || miss "macOS (the person-mask tool is Mac-only; the rest works anywhere)" "n/a"
command -v brew >/dev/null && ok "Homebrew" || miss "Homebrew" '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
command -v ffmpeg >/dev/null && ok "ffmpeg" || miss "ffmpeg" "brew install ffmpeg"
command -v python3 >/dev/null && ok "python3 ($(python3 --version 2>&1))" || miss "python3" "brew install python"
for m in PIL numpy cv2; do python3 -c "import $m" 2>/dev/null && ok "python module $m" || miss "python module $m" "pip3 install --break-system-packages pillow numpy opencv-python-headless"; done
if command -v mlx_whisper >/dev/null || [ -x "$HOME/.local/bin/mlx_whisper" ]; then ok "speech-to-text: mlx-whisper"
elif python3 -c "import faster_whisper" 2>/dev/null; then ok "speech-to-text: faster-whisper"
elif python3 -c "import whisper" 2>/dev/null; then ok "speech-to-text: openai-whisper"
else miss "a speech-to-text engine" "brew install pipx && pipx ensurepath && pipx install mlx-whisper    (Apple Silicon)"; fi
command -v swiftc >/dev/null && ok "swiftc (Xcode command-line tools)" || miss "Xcode command-line tools (person masks)" "xcode-select --install"
if command -v code >/dev/null; then
  code --list-extensions 2>/dev/null | grep -qi "extendscript" && ok "VS Code + ExtendScript Debugger extension" || miss "VS Code ExtendScript Debugger extension" "code --install-extension Adobe.extendscript-debug"
else miss "VS Code (runs the caption script against Premiere)" "brew install --cask visual-studio-code   then   code --install-extension Adobe.extendscript-debug"; fi
ls /Applications 2>/dev/null | grep -qi "Adobe Premiere Pro" && ok "Adobe Premiere Pro ($(ls /Applications | grep -i 'Adobe Premiere Pro' | head -1))" || miss "Adobe Premiere Pro in /Applications" "install from Creative Cloud (current release, not beta)"
[ -f "$HOME/Documents/premiere-edit/Caption.mogrt" ] && ok "Caption.mogrt" || miss "Caption.mogrt (one-time, in Premiere)" "follow $SKILL/references/mogrt-caption-template.md"
[ -f "$HOME/Documents/premiere-edit/Blurb.mogrt" ] && ok "Blurb.mogrt" || miss "Blurb.mogrt (one-time, in Premiere)" "follow $SKILL/references/mogrt-caption-template.md"
[ -f "$SKILL/sounds/sfx_pop.wav" ] && ok "sound pack" || miss "sound pack" "python3 $SKILL/scripts/make_sounds.py"
[ $MISSING = 0 ] && echo "All set." || echo "Run the fix lines above, then run this again."
