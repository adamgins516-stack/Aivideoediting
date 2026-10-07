# Lessons — everything that went wrong once

## Rendering
- **Straight alpha = halo.** Premiere treats the ProRes 4444 as straight unless told otherwise, so the layers are premultiplied and the XML says `alphatype straight` — if you ever see dark fringes, right-click the clip > Modify > Interpret Footage > Alpha Channel: Premultiplied. Multiply RGB by alpha before encoding every
  sticker and the cutout (`render.premul`). ffmpeg's `overlay` composites straight alpha, so the preview never shows it.
- **`-shortest` drops a frame.** Trimmed AAC is a hair shorter than n/30 s; 14 of 23 take pieces came back one frame
  short and the whole timeline ended 0.47 s early. Use `-af apad -t <n/fps>`.
- **Tile the take by frame counts**, not by the 10 ms-rounded start in a file name. a rounded name can be a frame off and open a gap or an overlap on the take track.
- **Drawing with alpha 0 on a filled card punches a hole.** PIL draws, it doesn't blend; `eob(0)` is 2e-16 not 0, so
  `if p <= 0:` guards fail. Guard pops with `<= 0.01`. Symptom: a dark word showing through a white card.
- **`alpha_composite` refuses negative destinations.** Clamp with `max(0, …)` when a rotated prop can poke above a card.
- **A glow colour needs an alpha channel.** `Region.glow(..., col=(40, 26, 10))` crashes inside `A()`; pass 4-tuples.
- **Placing a full-frame image "at a point" moves it off screen.** `classic_box` returns a full 1080×1920 layer; crop to
  `getbbox()` before `place()`-ing it with a scale (the popping blurb was invisible for one render because of this).
- **A sound-only or opening-only change must not re-render the video.** `make.py sound` remuxes with `-c:v copy` (2 s);
  `make.py head` re-renders only the frames up to the blurb's end and concatenates (30 s). A full render is 3 min for 44 s.
- **Zoom from the 4K export.** A 1.2× punch cropped from 1080 goes soft; the same cut exported at 4K is identical (check
  with a PSNR compare, >35 dB) and keeps the zooms sharp.

## Measuring instead of guessing
- **Scene-change detection cannot see a slow zoom.** The first research pass concluded winners "barely punch in". Register
  the background between frames (top third, homography) to measure zooms; face size alone is fooled by leaning in.
- **Colour matching finds a flat wall at any zoom.** Fit a plate or a frame on edges (Sobel + normalised correlation).
- **Measure the platform UI from a phone screen recording**, by template-matching a rendered frame into it. "Top 10% is a
  red zone" was a guess; the real zones are in `safe-zones.md` and the save button sat exactly where the captions were.
- **The user's time estimates run early** ("around 5 seconds" was 6.4). Place on `words.txt`, never on the script.

## Taste calls that are now rules
- **Reference beats adjectives.** Ask for a link before designing. The first "cool girl / dark" edit built from the words
  was a scrapbook of hand-drawn hearts; the reference wanted captions + yellow keyword, word pops, real app cards.
- **Restrained looks.** Halve every departure from the base grade (see `looks.md`).
- **If it's behind them, it's behind them.** No dimmed or soft-edged back cards; full-opacity cutout.
- **Cards go behind by default** when the person films with headroom; the opening proof card and the paywall go in front.
- **Real screen footage** for an editor-timeline card, never a drawing; ask for a screen recording.
- **Sounds:** pop for pictures of the person, click only for computer-screen footage, one bell per look switch, typing =
  sliced single keystrokes. This skill ships its own generated pack (`sound.md`); synthesized sounds were once called
  "hard on the ears" by a creator, so audition by ear and swap anything weak for a real sample.
- **Captions ≤ 720 px wide, centred at x=500**; pops and serif words auto-fit. Blurb centred under the top tabs.

## Premiere and the XML import
- **Nothing here has been tested inside Premiere yet** (the skill was written on Linux). First import on the Mac is a
  checkpoint: open the sequence, scrub it, and fix `build_xmeml.py` for whatever differs. Likely candidates: keyframe
  `when` offsets, interpolation, which track the mono audio lands on.
- **A keyframe at a clip's end time belongs to the next clip.** Otherwise a push-in's start key lands on the previous
  piece and the section holds at the peak the whole way.
- **4K media in a 1080x1920 sequence imports at 100% scale, i.e. cropped.** The builder sets a 50% base scale on 2160-wide
  files; the zoom keys multiply it. Check the first piece fills the frame.
- **The XML points at your layers folder.** Move or delete it and Premiere asks to relink. Keep it until the project is
  final, then Project > Consolidate Duplicate Clips / File > Project Manager if you want a self-contained copy.
- **The caption script depends on the template's parameter names** (`Line`, `Keyword`, `Text`). A wrong name is logged with
  the list of names the template does have; fix `P_LINE` / `P_KEY` at the top of `place_captions.jsx`.
- **Scripted clicking into Premiere needs accessibility permission** for the terminal. Don't fight it: ask for a screen recording.
- **The screen-recording file name has a narrow no-break space** before AM/PM. Find it with `find … -name "Screen Recording 2026*"`
  and `-exec cp`, never by typing the path.

## Working with the person
- **Cards in front vs. behind the head** is their call; ask once, then make it a rule for that creator.
- **Two sessions, one folder.** Before touching an edit folder, `stat` the make files; if something changed in the last
  hour that you didn't do, stop and ask.
- **Instagram/TikTok cover URLs expire** within hours. Download real covers the moment you find them; a thumbnail can be a
  bad frame (a ceiling), so grab a frame from the video itself if it is.
- **Disk space.** Frames + masks + a 4K copy + layers is ~3 GB per edit. After the project is
  confirmed good, delete frames/masks and keep the layers folder (the sequence links to it), keep frames only
  while visual tweaks are still coming.
