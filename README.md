# aivideoediting

**Start with `WALKTHROUGH.md`: exact copy-paste steps for the MacBook.**

`premiere-edit/` is a Claude Code skill that edits a talking-head video and hands back an **editable Premiere Pro
sequence** (not a flat mp4). It's a fork of the CapCut version, rebuilt for Premiere.

## When you get home (about 25 minutes, all copy-paste)

Open **Terminal** on the MacBook, one block at a time.

**1. Install the skill**
```bash
cd ~ && git clone https://github.com/adamgins516-stack/aivideoediting.git
mkdir -p ~/.claude/skills && cp -r ~/aivideoediting/premiere-edit ~/.claude/skills/
```

**2. Check what's missing** (installs nothing, just tells you)
```bash
bash ~/.claude/skills/premiere-edit/scripts/setup_check.sh
```
It prints a `fix:` line under anything missing. Copy-paste those. Typical set:
```bash
brew install ffmpeg pipx
pipx ensurepath && pipx install mlx-whisper
pip3 install --break-system-packages pillow numpy opencv-python-headless
xcode-select --install
brew install --cask visual-studio-code
code --install-extension Adobe.extendscript-debug
```
Run the check again until it says **All set** (the two `.mogrt` lines will stay red until step 3).

**3. Build the caption template (once, ~10 min in Premiere)**
Follow `premiere-edit/references/mogrt-caption-template.md`. Save `Caption.mogrt` and `Blurb.mogrt` into
`~/Documents/premiere-edit/`.

**4. Bring footage**
Put your raw take in a folder, open Claude Code in that folder, and say:
```
Use the premiere-edit skill. Here's my raw take. Edit it into a Premiere sequence.
```
Claude will ask a few questions (raw or pre-cut, the feel you want, behind or in front of your head, 4K export if you
have one). Examples of videos you like help a lot.

## What's here

- `premiere-edit/SKILL.md` — the instructions Claude follows
- `premiere-edit/sounds/` — 16 generated sound effects (audition them, swap any you don't like)
- `premiere-edit/scripts/` — cutting, transcription, rendering, sound, and the Premiere sequence builder
- `premiere-edit/references/` — safe zones, caption/card styles, looks, motion, sound, lessons

## Honest status

- Built and unit-checked on Linux: the sound pack, the cut/transcribe/render code (carried over), the XML writer
  (well-formed, track layout and zoom keyframes verified from a synthetic project), the caption script (syntax-checked).
- **Not yet run against Premiere.** The first XML import and the first caption-script run are checkpoints; expect to fix
  small things together at the laptop (`references/premiere-import.md`, "Known unknowns").
- Generated sound effects can sound thin on a phone speaker. Audition first; real samples override them.
