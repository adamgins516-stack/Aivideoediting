# Build the caption template once (about 10 minutes, in Premiere)

Captions in this skill are **real, editable clips**: one Motion Graphics template (`.mogrt`) placed once per phrase by
`place_captions.jsx`, with the words filled in from the transcript. Claude can't author a `.mogrt` (it's made in
Premiere's Essential Graphics panel), so this is the one thing the user builds by hand. After that, every caption in
every future edit uses it, and restyling the template restyles them all.

Save both files in `~/Documents/premiere-edit/` (that's where `build_xmeml.py` looks by default):
`Caption.mogrt` and `Blurb.mogrt`.

## Caption.mogrt

1. New project, then **New Sequence**: Settings tab, Editing Mode **Custom**, frame size **1080 x 1920**, **30 fps**.
2. **Type tool (T)**: drag a text *box* in the Program Monitor, about **720 px wide** (the safe-zone width; text wraps
   inside it), centred horizontally on **x = 500**. Type `caption words`.
3. Window > **Essential Graphics** > **Edit** tab. Select the layer and style it:
   - Font: a heavy sans (Avenir Next Heavy, Montserrat ExtraBold, Inter Black). Size about **64**. Fill **white**.
   - Align: **centre**. Shadow on: opacity about 60%, distance 4, blur 8.
   - Position: line centre at about **y = 1500** (low enough to clear the face, above the platform's bottom block at y > 1690).
4. **Rename the layer** (double-click its name in the layer list) to exactly: `Line`.
5. Duplicate the layer (Option-drag in the layer list), rename the copy `Keyword`, fill **#F2CF4A** (the highlight yellow),
   same font, and place it directly under the first line (about y = 1585). It shows the highlighted word.
6. Optional pop-in: Effect Controls for the graphic: scale 92% to 100% and opacity 0 to 100 over the first 4 frames
   (keyframes). Essential Graphics > **Responsive Design – Time**: protect the first and last 4 frames so the pop-in and
   fade-out stay fixed when the clip is stretched.
7. Right-click the graphic clip in the timeline > **Export As Motion Graphics Template…** Name it `Caption`, save to
   `~/Documents/premiere-edit/` ("Local Drive" destination). Compatibility: current version.

**Why a second line for the keyword?** A mogrt can't reliably colour one word inside a string through scripting, so the
keyword is its own text parameter on its own line. It's a legitimate look (the key word gets the yellow second line).
An upgrade, to try together at the laptop: if Premiere exposes rich-text runs on the Line parameter, `place_captions.jsx`
can colour the word inline and drop the second layer.

## Blurb.mogrt (the hook line near frame zero)

1. Same 1080 x 1920 sequence. **Rectangle tool**: a white rounded rectangle (corner radius about 25%).
2. **Type tool**: dark text (#111113), heavy sans, about 50, centre aligned: `hook text here`.
3. Rename the text layer exactly `Text`.
4. Essential Graphics > select the rectangle > **Responsive Design – Position**: pin it to the `Text` layer with padding
   about 44 px left/right and 22 px top/bottom, so the box grows with the words.
5. Place the pair centred on x = 540, about **y = 415** (under the platform's top tabs, above the head).
6. Export as `Blurb`, same folder.

## Test it

Drag `Caption.mogrt` from the Essential Graphics > Browser > Local Templates (or File > Import) onto the timeline. Type in
the `Line` and `Keyword` fields in the Edit tab. If both change, the parameter names are right. Names are read by
`place_captions.jsx` (`P_LINE`, `P_KEY`, `P_BLURB` at the top); change them there if you named things differently.
