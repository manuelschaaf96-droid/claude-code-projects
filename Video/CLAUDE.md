# Video — Instagram Reels editing workflow

Manuel shoots the raws, Claude does the cutting/assembly with **ffmpeg** (installed via Homebrew),
and we plan everything in markdown first. Later this may connect to another editor (DaVinci, CapCut, Premiere).

## Folder layout

```
Video/
├── inbox/                 # Drop raws here (AirDrop / copy). Claude sorts them into a project.
├── references/            # Reel library: reference clips + references.md (what we like about each)
├── style-guide.md         # Our house look: format, captions, pacing, colour, music rules
├── templates/
│   └── storyboard.md      # Copy this for each new reel
├── tools/                 # Reusable scripts (contact sheets, transcription, export presets)
└── projects/
    └── YYYY-MM-DD-slug/
        ├── storyboard.md  # The plan: hook, shots, text, music, cut list  ← versioned in git
        ├── log.md         # Clip log: what's in each raw, good takes, timecodes ← versioned
        ├── raw/           # Original footage (never modified, gitignored)
        ├── refs/          # Reference reels for this project (gitignored)
        ├── work/          # Frames, proxies, transcripts, intermediate renders (gitignored)
        └── exports/       # Final MP4s for upload (gitignored)
```

Only `.md` files and scripts go in git. All media is gitignored (see `.gitignore`).

## Workflow per reel

1. **Ingest** — Manuel drops raws in `inbox/` and names the idea. Claude creates the project folder,
   moves raws to `raw/`, and runs `ffprobe` on each (duration, resolution, fps, orientation).
2. **Look** — Claude can't watch video, so it "sees" footage by:
   - extracting frames / contact sheets (`ffmpeg ... fps=1` tiled) into `work/` and viewing them as images
   - transcribing speech (Whisper, once installed) for talking-head clips
   - Claude writes findings to `log.md` (clip → content, best moments with timecodes).
3. **Storyboard** — we write `storyboard.md` together from `templates/storyboard.md`
   (Manuel can text the plan in chat; Claude formats it). Agree before cutting.
4. **Rough cut** — Claude cuts per the storyboard's cut list with ffmpeg, renders a low-res preview
   to `exports/` (`*_preview.mp4`), and sends it. Manuel gives notes by timecode ("at 0:04 cut earlier").
5. **Final** — export per `style-guide.md` export spec → `exports/<slug>_final.mp4`.
   Deliverables stay in `exports/`; to hand one to Edits, copy it to `~/Movies/Claude Exports/` and
   `newProject` → `importMedia` → `setTitle` → `saveProject` through the Edits MCP. Never import into Photos.
6. Commit the `.md` files and push.

## Tools & skills

- **ffmpeg / ffprobe** (Homebrew) — cutting, concatenating, scaling, burning text, export.
- **`hyperframes` skills** (already available to Claude) — animated titles, kinetic text, captions,
  overlays, transitions rendered from HTML to video; `hyperframes-registry` has ~450 ready-made blocks.
- **`media-use` skill** (already available) — transcripts, captions, colour grades/looks, music & SFX,
  audio mixing with free local tools.
- **Whisper** (to install) — speech-to-text for talking-head clips and captions.
- **Edits** (Instagram's editor, `/Applications/Edits.app`) — connected to Claude via its own MCP server
  `metapilot-native` (http://127.0.0.1:19501/mcp, user scope; only reachable while Edits is running).
  ~250 tools: newProject, importMedia, addText, captions, licensed IG music (`addSongToComposition`),
  sound effects, transitions, colour, export, frame capture. **Edits is sandboxed: it can only import
  files from `~/Movies`** — copy deliverables to `~/Movies/Claude Exports/` before `importMedia`.
  Never import into the Photos library.
  `export` (path in `~/Movies`) renders the full mix **including licensed songs** (verified 2026-11-08: tempo of both
  songs measurable in the file; a project with *only* a song and no video exports without audio). Note: a file with
  licensed music posted outside Edits may be flagged/muted by Instagram — posting from Edits keeps the licence.
  **Never delete or overwrite files in `~/Movies/Claude Exports/`** — Edits references them in place
  (no copy); deleting one breaks every project that uses it. To swap a clip's media use a **new filename**
  (`replaceElementMedia` refuses a name already in its library) and check `sourceInPoint` afterwards:
  the swap resets it to 0 on pieces that don't start at source 0 — `slipClip` it back. Music tracks don't ripple when clips
  are deleted — re-align them by hand.
- **Wispr Flow** — Manuel's dictation app (voice → typed text). Used to talk storyboards into chat;
  it does not transcribe video files.
- Later: a DaVinci Resolve MCP server if we move editing into Resolve.

## Reference reels

Manuel saves reels (Instagram "Save" → download, or screen-record) into `references/` or a project's
`refs/`. Claude breaks them down (contact sheet + timing of cuts via scene detection) and records the
takeaways in `references/references.md`. Claude does not log into Instagram.

## Export spec (default, see style-guide.md)

- 1080×1920 (9:16), H.264 High, yuv420p, 30 fps (or source fps if 24/25/60 intended), AAC 48 kHz 192k
- `-movflags +faststart`, ~12–16 Mbps
- Keep text/captions inside IG safe zone: avoid top ~250 px and bottom ~420 px, right ~150 px

## Conventions

- Never modify or delete files in `raw/` — always write new files to `work/` or `exports/`.
- Timecodes in notes as `m:ss.f` (e.g. `0:04.5`) relative to the source clip or the edit, say which.
- Licensed music is best added inside Instagram at upload (copyright); we export with a scratch track
  or no music unless Manuel provides a licensed file.
