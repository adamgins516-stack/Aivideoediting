#!/usr/bin/env python3
"""build_xmeml.py <layers dir> "<Sequence name>" [--out file.xml] [--mogrt Caption.mogrt] [--blurb-mogrt Blurb.mogrt]

Write a Premiere-importable sequence (Final Cut Pro 7 XML / xmeml v4) from a premiere_layers/ folder, plus a
Premiere script (place_captions.jsx) that drops every caption and the hook blurb in as EDITABLE Motion Graphics
templates. Import in Premiere: File > Import > the .xml  (a bin with the sequence appears; open the sequence).

Reads the files make.py / Edit.layers() writes:
  01_<start>s_TAKE[_look].mp4        take pieces, one per cut (grades baked where a look applies); 4K when available
  02_*_BACK_alpha.mov                graphics behind the person (needs the cutout)
  03_00.00s_CUTOUT_alpha.mov         the person, cut out
  04_*_FRONT_alpha.mov               graphics in front
  05_00.00s_SFX.wav / 06_*.wav       sound effects / caption ticks (ticks come in disabled)
  meta.json                          zoom_keys (eased scale keyframes), cues, blurb, fps

Sequence layout, bottom to top:
  V1 take · V2.. back1..n · cutout · front1..n · two EMPTY tracks (captions, blurb — filled by place_captions.jsx)
  A1 take voice · A2 sfx · A3 caption ticks (disabled)
Zooms are Basic Motion > Scale keyframes on the take pieces and the cutout, scaled so a 4K take still fills the frame.
"""
import os, re, sys, json, argparse, subprocess, html
from urllib.parse import quote

ap = argparse.ArgumentParser()
ap.add_argument("layers"); ap.add_argument("name", nargs="?", default="premiere-edit")
ap.add_argument("--out"); ap.add_argument("--mogrt", default=os.path.expanduser("~/Documents/premiere-edit/Caption.mogrt"))
ap.add_argument("--blurb-mogrt", default=os.path.expanduser("~/Documents/premiere-edit/Blurb.mogrt"))
o = ap.parse_args()
L = os.path.abspath(o.layers); NAME = o.name
META = json.load(open(f"{L}/meta.json")); FPS = int(META.get("fps", 30)); W, H = 1080, 1920
OUT = o.out or os.path.join(os.path.dirname(L), f"{NAME}.xml")

def probe(p, entries, stream="v:0"):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", stream, "-show_entries", f"stream={entries}", "-of", "csv=p=0", p], capture_output=True, text=True).stdout.strip()
    return r.split(",") if r else []
def frames(p):
    n = probe(p, "nb_frames")
    if n and n[0].isdigit(): return int(n[0])
    return int(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", p],
                              capture_output=True, text=True).stdout.strip() or 0)
def size(p): return tuple(int(x) for x in probe(p, "width,height"))
def adur(p): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout)
def fr(t): return int(round(t * FPS))
def url(p): return "file://localhost" + quote(p)
def esc(s): return html.escape(str(s), quote=True)

files = sorted(os.listdir(L))
def items(pre): return sorted((float(re.match(r"\d\d_(\d+\.\d+)s_", f).group(1)), f) for f in files if f.startswith(pre))
def lanes(its):                                      # overlapping graphics get their own tracks
    ends = []; res = []
    for t, f in its:
        d = frames(f"{L}/{f}") / FPS
        k = next((i for i, e in enumerate(ends) if e <= t + 0.001), None)
        if k is None: ends.append(0); k = len(ends) - 1
        ends[k] = t + d; res.append((k, t, f))
    return res

RATE = f"<rate><timebase>{FPS}</timebase><ntsc>FALSE</ntsc></rate>"
SC = lambda w, h: (f"<samplecharacteristics>{RATE}<width>{w}</width><height>{h}</height><anamorphic>FALSE</anamorphic>"
                   "<pixelaspectratio>square</pixelaspectratio><fielddominance>none</fielddominance></samplecharacteristics>")
_ids = {"clip": 0, "file": 0}; _filedef = {}
def nid(k): _ids[k] += 1; return f"{k}item-{_ids[k]}" if k == "clip" else f"file-{_ids[k]}"

def file_xml(f, kind, nfr):
    """the full <file> element the first time a file is used, a bare reference afterwards."""
    if f in _filedef: return f'<file id="{_filedef[f]}"/>'
    fid = nid("file"); _filedef[f] = fid; p = f"{L}/{f}"; w, h = size(p) if kind != "audio" else (0, 0)
    media = ""
    if kind != "audio": media += f"<video>{SC(w, h)}</video>"
    if kind in ("audio", "av"): media += "<audio><samplecharacteristics><depth>16</depth><samplerate>48000</samplerate></samplecharacteristics><channelcount>1</channelcount></audio>"
    return (f'<file id="{fid}"><name>{esc(f)}</name><pathurl>{esc(url(p))}</pathurl>{RATE}<duration>{nfr}</duration>'
            f"<timecode>{RATE}<string>00:00:00:00</string><frame>0</frame><displayformat>NDF</displayformat></timecode><media>{media}</media></file>")

def zval(keys, t):
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t0 <= t <= t1: return v0 + (v1 - v0) * ((t - t0) / (t1 - t0) if t1 > t0 else 0)
    return keys[-1][1] if keys else 1.0
KEYS = [tuple(k) for k in META.get("zoom_keys") or []]
if not KEYS:
    for a, b, s in META.get("punch", []): KEYS += [(a - 1 / FPS, 1.0), (a, s), (b, s), (b + 1 / FPS, 1.0)]
    if META.get("push"): a, b, s = META["push"]; KEYS += [(a, 1.0), (b, s), (b + 1 / FPS, 1.0)]
    KEYS = sorted(KEYS)

def motion(a, b, base):
    """Basic Motion > Scale. base = 100 for 1080-wide media, 50 for 2160-wide (4K) so it fills the frame; keys multiply it. Empty when the clip never zooms."""
    local = [(a / FPS, zval(KEYS, a / FPS))] + [(t, v) for t, v in KEYS if a / FPS + 1e-4 < t < (b - 1) / FPS] + [((b - 1) / FPS, zval(KEYS, (b - 1) / FPS))]
    moving = any(abs(v - 1.0) > 1e-4 for _, v in local)
    kf = "".join(f'<keyframe><when>{max(0, fr(t) - a)}</when><value>{v * base:.3f}</value><interpolation><name>bezier</name></interpolation></keyframe>' for t, v in local) if moving else ""
    return ('<filter><effect><name>Basic Motion</name><effectid>basic</effectid><effectcategory>motion</effectcategory><effecttype>motion</effecttype><mediatype>video</mediatype>'
            f'<parameter authoringApp="PremierePro"><parameterid>scale</parameterid><name>Scale</name><valuemin>0</valuemin><valuemax>1000</valuemax><value>{base:.3f}</value>{kf}</parameter>'
            '</effect></filter>')

def vclip(f, start, nfr, kind="v", zoom=False, link=None, enabled=True):
    cid = nid("clip"); p = f"{L}/{f}"; w, h = size(p); base = 100.0 * W / w if w > W else 100.0
    return cid, (f'<clipitem id="{cid}"><name>{esc(f)}</name><enabled>{"TRUE" if enabled else "FALSE"}</enabled><duration>{nfr}</duration>{RATE}'
                 f"<start>{start}</start><end>{start + nfr}</end><in>0</in><out>{nfr}</out><alphatype>{'straight' if kind == 'alpha' else 'none'}</alphatype>"
                 f"{file_xml(f, 'av' if kind == 'av' else 'v', nfr)}{motion(start, start + nfr, base) if zoom else ''}{link or ''}</clipitem>")

def aclip(f, start, nfr, ref_file_xml=None, link=None, enabled=True):
    cid = nid("clip")
    fx = ref_file_xml or file_xml(f, "audio", nfr)
    return cid, (f'<clipitem id="{cid}" premiereChannelType="mono"><name>{esc(f)}</name><enabled>{"TRUE" if enabled else "FALSE"}</enabled><duration>{nfr}</duration>{RATE}'
                 f"<start>{start}</start><end>{start + nfr}</end><in>0</in><out>{nfr}</out>{fx}<sourcetrack><mediatype>audio</mediatype><trackindex>1</trackindex></sourcetrack>{link or ''}</clipitem>")

def links(pairs):
    return "".join(f"<link><linkclipref>{c}</linkclipref><mediatype>{m}</mediatype><trackindex>{ti}</trackindex><clipindex>{ci}</clipindex></link>" for c, m, ti, ci in pairs)

vtracks = []; atracks = []; total = 0
# --- take: V1 + A1, tiled from real frame counts, voice linked to picture ---
v1 = []; a1 = []; acc = 0; takes = items("01_")
for ci, (t, f) in enumerate(takes, 1):
    n = frames(f"{L}/{f}"); vid, aid = f"clipitem-{_ids['clip'] + 1}", f"clipitem-{_ids['clip'] + 2}"
    lk = links([(vid, "video", 1, ci), (aid, "audio", 1, ci)])
    _, vx = vclip(f, acc, n, "av", zoom=True, link=lk); fx = file_xml(f, "av", n)
    _, ax = aclip(f, acc, n, ref_file_xml=fx, link=lk); v1.append(vx); a1.append(ax); acc += n
total = acc
vtracks.append(v1)
# --- behind the head ---
back = lanes(items("02_")); nback = (max(k for k, *_ in back) + 1) if back else 0
for k in range(nback): vtracks.append([vclip(f, fr(t), frames(f"{L}/{f}"), "alpha")[1] for kk, t, f in back if kk == k])
cut = next((f for f in files if f.startswith("03_")), None)
if cut: vtracks.append([vclip(cut, 0, frames(f"{L}/{cut}"), "alpha", zoom=True)[1]])
front = lanes(items("04_")); nfront = (max(k for k, *_ in front) + 1) if front else 0
for k in range(nfront): vtracks.append([vclip(f, fr(t), frames(f"{L}/{f}"), "alpha")[1] for kk, t, f in front if kk == k])
cap_track = len(vtracks); vtracks += [[], []]                                   # empty tracks for captions + blurb (place_captions.jsx)
atracks.append(a1)
for pre, en in (("05_", True), ("06_", False)):
    f = next((x for x in files if x.startswith(pre)), None)
    atracks.append([aclip(f, 0, fr(adur(f"{L}/{f}")), enabled=en)[1]] if f else [])

def trk(clips, extra=""): return f"<track>{''.join(clips)}{extra}</track>"
vxml = "".join(trk(c) for c in vtracks)
axml = "".join(f'<track currentExplodedTrackIndex="0" totalExplodedTrackCount="1" premiereTrackType="Mono">{"".join(c)}</track>' for c in atracks)
seq = (f'<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>\n<xmeml version="4"><sequence id="sequence-1"><name>{esc(NAME)}</name><duration>{total}</duration>{RATE}'
       f"<timecode>{RATE}<string>00:00:00:00</string><frame>0</frame><displayformat>NDF</displayformat></timecode>"
       f"<media><video><format>{SC(W, H)}</format>{vxml}</video>"
       f"<audio><numOutputChannels>2</numOutputChannels><format><samplecharacteristics><depth>16</depth><samplerate>48000</samplerate></samplecharacteristics></format>{axml}</audio></media></sequence></xmeml>\n")
open(OUT, "w", encoding="utf-8").write(seq)
import xml.etree.ElementTree as ET; ET.parse(OUT)                                 # well-formedness check
print(f"wrote {OUT}  ({len(takes)} take pieces, {nback} back lane(s), {nfront} front lane(s), {total} frames = {total / FPS:.2f}s)")

# --- the caption script: every phrase + the hook blurb as an editable template clip ---
tpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "place_captions.jsx.tpl"), encoding="utf-8").read()
data = {"mogrt": o.mogrt, "blurbMogrt": o.blurb_mogrt, "capTrack": cap_track, "blurbTrack": cap_track + 1, "cues": META.get("cues", []), "blurb": META.get("blurb"), "fps": FPS}
js = tpl.replace("/*__DATA__*/", "var DATA = " + json.dumps(data, ensure_ascii=False) + ";")
jp = os.path.join(os.path.dirname(OUT), "place_captions.jsx"); open(jp, "w", encoding="utf-8").write(js)
print(f"wrote {jp}  ({len(data['cues'])} caption cues" + (", 1 blurb" if data["blurb"] else "") + ")")
