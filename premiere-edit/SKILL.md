---
name: premiere-edit
description: >
  Turn a raw talking-head take (or a cut already made in Premiere Pro) into a fully EDITED, fully EDITABLE Premiere Pro
  sequence: word-synced captions with one highlighted keyword placed inside the platform's safe zones (as editable
  Motion Graphics template clips), big word pops, real app cards in front of and BEHIND the person, two switchable
  restrained aesthetics ("soft & warm" and "moody") that the viewer watches ramp in, the breathing-camera zooms that
  winning talking heads use, a flicker open, the person's own videos orbiting their head, sound effects from the skill's
  own pack, all as separate clips so every piece can still be changed inside Premiere. Use whenever someone says "edit
  this video", "edit my video in Premiere", "make this look like [aesthetic]", "add captions and graphics", "turn my raw
  footage into a Premiere project", or hands you a take and a description of the edit they want. macOS, Premiere Pro
  (current release), ffmpeg, Python 3.
---

# premiere-edit — Claude edits your video, and you can still edit it after

The thing most "Claude video editor" setups get wrong: they hand you back a flat mp4. One typo, one wrong sound, and
you're re-prompting. This skill never renders a flat file as the deliverable. It writes a **Premiere sequence** (Final
Cut Pro 7 XML, which Premiere imports natively) where the take is one clip per cut, every graphic is its own alpha clip,
the zooms are Scale keyframes, the sound effects sit on their own track, and every caption is an **editable Motion
Graphics template clip** that a script fills in from the transcript.

Forked from `capcut-edit`. The rendering half is unchanged; the project writer is new (`scripts/build_xmeml.py`).
**The XML import and `place_captions.jsx` have not yet run inside Premiere**: the first import is a checkpoint
(`references/premiere-import.md`, "Known unknowns").

Read `references/premiere-import.md` and `references/mogrt-caption-template.md` before building, `references/safe-zones.md`
and `references/captions-and-cards.md` before placing anything, `references/looks.md` for the aesthetics,
`references/motion.md` for zooms and the flicker, `references/sound.md` before touching sound,
`references/style-from-examples.md` when the user gives example videos, `references/lessons.md` for everything that went wrong once.

## Intake — ask these things, every time

1. **Raw or pre-cut?** Raw take (one long recording with bad takes) → this skill cuts it (`cutplan.py silence`). Already
   cut in Premiere → they export the cut (H.264, 1080x1920 or 4K) and you run `cutplan.py whole`. Don't guess; ask.
2. **What should it feel like?** Examples beat adjectives. If they hand you 5–10 of their own videos, or a few from a
   creator they love, study them frame by frame first and write the style down (`references/style-from-examples.md`).
   If they only name an aesthetic, confirm which reading they mean with one line each (see `looks.md`), then go.
3. **A 4K export of the same cut**, if they have one: zooms cropped from 4K stay sharp at 1080 (`motion.md`).
4. **Sounds.** The skill's generated pack is the default (`sound.md`). Audition by ear (`make.py audition`) and swap any
   weak one for a real sample the user drops in `work/assets/sfx_<role>.wav`.
5. **A 10-second screen recording of their Premiere timeline**, when the script shows "the editor". It becomes a real
   card; scripted clicking into Premiere is blocked on macOS.
6. **Behind or in front?** Creators who film with headroom usually want cards behind their head. Ask once, then it's a
   rule for them: and when it's behind them, it's fully behind them (no see-through).
7. **Caption templates exist?** `~/Documents/premiere-edit/Caption.mogrt` and `Blurb.mogrt`. If not, walk them through
   `mogrt-caption-template.md` first (10 minutes, once).

Everything else (what to show when, which words to highlight) you decide from the transcript. Don't ask about it.

## The pipeline

Work in a scratch folder next to the footage (`<video>-edit/work/`). Deliver to `<video>-edit/`.
First run on a Mac: `bash scripts/setup_check.sh` (it checks and tells you what to install; nothing installs silently).

1. **Cut.** Raw: `python3 scripts/cutplan.py silence raw.mp4 --out cut.mp4` (audio-envelope pause trim: handles of a
   few frames, pauses shortened to ~0.12 s; no dead air between lines). Pre-cut export: `python3 scripts/cutplan.py whole
   their_cut.mp4 --out cut.mp4`. For a raw take with repeated lines, read `words.txt` and keep the LAST take of each
   line (`--keep keep.json`). A 4K export of the same cut goes in as `work/take_4k.mp4` + `work/frames4k/` (verify it's
   the same cut: PSNR > 35 dB).
2. **Time the words.** `python3 scripts/transcribe.py cut.mp4 words/` → `words/words.txt` (`  6.40 three`). Every
   placement comes from these times. People's own estimates of when they say something run 1–2 s early.
3. **Frames + masks.** `ffmpeg -i cut.mp4 -q:v 2 frames/%05d.jpg`. Masks are needed for anything behind the person and
   for the flicker: `swiftc -O scripts/segbatch.swift -o segbatch && ./segbatch frames masks` (macOS Vision, ~1 min per
   1,300 frames). The flicker also needs an empty-room plate: 2 s of the empty room filmed from the same spot, or
   `python3 scripts/plate.py work` (median of mask-free pixels; the chair centre ends up inpainted, say so).
4. **Look at the footage first.** Contact sheet (`fps=1/2,scale=270:-1,tile=8x6`), then Read it. Find where the head
   top is, where hands come up, how much headroom there is. Everything below depends on that.
5. **Sounds.** `python3 scripts/make_sounds.py` (once; the pack lives in `sounds/`). Pick by role (`sound.md`: pop = a
   picture of them appears, click = computer-screen footage, typing = a typing recording sliced per keystroke, one bell
   per look switch). Real samples in `work/assets/sfx_<role>.wav` override the pack.
6. **Plan the asset table before writing code.** One row per graphic: name · the word it lands on · in · out · builder ·
   sound · layer (text / front / back). Then write `make.py` from `scripts/example_make.py` on top of `scripts/render.py`.
   Motion too: 3–6 breathing pushes (1.08–1.15× in over ~1.5 s, hold, out), 2–3 hard punches on joke/warning words, a slow
   creep across the moody look (`motion.md`).
7. **Check before rendering.** `python3 make.py check` renders composite frames at the beats into one sheet with the
   platform's no-go zones tinted red. Read it. Fix anything touching a red zone, cards over the face, two things in the
   headroom at once, a back card showing through hair. Repeat.
8. **Render.** `python3 make.py preview` (the finished mp4, zooms cropped from 4K when present, effects mixed; caption
   ticks left out) and `python3 make.py layers` (take pieces with grades/flicker baked, premultiplied ProRes 4444 alpha
   clips for back and front, the SFX wavs (mono), `meta.json` with the eased zoom keys and caption cues).
9. **Build the sequence.** `python3 scripts/build_xmeml.py <premiere_layers dir> "<Sequence name>"` → `<name>.xml` +
   `place_captions.jsx`. In Premiere: File > Import the `.xml`, open the sequence, then run `place_captions.jsx`
   (`premiere-import.md`) for the editable captions and blurb. Never import over a project the user is working in:
   make a new project or a new bin.
10. **Iterate cheaply.** A sound swap is `make.py sound` (2 s, picture untouched; reopen the project to relink the wav).
    A blurb or opening change is `make.py head` (30 s). Only a visual change elsewhere needs a full render.
11. **README.** Write `README.txt` with the placement table (time, file, what happens on which word), the zooms, the
    looks, what's baked vs. editable, what was left out.
12. **Post it and look.** Ask for a phone screen recording of the posted video. If their phone's UI differs from the
    measured zones in `safe-zones.md`, re-measure once (10 minutes) and make the numbers theirs.

## Rules that make the edit good (defaults; a reference video overrides them)

- **Frame zero is the person + one line of text** (or the text popping in). The blurb is centred between the platform's
  top tabs and the head, not as high as it can go. A visual that supports the hook can pop in from ~1 s and can be big.
- **Nothing but footage in the platform's zones:** the top band (y<260), the right icon column (x>880 below y 930), the
  bottom block (y>1690), and 40 px off each side. Measured, not guessed (`safe-zones.md`).
- **Captions on every line, 2–4 words per cue, one keyword per cue in the highlight colour, ≤720 px wide, centred at
  x=500.** Cues come from the transcript, phrase by phrase, and never run into a section that speaks through its own
  typography.
- **Big single-word pops above the head** on the words that carry the line, auto-fit to the safe width. Never while a
  card already owns the headroom.
- **Cards look real** (the app, a Finder window, a code editor, a player window, a comments card, THEIR screen recording
  of the editor) with a soft shadow and a slight tilt. No clip-art, no mascots, no mock UI with invented numbers, and no
  drawn timeline when a real recording is one ask away.
- **The sandwich.** Pictures of the person and app cards go behind the head; word pops, serif words, the opening proof
  card (on the chest) and the paywall (headroom) go in front. Occlusion is binary: the cutout at full opacity, never a
  dimmed or soft-edged back card.
- **A look is not an overlay.** When the script names an aesthetic, re-grade the FOOTAGE itself (take and cutout, same
  function, same noise seed), restrained, and let its strength RAMP across the phrase so the viewer watches it happen.
  On at the word that names it, off at the first word of the next idea. One soft sound on the switch, not two.
- **The camera breathes.** Winning talking heads spend ~25% of the runtime in slow push-and-release zooms; hard punches
  are rarer and land on a joke or warning word with a treatment (two black-and-white frames). Keyframes, never baked.
- **Sound lands on the verb, from the editor's library.** Pop when a picture of them appears, click when a computer
  screen appears, a real typing recording when text is typed, a bell on a warm switch, a low swell on a moody one. About
  20 dB under the voice. Caption ticks on their own muted track. The music bed is theirs to add.
- **Nothing lingers past the next spoken beat.** Pop-ins 0.3 s, fades out 0.2–0.3 s.
- **Truth.** A number or a name on screen comes from somewhere real (the user's own stats, the actual file name, the
  actual folder, their real covers and view counts). If you don't have it, don't invent it; draw the card without it.

## What you deliver

`<video>-edit/` with `FINAL.mp4` (the flat preview), `SOUND_AUDITION.mp4` when sounds were chosen, `premiere_layers/`
(every clip, named `NN_<start>s_<what>`; keep it, the sequence links to it), `<name>.xml`, `place_captions.jsx`, and
`README.txt`. In the sequence: `take` · `back1..n` · `cutout` · `front1..n` · `captions` + `blurb` (template clips) ·
audio: voice, `sfx`, `caption ticks` (disabled). Tell the user: import the XML, run the caption script, add a music bed,
export from Premiere.
