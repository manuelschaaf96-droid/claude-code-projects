# Warum wählen Menschen freiwillig Treppenläufe?

- **Date:** 2026-11-06 (session) · storyboard 2026-11-08
- **Status:** v7 — built in Edits (project "Treppenlauf v7")
- **Goal / one-liner:** Self-ironic disbelief that 15 people voted for stair runs, flipping to "ok, it was actually great".
- **Target length:** ~25 s
- **References:** none yet
- **Music / audio (v2):** 0–10.2 s playful lo-fi (HeyGen catalog `bgm_002`, 115 BPM), hard stop on "15." + synthesized bass hit; sports track (`bgm_001`, 127.7 BPM) rises in from 10.9 s, drop at 11.6 s on the first stairs cut, fades out at the end. Scene 4–5 cuts snapped to its beat. Original camera sound at 35 %.
- **Caption (post text):** _TBD_
- **Hashtags:** _TBD_
- **Tone rule:** friendly teasing inside the community, nobody looks bad.

## Brief (summary of Manuel's brief)

Vote between Lauf-ABC, Last K Fast K, Treppenläufe. Manuel voted Lauf-ABC, 15 people voted stairs. Asked Leo (organiser) how many → "15". We did stairs. It was great.
Scenes: 1 Hook (0–3) · 2 Disbelief (3–8) · 3 Confirmation (8–12) · 4 Reality, fast cuts to music (12–21) · 5 Twist "War doch ziemlich geil" (21–27).

## Cut list (v1) — source of truth is `build.py`

| # | Edit time | Source | In (src) | Len | Move | On-screen text |
|---|---|---|---|---|---|---|
| 1 | 0.0–2.6 | IMG_2631 | 2.6 | 2.6 | slow push-in | **15 LEUTE** haben tatsächlich für Treppenläufe gestimmt?! |
| 2 | 2.6–4.2 | IMG_2625 | 5.0 | 1.6 | push-in | WIR HATTEN DIE WAHL. + Lauf-ABC · Last K, Fast K · Treppenläufe |
| 3 | 4.2–6.0 | IMG_2628 | 0.8 | 1.8 | static zoom | Ich habe für Lauf-ABC gestimmt. |
| 4 | 6.0–7.8 | IMG_2626 | 0.8 | 1.8 | fast punch-in | 15 LEUTE WOLLEN TREPPENLAUF?! |
| 5 | 7.8–8.2 | IMG_2629 | 0.2 | 0.4 | whip | — |
| 6 | 8.2–10.2 | IMG_2654.PNG | DM chat | 2.0 | slow push | Also habe ich Leo gefragt, wie viele dafür gestimmt haben … |
| 7 | 10.2–11.6 | IMG_2654.PNG | zoom on "15 Leute" | 1.4 | punch zoom + bass hit | **15.** |
| 8–15 | 11.6–20.07 | 2631, 2632, 2633, 2632, 2630 (slow-mo, 4 beats), 2631, 2634, 2625 | | 2 beats (~0.94 s) each | cuts on the beat, drop on #8 | — (music carries it) |
| 16 | 20.07–21.93 | IMG_2634 | 2.4 | 4 beats | | Okay … ich muss zugeben. |
| 17 | 21.93–24.30 | IMG_2634 | 4.2 | 5 beats | slow push | War doch ziemlich geil. |

## v7 — faster cut, music + SFX in Edits

Picture (`build.py`, `MIX_IN_EDITS = True`): 23 cuts, 23.1 s, vote options as 0.5 s flashes, reality section cut on
Kernkraft's beat (140.5 BPM, 1–2 beat cuts). Only camera sound + cat sounds are baked in.
Edits project "Treppenlauf v7" (built via the Edits MCP) adds:

| Time | Element | Vol |
|---|---|---|
| 0–6.4 | 🎵 Wii Sports Theme (AWJC Media), stops dead on "15 LEUTE WOLLEN …" | 0.55 |
| 0.9 / 7.95 | Whoosh (sharp) | 1.0 |
| 3.6 / 4.1 / 4.6 | Ding on options 1-2-3 | 0.8–0.9 |
| 6.4 | Record scratch | 1.0 |
| 6.55 | What (cartoon) | 1.3 |
| 8.4–10.35 | Drums (suspense) | 0.6 |
| 8.5–9.9 | Typing (fast) 2 | 0.8 |
| 10.0 | Bell ding (Leo replies) | 0.7 |
| 10.4 | Boom (bass) on "15." | 1.0 |
| 10.75–12.4 | Sad trombone | 0.9 |
| 12.4–19.23 | 🎵 Kernkraft 400 (Sport Chant Stadium Remix), source 48.78 s on the drop cut | 0.8 |
| 19.2 | Vinyl record stop (music gap under "Okay …") | 1.0 |
| 19.65 | Sigh | 1.4 |
| 20.73–23.13 | 🎵 Kernkraft continues (on grid) under the happy cat + Yay (crowd) | 0.4 / 0.6 |

Licensed songs are stripped from Edits file exports — post directly from Edits. Edits' own SFX need no credits.

## Cats (v6)

| Edit time | Clip | Use |
|---|---|---|
| 1.3–3.1 s | `refs/cat_scream.mp4` 4.7–6.5 s | screaming cat bottom right on "WER WOLLTE TREPPEN LAUFEN?!", with its scream sound (replaces the "huh?") |
| 23.6–26.0 s | `refs/cat_happy.mp4` 0–2.4 s | "happy happy happy" cat on "ZIEMLICH GEIL.", its song on top; sports track ducked to 40 %, cheering at 25 % |

## Meme templates (v4 only — removed in v5)

Green/blue-screen templates Manuel screen-recorded from CapCut → `refs/capcut_1..3.mov` (gitignored), keyed in `build.py`.

| Edit time | Template | Use |
|---|---|---|
| 0–1.3 s | — | Hook part 1: "Wer wollte Treppenlauf?" |
| 1.3–2.8 s | capcut_1 0–1.5 s (dog, side-eye) | slides in from left on whoosh + "huh?"; text "WER WOLLTE TREPPEN LAUFEN?!" |
| 6.2–7.3 s | capcut_2 2.55 s (girl + tablet) | our vote card keyed into the blue tablet screen: "TREPPENLÄUFE 15 STIMMEN" |
| 7.3–8.8 s | capcut_2 9.9 s (girl screams) | "whaaat" + "15 LEUTE WOLLEN TREPPENLAUF?!" |
| 11.2–13.8 s | capcut_1 22.5 s (dog, open-mouth stare) | bottom right on "15." while groaning |
| 24.2–26.5 s | capcut_3 2 s (dancing cat) | bottom right on "ZIEMLICH GEIL." |

Template sound is not used. The screen recordings are low-res (~850 px), so the meme parts are softer than our footage.

## Sound effects (v3)

| Edit time | Sound | Why |
|---|---|---|
| 6.1 s | "confused what?" stretched to a "whaaat", music ducked | reaction to 15 LEUTE WOLLEN TREPPENLAUF?! |
| 7.65 s | whoosh | whip pan |
| 8.4 s | iPhone typing | writing to Leo |
| 9.9 s | message ding | reply comes in |
| 10.2 s | music stops + bass hit | "15." |
| 10.65 s | two groans (jammern) | held on "15." (segment extended to 2.6 s) |
| 12.8 s | drop | stairs action starts |
| 21.27 s | record scratch, music cuts out | "Okay … ich muss zugeben." |
| 21.5 s | male sigh | |
| 23.13 s | music back + crowd cheering | "War doch ZIEMLICH GEIL." |

**Credits required (CC BY) — put in the post caption or comments:**
- "Sci Fi Message Notification 7.wav" by F.M.Audio, CC BY 4.0 — https://freesound.org/people/F.M.Audio/sounds/686278
- "small crowd cheering and clapping.wav" by Tomlija, CC BY 3.0 — https://freesound.org/people/Tomlija/sounds/99634

## Open questions

- DM screenshot shows "Welche dumme Sau hat Treppenläufe gedrückt?" — keep, or crop to just the answers?

## Feedback log

- v1 preview (2026-11-08): fixed text overlaps; Manuel asked for music.
- v2 (2026-11-08): music added, scene 4–5 re-timed to the beat. Manuel: "schon sehr gut", needs more humor + SFX (whaat, Leo check, jammern).
- v3 (2026-11-08): SFX pass, longer "15." hold with groans, record-scratch music stop on "Okay …". Manuel: good; new hook "Wer wollte Treppenlauf?" + whoosh + SFX, add grumpy dog overlays; sent CapCut templates.
- v4 (2026-11-08): new two-step hook with side-eye dog, girl/tablet template for the vote, staring dog on "15.", dancing cat at the end. Manuel: memes look terrible, remove.
- v5 (2026-11-08): memes removed; two-step hook (text + whoosh + "huh?") kept, vote beat back on IMG_2626. Exported to Photos/Edits.
- v6 (2026-11-08): Manuel tries green screen again with his own clips: screaming cat on the hook, happy cat at the end.
- v7 (2026-11-08): Manuel: better music, better sound, funnier, faster cuts. Rebuilt in Edits with licensed music + Edits SFX.
- v7c (2026-11-08): text at 6.4 s → "TREPPENLÄUFE HAT GEWONNEN" (Manuel). Manuel had removed the whip pan in Edits (−0.47 s, ripple); both Kernkraft pieces moved −0.47 s to stay on the cuts (drop now 11.93 s, music gap 18.77–20.27 s).
- v7d (2026-11-08, in Edits): removed the two non-stairs shots at 17.9–18.77 s (IMG_2625 flag path, IMG_2626 building; 2 beats). Kernkraft piece 1 trimmed to 17.9, piece 2 moved to 19.4; record stop re-added at 17.87 (ripple delete had removed it). Reel now 21.8 s.
  **The Edits project is now the source of truth** — Manuel's and these edits are not in `build.py`.
- v7f (2026-11-08, in Edits): opening text → "Wer wollte Treppenläufe?" (first video piece 0–8 s swapped to `treppenlauf_v7f.mp4`). _waiting for notes_
