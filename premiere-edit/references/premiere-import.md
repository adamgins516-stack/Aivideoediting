# Getting the layers into Premiere

`scripts/build_xmeml.py <premiere_layers> "<Sequence name>"` writes two files next to the layers folder:

- `<Sequence name>.xml`: a Final Cut Pro 7 XML (xmeml v4) sequence. In Premiere: **File > Import**, pick the `.xml`, then
  open the new sequence from the Project panel. 1080 x 1920, 30 fps.
- `place_captions.jsx`: fills the sequence with editable captions (below).

## Track layout (bottom to top)

| Video | contents |
|---|---|
| V1 | `take`: one clip per cut, grades baked where a look applies, 4K when available. Scale keyframes = the zooms. |
| V2..n | `back` graphics (behind the person) |
| next | `cutout`: the person, premultiplied alpha, same zoom keys as the take |
| next | `front` graphics (word pops, cards, serif words) |
| top two | empty: captions, then blurb (`place_captions.jsx` fills them) |

Audio: A1 voice (mono, linked to the picture), A2 sound effects, A3 caption ticks (**disabled**; enable if wanted).
Everything is its own clip, so any piece can be nudged, trimmed, swapped or deleted.

## Captions and the blurb

`place_captions.jsx` places one `Caption.mogrt` clip per phrase and one `Blurb.mogrt` for the hook, then types the words in
(parameters `Line`, `Keyword`, `Text`). Build the templates first: `mogrt-caption-template.md`.

Running a script against Premiere: Premiere has no universal "run script" menu. Install **VS Code** and Adobe's
**ExtendScript Debugger** extension, open `place_captions.jsx`, choose **Adobe Premiere Pro** as the target, run it with
the sequence open. If your build has File > Scripts > Run Script File, that works too. `var DRY = true;` at the top of
the script logs what it would do without touching the sequence: run that first.

## No-script fallback: captions.srt

`build_xmeml.py` also writes `captions.srt`. File > Import it, drag it onto the sequence: native, editable Premiere captions
(plain text, no yellow keyword). Use it if the script route (and VS Code) is more trouble than it's worth.

## Known unknowns (first import is a checkpoint, scripts were written without Premiere to test against)

- Keyframe time offsets and bezier interpolation from the XML.
- Whether `importMGT` takes the track offsets the way the script passes them on this Premiere version, and whether
  ExtendScript is still supported in the current release (Adobe is moving scripting to UXP). If it isn't, the fallback is
  dropping `Caption.mogrt` on the timeline by hand per the placement table in the edit's `README.txt`, or porting the
  loop in `place_captions.jsx` to UXP (same data, different calls).
- Nothing here has touched a real Premiere install yet. Fix `build_xmeml.py` for whatever the first import shows.
