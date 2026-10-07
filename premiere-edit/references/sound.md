# Sound — the skill's own pack, plus three rules

The user chose to have the skill make its own sound effects. `scripts/make_sounds.py` writes a deterministic pack into
`sounds/` (pop, pop2, click, tap, tick, whoosh, whoosh2, bell, low, ding, static, bass, sparkle, riser, hit, typing).

**Be honest about the limit.** Synthesized effects can read as cheap on a phone speaker; an earlier creator rejected two
rounds of them as "hard on the ears". So:

## Rule 1 — audition by ear, swap what's weak

- Always run `make.py audition` and let the user pick by number before the final mix.
- Any real sample beats a generated one. If the user has (or finds) a sound they like, drop it into `work/assets/` as
  `sfx_<role>.wav` and `example_make.py` uses it instead of the pack. Royalty-free packs and the user's own recordings
  (a real keyboard, a real mouse click, a real door) work great.
- Load with `snd_file(path)` (any sample rate, mono-summed, peak-normalised, optional trim/fade) and map roles with `SND`.
- A short "typing" recording is sliced into single keystrokes (`slice_transients`) and re-sequenced per character; the
  pack's `sfx_typing.wav` is built for this.

## Rule 2 — what sounds on what

- **A picture of the person appears** (their own reels as phone cards, a frame of their take in a before/after): a **pop**.
- **A recording of a computer screen appears** (an editor timeline, an app window, a player window, a web card, a comments
  box): a **click**. Not a pop.
- **Typed text** (a slash command, a comment being typed): a keyboard sound, one keystroke per character, from a real
  typing recording (slice and sequence it; never a tick per letter from a click sound).
- **A look switch**: one soft sound (a short bell for a warm look, a low swell for a moody one). One, not two. Nothing
  on the title that follows it.
- **Word pops** keep a pop. **A warning word** ("wrong") gets one low hit.
- **Caption changes**: a tick is what the research shows winners doing, but creators hear it as noise on their own voice.
  Render the ticks to their own wav (`06_*_caption-ticks.wav`), put it on its own track in the project, and leave it OUT
  of the flattened mp4. The user can turn it on.

## Rule 3 — levels

Peak-normalise every sample, then gain 0.16–0.55 per role before the 0.4 master scale: that puts effects about 20 dB
under the voice. The mix's own peak should land around −13 dBFS; the finished file with voice around −4 dBFS peak.

## What the research says (21 top editing-style reels, 2026-10)

Every performing talking-head reel has a continuous music bed and something audible every 0.6–1.3 s: a soft tick on
caption swaps, a pop per sticker, a whoosh on a card or section change. Big hits are saved for frame 0, section switches
and the CTA. Sticker sounds sit under the voice; only transitions sit at voice level. The music bed is the user's call
(they add it in Premiere from a licensed library); the skill never ships music.

## Audition reel and sound-only remix

- `make.py audition` writes `SOUND_AUDITION.mp4`: every candidate plays twice with its name on screen, under a minute.
  The user picks by ear and names a number.
- `make.py sound` re-mixes the effects track onto the EXISTING picture (`-c:v copy`) in a couple of seconds and overwrites
  the linked `05_00.00s_SFX.wav` in `premiere_layers/` (Premiere reads linked media in place: save, close and reopen the
  project, or Link Media, to pick up the new file). A sound swap never re-renders a frame.
