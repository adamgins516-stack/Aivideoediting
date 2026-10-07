# premiere-edit: exact walkthrough (MacBook)

Do the parts in order. Every grey box is copy-paste. Press **Return** after each paste. If a step shows an error, stop,
copy the whole error, and give it to Claude.

Terminal = press **Cmd + Space**, type `Terminal`, press Return. Keep one Terminal window open the whole time.

---

## PART 1: Install the tools (about 15 minutes)

### 1.1 Apple's developer tools (also gives you `git`)
```bash
xcode-select --install
```
A pop-up appears. Click **Install**, then **Agree**. Wait until it says "The software was installed" (5-10 minutes).
If it says "command line tools are already installed", that's fine, go on.

### 1.2 Homebrew (the Mac app installer)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
It asks for your Mac password (typing shows nothing, that's normal) and says "Press RETURN". When it finishes, it prints
a **"Next steps"** section. Paste these two lines (Apple Silicon Macs, which yours is):
```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```
Check it worked:
```bash
brew --version
```
It should print `Homebrew 4.x.x`.

### 1.3 Video, Python and speech-to-text tools
```bash
brew install ffmpeg python pipx
```
```bash
pipx ensurepath
```
```bash
pipx install mlx-whisper
```
```bash
pip3 install --break-system-packages pillow numpy opencv-python-headless
```
Now **close Terminal completely (Cmd + Q) and open it again** so the new paths load.

### 1.4 Claude Code
Skip this if you already type `claude` in Terminal and it opens. Check:
```bash
claude --version
```
If it says "command not found":
```bash
curl -fsSL https://claude.ai/install.sh | bash
```
Then close and reopen Terminal, run `claude --version` again, and sign in the first time you run `claude`.

### 1.5 VS Code (used once to run the caption script)
```bash
brew install --cask visual-studio-code
```
Wait for it to finish, then:
```bash
export PATH="$PATH:/Applications/Visual Studio Code.app/Contents/Resources/app/bin"
code --install-extension Adobe.extendscript-debug
```
If the second command says it installed the extension, good. (If `code` is "not found", open VS Code from Applications,
press **Cmd + Shift + X**, search `ExtendScript Debugger` by Adobe, click **Install**.)

---

## PART 2: Get the skill (2 minutes)

```bash
cd ~
git clone https://github.com/adamgins516-stack/Aivideoediting.git
```
If it asks for a username and password, the repo is private. Do this instead:
```bash
brew install gh
gh auth login
```
Pick **GitHub.com**, **HTTPS**, **Yes** (authenticate Git), **Login with a web browser**, copy the code it shows, press
Return, paste the code in the browser page, approve. Then:
```bash
cd ~
gh repo clone adamgins516-stack/Aivideoediting
```

Install the skill:
```bash
mkdir -p ~/.claude/skills
cp -r ~/Aivideoediting/premiere-edit ~/.claude/skills/
```

Run the checker. **It installs nothing**; it only tells you what is still missing:
```bash
bash ~/.claude/skills/premiere-edit/scripts/setup_check.sh
```
Everything should say `[ok]` **except** the two `.mogrt` lines and possibly Premiere. Those are Part 3.

---

## PART 3: Build the caption template in Premiere (one time, about 15 minutes)

Claude cannot make this file; it has to be built in Premiere's graphics panel. After this, every caption in every future
edit uses it.

Make the folder it gets saved in:
```bash
mkdir -p ~/Documents/premiere-edit
```

### 3.1 Set up a vertical sequence
1. Open **Premiere Pro** (current release, not beta). **File > New > Project**, name it `templates`, **Create**.
2. **File > New > Sequence**. Click the **Settings** tab at the top.
3. **Editing Mode:** Custom. **Timebase:** 30.00 frames/second. **Frame Size:** `1080` horizontal, `1920` vertical.
   **Sequence Name:** `caption template`. Click **OK**.
4. **Window > Workspaces > Graphics**. Then **Window > Essential Graphics** if the panel isn't on the right.

### 3.2 Caption.mogrt
1. Click the **Type tool** in the toolbar (the **T**) or press **T**.
2. In the **Program Monitor**, click and **drag a box** near the lower part of the frame, about two-thirds of the frame wide
   (the box should be about **720 px** wide). Type: `caption words`. Press **Esc**.
3. A text clip appears on the timeline. Click it. In **Essential Graphics > Edit** you see the layer.
4. Select the layer. Set it up (all under the **Edit** tab; scroll down for **Appearance**):
   - **Font:** `Avenir Next` **Heavy** (or any heavy font you like).
   - **Size:** `64`.
   - **Align:** the **center** paragraph button.
   - **Appearance:** Fill checked, white (`#FFFFFF`). **Shadow** checked: opacity about `60%`, angle `135`, distance `4`, blur `8`.
5. Under **Align and Transform**, set the layer's position: horizontal `500`, vertical `1500`.
   (Position fields are `x, y` in pixels from the top-left.)
6. **Rename the layer:** double-click its name in the layer list at the top of the panel and type exactly `Line`
   (capital L, lowercase `ine`, no spaces). Press Return.
7. **Duplicate it:** hold **Option** and drag the `Line` layer down in the list, or select it and press **Cmd + C**, then
   **Cmd + V**. You now have two layers.
8. Select the copy. Rename it exactly `Keyword`. Change its text to `keyword`. Fill color: click the white swatch and type
   `F2CF4A` in the hex box. Move it to vertical `1585` so it sits just under `Line`.
9. Select both clips' graphic (they are one clip on the timeline). **Right-click the clip in the timeline > Export As
   Motion Graphics Template...**
10. **Name:** `Caption`. **Destination:** `Local Drive` (not "Local Templates Folder"). Click **OK** and save into
    `Documents > premiere-edit` (the folder you made above). The file must end up at
    `~/Documents/premiere-edit/Caption.mogrt`.

### 3.3 Blurb.mogrt
1. In the same sequence, delete the caption clip (click it, press Delete).
2. **Rectangle tool** (hold the **Pen tool** icon to find it, or press **R** if available). Drag a rectangle in the upper
   part of the frame. In **Essential Graphics > Edit**: Fill white, **Corner radius** high (rounded), no stroke.
3. **Type tool:** click inside the rectangle and type `hook text here`. Font Avenir Next Heavy, size `50`, center
   aligned, fill dark (`111113`).
4. Rename the text layer exactly `Text`. Rename the rectangle `Box`.
5. Select `Box`. In **Essential Graphics**, find **Responsive Design - Position**. Check **Pin To:** and choose `Text`.
   Set the padding to about `44` left/right and `22` top/bottom. (This makes the white box grow with the words.)
6. Position the pair: horizontal `540`, vertical `415`.
7. Right-click the clip > **Export As Motion Graphics Template...**, **Name:** `Blurb`, **Destination:** `Local Drive`,
   save into the same `premiere-edit` folder.

### 3.4 Test the template
1. Drag `~/Documents/premiere-edit/Caption.mogrt` from Finder onto a timeline. Click the clip. In **Essential Graphics >
   Edit** type something different in the `Line` and `Keyword` boxes. Both should change on screen.
2. If a box is named something else, rename the layer and re-export.

Check:
```bash
ls ~/Documents/premiere-edit
```
You should see `Blurb.mogrt` and `Caption.mogrt`. Then:
```bash
bash ~/.claude/skills/premiere-edit/scripts/setup_check.sh
```
Everything should now say `[ok]`.

(Menu names shift a little between Premiere versions. If a button isn't where this says, tell Claude exactly what you see.)

---

## PART 4: Your first edit

### 4.1 Make a project folder and put your footage in it
```bash
mkdir -p ~/Movies/premiere-edit-test
open ~/Movies/premiere-edit-test
```
Finder opens the folder. Drag your raw take (the `.mp4` or `.mov`) into it. Vertical 1080x1920 or 4K vertical both work.
Rename it to something simple like `take.mp4` (no spaces keeps commands easier).

### 4.2 Start Claude Code in that folder
```bash
cd ~/Movies/premiere-edit-test
claude
```
When it opens, paste this:
```
Use the premiere-edit skill. My raw take is take.mp4 in this folder. Edit it into a Premiere Pro sequence. Ask me whatever you need first.
```
Claude will ask: raw or pre-cut, what it should feel like (send example videos or links if you have them), whether graphics
go in front of or behind your head, if you have a 4K export, whether the caption templates are in place (they are).
Answer, and it runs the pipeline: cut, transcribe, make person masks, plan, a check sheet of frames, render, build.

Things it may ask you to run or approve: it will run `ffmpeg`, `python3`, and compile one small Swift file. Approve those.

### 4.3 When Claude says the sequence is built
It writes into `~/Movies/premiere-edit-test/take-edit/` (name may differ):
- `<name>.xml` the Premiere sequence
- `place_captions.jsx` the caption script
- `premiere_layers/` all the clips (keep this folder, the sequence links to it)
- `FINAL.mp4` a flat preview to watch first
- `README.txt` what lands on which word

Watch `FINAL.mp4` first. Tell Claude what to change. It re-renders.

### 4.4 Bring it into Premiere
1. Open Premiere, **File > New > Project**, name it, **Create**.
2. **File > Import**, pick `<name>.xml`, **Open**. A sequence appears in the Project panel.
3. **Double-click the sequence** to open it. Press **Space** to play. Check the takes line up and the zooms move.
   Tell Claude what you see (screenshots help). First import is the checkpoint: this part has not been tested yet.

### 4.5 Add the editable captions
1. With the sequence open and active, open the folder in VS Code:
```bash
code ~/Movies/premiere-edit-test/take-edit
```
2. In VS Code click `place_captions.jsx`. In the first lines find `var DRY = false;` and change it to `var DRY = true;`
   (a test run that changes nothing). Save with **Cmd + S**.
3. Press **Cmd + Shift + D** (Run and Debug). Click **create a launch.json file**, choose **ExtendScript Debug**. In the
   file that opens, set `"program": "${file}"` and `"targetSpecifier": "premierepro"`, save.
4. Make sure Premiere is open with the sequence active, click `place_captions.jsx` tab, press **F5**.
5. Look at the Debug Console at the bottom. A dry run prints each caption line. Then change `DRY` back to `false`, save, and
   press **F5** again. Captions appear on the top video tracks as clips you can click, retype, restyle and move.

If VS Code can't find Premiere or the script errors, copy the whole message into Claude. This is the part most likely to
need a small fix.

### 4.6 Finish
Add a music bed, adjust anything, then **File > Export > Media**. Delete nothing from `premiere_layers/` until you're done.

---

## If something goes wrong
- Copy the **entire** terminal text (select, Cmd + C) and paste it to Claude.
- `command not found: brew` or `claude`: close Terminal, reopen, try again; if still failing, redo that Part's first step.
- Re-run the checker any time: `bash ~/.claude/skills/premiere-edit/scripts/setup_check.sh`
- To update the skill later:
```bash
cd ~/Aivideoediting && git pull && cp -r ~/Aivideoediting/premiere-edit ~/.claude/skills/
```
