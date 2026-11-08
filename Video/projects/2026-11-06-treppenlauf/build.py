#!/usr/bin/env python3
"""Build the Treppenlauf reel from raw/ clips. Source of truth for the cut list.

Usage:  python3 build.py [version]      -> exports/treppenlauf_<version>.mp4  (default v1)

Pipeline per segment: trim -> HLG HDR to SDR bt709 -> speed -> 30 fps -> zoom (zoompan on a 4K
upscale for smoothness) -> text overlay (PNG rendered with Pillow; this ffmpeg build has no drawtext)
-> H.264/AAC. Segments are then concatenated without re-encoding.
"""
import subprocess, sys, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
RAW, WORK, EXPORTS = ROOT / "raw", ROOT / "work" / "build", ROOT / "exports"
W, H, FPS = 1080, 1920, 30
FONT = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
YELLOW = (255, 225, 77)
WHITE = (255, 255, 255)
GRADE = "colorspace=all=bt709:iall=bt2020:itrc=bt2020-10:fast=1"
LOOK = "eq=saturation=1.12:contrast=1.04"

# Text block: list of (text, size, colour) lines, centred around y. Safe zone ~ y 260..1500.
def T(y, *lines, box=False):
    return {"y": y, "lines": lines, "box": box}

# DM screenshot is 1170x2532; we use a 9:16 window from y=452 (full width) as the "frame".
DM_CROP = (0, 452, 1170, 452 + 2080)
def dm(x, y):  # absolute screenshot coords -> normalised focus inside the crop
    return ((x - DM_CROP[0]) / 1170, (y - DM_CROP[1]) / 2080)

# Meme templates — tried in v4, removed in v5 (Manuel: looked bad). Kept here, unused, for reference.
# Green/blue-screen meme templates (screen recordings from CapCut in refs/). Keyed with colorkey.
REFS = ROOT / "refs"
DOG_SIDEEYE = dict(src="capcut_1.mov", ss=0.0, key="0x5FFD00", crop=(0, 8, 858, 1228),
                   w=1000, x=-60, y=1920 - 1431, slide=0.18)          # suspicious side-eye, slides in from left
DOG_STARE = dict(src="capcut_1.mov", ss=22.5, key="0x5FFD00", crop=(300, 8, 558, 1228),
                 w=520, x=1080 - 500, y=1920 - 1145)                 # open-mouth stare, bottom right
CAT_DANCE = dict(src="capcut_3.mov", ss=2.0, key="0x00FE00", crop=(0, 0, 844, 1102),
                 w=560, x=1080 - 540, y=1920 - 731 - 150)            # dancing cat with cap
POLL_SCREEN = dict(key="0x0000FD", center=(540, 900), angle=19.5)  # tablet screen in capcut_2

# v6: Manuel's own green-screen cats (clean downloads, refs/cat_*.mp4), with their meme sound.
CAT_SCREAM = dict(src="cat_scream.mp4", ss=4.7, key="0x00FE00", crop=(0, 0, 900, 1350),
                  w=760, x=400, y=1920 - 1140, audio=1.0)         # screaming cat, bottom right
CAT_HAPPY = dict(src="cat_happy.mp4", ss=0.0, key="0x00FF01", crop=(640, 40, 700, 1040),
                 w=640, x=220, y=1920 - 951 - 60, audio=0.9)     # "happy happy happy" cat, bottom centre-left

SEGMENTS = [
    # v7: faster + funnier. Music and meme SFX are added inside Edits (licensed IG songs), see storyboard.md.
    # --- Scene 1: hook
    dict(id="q", src="IMG_2631.MOV", ss=2.0, dur=1.0, zoom=(1.0, 1.06),
         text=T(560, ("Wer wollte", 80, WHITE), ("Treppen laufen?", 80, WHITE))),
    dict(id="hook", src="IMG_2631.MOV", ss=3.3, dur=1.6, zoom=(1.25, 1.38), ease=True,
         text=T(520, ("WER WOLLTE", 120, YELLOW), ("TREPPEN", 120, YELLOW), ("LAUFEN?!", 120, YELLOW)),
         overlays=[CAT_SCREAM]),
    # --- Scene 2: the vote, as quick flashes
    dict(id="wahl", src="IMG_2625.MOV", ss=5.0, dur=1.0, zoom=(1.05, 1.15),
         text=T(600, ("WIR HATTEN", 110, WHITE), ("DIE WAHL:", 110, WHITE))),
    dict(id="opt1", src="IMG_2628.MOV", ss=0.8, dur=0.5, zoom=(1.15, 1.22),
         text=T(600, ("1", 170, YELLOW), ("Lauf-ABC", 100, WHITE))),
    dict(id="opt2", src="IMG_2625.MOV", ss=6.3, dur=0.5, zoom=(1.1, 1.2),
         text=T(600, ("2", 170, YELLOW), ("Last K, Fast K", 90, WHITE))),
    dict(id="opt3", src="IMG_2632.MOV", ss=0.4, dur=0.5, zoom=(1.1, 1.2),
         text=T(600, ("3", 170, YELLOW), ("Treppenläufe", 100, WHITE))),
    dict(id="me", src="IMG_2628.MOV", ss=1.6, dur=1.3, zoom=(1.12, 1.2),
         text=T(560, ("Ich habe für", 72, WHITE), ("LAUF-ABC", 120, YELLOW), ("gestimmt.", 72, WHITE))),
    dict(id="what", src="IMG_2626.MOV", ss=0.8, dur=1.6, zoom=(1.0, 1.35), ease=True,
         text=T(600, ("TREPPENLÄUFE", 100, YELLOW), ("HAT GEWONNEN", 92, WHITE))),
    dict(id="whip", src="IMG_2629.MOV", ss=0.2, dur=0.4, zoom=(1.0, 1.0)),
    # --- Scene 3: asking Leo
    dict(id="leo", img="IMG_2654.PNG", dur=2.0, zoom=(1.0, 1.08), focus=dm(585, 1800),
         text=T(420, ("Also habe ich Leo gefragt,", 60, WHITE), ("wie viele dafür", 60, WHITE),
                ("gestimmt haben …", 60, WHITE), box=True)),
    dict(id="fifteen", img="IMG_2654.PNG", dur=2.0, zoom=(2.0, 2.8), ease=True, focus=dm(340, 1820),
         text=T(470, ("15.", 330, YELLOW))),
    # --- Scene 4: reality, cut on Kernkraft 400's beat (140.5 BPM); the drop lands on "drop"
    dict(id="drop", src="IMG_2631.MOV", ss=4.0, beats=2, zoom=(1.1, 1.18)),
    dict(src="IMG_2632.MOV", ss=1.0, beats=1, zoom=(1.15, 1.2)),
    dict(src="IMG_2633.MOV", ss=0.2, beats=1, zoom=(1.0, 1.1)),
    dict(src="IMG_2632.MOV", ss=3.6, beats=2, zoom=(1.1, 1.2)),
    dict(src="IMG_2634.MOV", ss=0.0, beats=1, zoom=(1.0, 1.1)),
    dict(src="IMG_2631.MOV", ss=5.4, beats=1, zoom=(1.2, 1.25)),
    dict(id="slowmo", src="IMG_2630.MOV", ss=4.4, beats=4, speed=0.5, zoom=(1.0, 1.12)),
    dict(src="IMG_2631.MOV", ss=6.2, beats=2, zoom=(1.2, 1.1)),
    dict(src="IMG_2625.MOV", ss=7.2, beats=1, zoom=(1.1, 1.2)),
    dict(src="IMG_2626.MOV", ss=2.4, beats=1, zoom=(1.1, 1.25)),
    # --- Scene 5: twist
    dict(id="okay", src="IMG_2634.MOV", ss=2.4, beats=3.5, zoom=(1.05, 1.1),
         text=T(520, ("Okay …", 100, WHITE), ("ich muss zugeben.", 72, WHITE))),
    dict(id="geil", src="IMG_2634.MOV", ss=4.2, dur=2.4, zoom=(1.1, 1.2),
         text=T(520, ("War doch", 90, WHITE), ("ZIEMLICH GEIL.", 110, YELLOW)), overlays=[CAT_HAPPY]),
]

MIX_IN_EDITS = True  # v7+: no music/SFX baked in; only camera sound + cat sounds. Music & SFX live in Edits.

# --- Music (HeyGen catalog tracks, imported via media-use into .media/audio/bgm/)
BGM = ROOT / ".media" / "audio" / "bgm"
# PLAYFUL stops dead on "15."; HYPE's drop lands on the first beat-cut. Times filled in by assign_durations.
PLAYFUL = dict(file=BGM / "bgm_002.wav", start=0.0, vol=0.45)   # lo-fi plucky, 115 BPM
HYPE = dict(file=BGM / "bgm_001.wav", drop=46.97, lead=0.7, vol=0.9)  # sports, 127.7 BPM

# Sound effects (Openverse / bundled, see .media/audio/sfx/CREDITS.md). Placed relative to a segment id.
SFX_DIR = ROOT / ".media" / "audio" / "sfx"
SFX = [  # (segment id, offset s, file, trim start, length, gain, tempo)
    ("hook",   -0.15, "sfx_011.mp3", 0.0,  0.57, 0.9, 1.0),   # whoosh into the hook punchline
    ("what",    0.12, "sfx_006.mp3", 0.0,  1.1,  6.0, 0.8),   # "confused what?" stretched to a "whaaat"
    ("whip",   -0.15, "sfx_011.mp3", 0.0,  0.57, 0.8, 1.0),   # whoosh on the whip pan
    ("leo",     0.20, "sfx_001.mp3", 0.0,  1.6,  3.0, 1.0),   # typing the DM
    ("leo",     1.70, "sfx_002.mp3", 0.05, 0.6,  0.6, 1.0),   # reply comes in
    ("fifteen", 0.45, "sfx_008.mp3", 0.05, 1.95, 1.6, 1.0),   # jammern (two groans)
    ("okay",   -0.70, "sfx_003.mp3", 0.0,  1.3,  0.6, 1.0),   # record scratch, scratch onset is 0.7 s in
    ("okay",    0.25, "sfx_005.mp3", 2.0,  1.3, 12.0, 1.0),   # sigh
    ("geil",    0.0,  "sfx_004.mp3", 0.0,  2.4,  0.25, 1.0),  # crowd cheering (under the happy cat)
]
DUCK_WHAT = 0.25  # playful music level under the "what"
BEAT = 0.42696  # v7: Kernkraft 400 (Sport Chant Stadium Remix), from Edits beat markers
ORIG_VOL = 0.35  # original camera sound under the music


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit("ffmpeg failed:\n" + " ".join(map(str, cmd)) + "\n" + r.stderr[-2000:])


def render_text(block, path):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rows = []
    for text, size, colour in block["lines"]:
        font = ImageFont.truetype(FONT, size)
        for line in textwrap.wrap(text, 26) or [""]:
            bbox = d.textbbox((0, 0), line, font=font, stroke_width=size // 12)
            rows.append((line, font, colour, size, bbox[2] - bbox[0], int(size * 1.12)))
    total = sum(r[5] for r in rows)
    y = block["y"] - total // 2
    if block.get("box"):  # dark rounded card behind the text, for busy backgrounds
        bw = max(r[4] for r in rows) + 80
        d.rounded_rectangle(((W - bw) / 2, y - 40, (W + bw) / 2, y + total + 30), radius=36,
                            fill=(0, 0, 0, 200))
    for line, font, colour, size, tw, lh in rows:
        sw = max(4, size // 12)
        # soft drop shadow, then stroked text
        d.text(((W - tw) / 2 + 6, y + 8), line, font=font, fill=(0, 0, 0, 140), stroke_width=sw,
               stroke_fill=(0, 0, 0, 140))
        d.text(((W - tw) / 2, y), line, font=font, fill=colour, stroke_width=sw, stroke_fill=(0, 0, 0))
        y += lh
    img.save(path)


def zoompan(z0, z1, frames, ease=False, focus=(0.5, 0.5)):
    p = f"(on/{max(frames - 1, 1)})"
    if ease:  # ease-out cubic for punch-ins
        p = f"(1-pow(1-{p},3))"
    fx, fy = focus
    return (f"zoompan=z='{z0}+({z1}-{z0})*{p}'"
            f":x='clip({fx}*iw-iw/zoom/2,0,iw-iw/zoom)':y='clip({fy}*ih-ih/zoom/2,0,ih-ih/zoom)'"
            f":d=1:s={W}x{H}:fps={FPS}")


def render_poll(path, center, angle):
    """White 'app' screen with the vote result, rotated to match the tablet in the template."""
    card = Image.new("RGBA", (1400, 900), (255, 255, 255, 255))
    d = ImageDraw.Draw(card)
    rows = [("UMFRAGE FREITAG", 52, (120, 120, 120)), ("Lauf-ABC: 1", 70, (60, 60, 60)),
            ("TREPPENLÄUFE", 110, (220, 30, 30)), ("15 STIMMEN", 90, (220, 30, 30))]
    y = 70
    for text, size, colour in rows:
        f = ImageFont.truetype(FONT, size)
        tw = d.textbbox((0, 0), text, font=f)[2]
        d.text(((1400 - tw) / 2, y), text, font=f, fill=colour)
        y += int(size * 1.35)
    card = card.rotate(angle, expand=True, resample=Image.BICUBIC, fillcolor=(255, 255, 255, 255))
    bg = Image.new("RGB", (W, H), (255, 255, 255))
    bg.paste(card, (int(center[0] - card.width / 2), int(center[1] - card.height / 2)), card)
    bg.save(path)


def n_inputs(inputs):
    return sum(1 for x in inputs if x == "-i")


def build_segment(i, seg):
    out = WORK / f"seg_{i:02d}.mp4"
    dur = seg["dur"]
    frames = round(dur * FPS)
    zp = zoompan(*seg.get("zoom", (1.0, 1.0)), frames, seg.get("ease", False), seg.get("focus", (0.5, 0.5)))
    inputs, fc = [], []
    silent = ["-f", "lavfi", "-t", f"{dur:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
    if "src" in seg:
        speed = seg.get("speed", 1.0)
        inputs += ["-ss", str(seg["ss"]), "-t", f"{dur * speed + 0.1:.3f}", "-i", str(RAW / seg["src"])]
        fc.append(f"[0:v]{GRADE},setpts=(PTS-STARTPTS)/{speed},fps={FPS},scale=2160:3840,{zp},{LOOK}[base]")
        fc.append(f"[0:a]atempo={speed},aresample=48000,volume={ORIG_VOL},"
                  f"afade=t=in:d=0.03,afade=t=out:st={dur - 0.04:.3f}:d=0.04[aud]")
    elif "tpl" in seg:  # meme template as the full picture (SDR screen recording, no HDR conversion)
        inputs += ["-ss", str(seg["ss"]), "-t", f"{dur + 0.1:.3f}", "-i", str(REFS / seg["tpl"])]
        fc.append(f"[0:v]setpts=PTS-STARTPTS,fps={FPS},scale=-2:{H},crop={W}:{H},setsar=1[tplv]")
        if seg.get("screen"):
            sc = seg["screen"]
            poll = WORK / f"poll_{i:02d}.png"
            render_poll(poll, sc["center"], sc["angle"])
            idx = n_inputs(inputs)
            inputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{dur:.3f}", "-i", str(poll)]
            # template's white "PIC/VIDEO" lettering sits on the blue screen: recolour light-blue/white
            # pixels to the key blue first so the letters vanish too, then key.
            c = "gt(b(X\\,Y)\\,200)*gt(r(X\\,Y)+g(X\\,Y)\\,180)"
            fc.append(f"[tplv]format=gbrp,geq=r='if({c}\\,0\\,r(X\\,Y))':g='if({c}\\,0\\,g(X\\,Y))'"
                      f":b='if({c}\\,253\\,b(X\\,Y))',colorkey={sc['key']}:0.38:0.10[keyed];"
                      f"[{idx}:v]format=yuv420p[under];"
                      f"[under][keyed]overlay=0:0:shortest=1[base]")
        else:
            fc.append("[tplv]null[base]")
        idx = n_inputs(inputs)
        inputs += silent
        fc.append(f"[{idx}:a]aformat=channel_layouts=stereo,aresample=48000[aud]")
    else:
        still = WORK / "dm_crop.png"
        if not still.exists():
            Image.open(RAW / seg["img"]).convert("RGB").crop(DM_CROP).resize((2160, 3840), Image.LANCZOS).save(still)
        inputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{dur:.3f}", "-i", str(still)]
        fc.append(f"[0:v]{zp},format=yuv420p[base]")
        if seg.get("hit"):  # synthesized bass hit for the punchline
            inputs += ["-f", "lavfi", "-t", f"{dur:.3f}", "-i",
                       "aevalsrc='0.9*sin(2*PI*52*t)*exp(-4*t)+0.35*sin(2*PI*104*t)*exp(-8*t)':s=48000"]
        else:
            inputs += silent
        fc.append("[1:a]aformat=channel_layouts=stereo,aresample=48000[aud]")
    vlabel, alabel = "base", "aud"
    for k, ov in enumerate(seg.get("overlays", [])):  # keyed meme overlays
        idx = n_inputs(inputs)
        inputs += ["-ss", str(ov["ss"]), "-t", f"{dur + 0.1:.3f}", "-i", str(REFS / ov["src"])]
        cx, cy, cw, ch = ov["crop"]
        fc.append(f"[{idx}:v]setpts=PTS-STARTPTS,fps={FPS},crop={cw}:{ch}:{cx}:{cy},"
                  f"colorkey={ov['key']}:0.42:0.06,format=gbrap,despill=type=green:mix=0.15:expand=0,"
                  f"scale={ov['w']}:-2,format=yuva420p[ov{k}]")
        x = str(ov["x"])
        if ov.get("slide"):  # slide in from the left edge
            x = f"if(lt(t,{ov['slide']}),-w+(w+{ov['x']})*t/{ov['slide']},{ov['x']})"
        fc.append(f"[{vlabel}][ov{k}]overlay=x='{x}':y={ov['y']}:eof_action=pass[o{k}]")
        vlabel = f"o{k}"
        if ov.get("audio"):  # the meme's own sound
            fc.append(f"[{idx}:a]asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,"
                      f"volume={ov['audio']},afade=t=out:st={dur - 0.08:.3f}:d=0.08[ova{k}];"
                      f"[{alabel}][ova{k}]amix=inputs=2:normalize=0:duration=first[aud{k}]")
            alabel = f"aud{k}"
    if seg.get("text"):
        png = WORK / f"text_{i:02d}.png"
        render_text(seg["text"], png)
        idx = n_inputs(inputs)
        inputs += ["-loop", "1", "-i", str(png)]
        fc.append(f"[{vlabel}][{idx}:v]overlay=0:0:shortest=1[txt]")
        vlabel = "txt"
    fc.append(f"[{vlabel}]format=yuv420p,setsar=1[v]")
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc),
         "-map", "[v]", "-map", f"[{alabel}]", "-t", f"{dur:.3f}", "-r", str(FPS),
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-profile:v", "high",
         "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(out)])
    return out


def assign_durations():
    """Fixed segments use dur; beat segments get frame-snapped lengths on the music's beat grid."""
    frame, beat_anchor, beats_done = 0, None, 0
    for seg in SEGMENTS:
        if "beats" in seg:
            if beat_anchor is None:
                beat_anchor = frame / FPS
            beats_done += seg["beats"]
            end = round((beat_anchor + beats_done * BEAT) * FPS)
        else:
            end = frame + round(seg["dur"] * FPS)
        seg["dur"] = (end - frame) / FPS
        seg["t"] = frame / FPS
        if "beats" in seg and "at" not in HYPE:
            HYPE["at"] = seg["t"]
        if seg.get("id") == "fifteen":
            PLAYFUL["until"] = seg["t"]
        frame = end
    return frame / FPS


def mix_music(picture, out, total):
    at = {seg["id"]: seg["t"] for seg in SEGMENTS if "id" in seg}
    lead_at = HYPE["at"] - HYPE["lead"]
    hype_len = total - lead_at
    w0, w1 = at["what"], at["what"] + 1.3
    fc = [f"[0:a]anull[orig]",
          f"[1:a]atrim={PLAYFUL['start']}:{PLAYFUL['start'] + PLAYFUL['until']},asetpts=PTS-STARTPTS,"
          f"volume={PLAYFUL['vol']},volume={DUCK_WHAT}:enable='between(t,{w0:.3f},{w1:.3f})',"
          f"afade=t=in:d=0.05,afade=t=out:st={PLAYFUL['until'] - 0.05:.3f}:d=0.05[p]",
          # hype: rise in, drop on the first beat-cut, cut out under "Okay …", back in on "geil"
          f"[2:a]atrim=start={HYPE['drop'] - HYPE['lead']},asetpts=PTS-STARTPTS,volume={HYPE['vol']},"
          f"afade=t=in:d={HYPE['lead']}:curve=exp,afade=t=out:st={hype_len - 1.2:.3f}:d=1.2,"
          f"adelay={int(lead_at * 1000)}:all=1,"
          f"volume=0:enable='between(t,{at['okay'] + 0.03:.3f},{at['geil']:.3f})',"
          f"volume=0.4:enable='gte(t,{at['geil']:.3f})'[h]"]
    inputs = ["-i", str(picture), "-i", str(PLAYFUL["file"]), "-i", str(HYPE["file"])]
    labels = ["[orig]", "[p]", "[h]"]
    for k, (sid, off, f, start, length, gain, tempo) in enumerate(SFX):
        idx = 3 + k
        inputs += ["-i", str(SFX_DIR / f)]
        delay = max(0, int((at[sid] + off) * 1000))
        fc.append(f"[{idx}:a]aresample=48000,aformat=channel_layouts=stereo,atrim={start}:{start + length},"
                  f"asetpts=PTS-STARTPTS,atempo={tempo},volume={gain},afade=t=out:st={length / tempo - 0.08:.3f}:d=0.08,"
                  f"adelay={delay}:all=1[s{k}]")
        labels.append(f"[s{k}]")
    fc.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=first,"
              "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]")
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", "0:v", "-map", "[a]",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(out)])


def main():
    version = sys.argv[1] if len(sys.argv) > 1 else "v1"
    WORK.mkdir(parents=True, exist_ok=True)
    EXPORTS.mkdir(exist_ok=True)
    (WORK / "dm_crop.png").unlink(missing_ok=True)
    total = assign_durations()
    t = 0.0
    parts = []
    for i, seg in enumerate(SEGMENTS):
        print(f"[{i:02d}] {t:5.2f}s  {seg.get('src') or seg.get('img') or seg.get('tpl')}  {seg['dur']:.3f}s")
        parts.append(build_segment(i, seg))
        t += seg["dur"]
    lst = WORK / "concat.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    picture = WORK / "picture.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-c", "copy", str(picture)])
    out = EXPORTS / f"treppenlauf_{version}.mp4"
    if MIX_IN_EDITS:
        run(["ffmpeg", "-v", "error", "-y", "-i", str(picture), "-c", "copy", "-movflags", "+faststart", str(out)])
        print("cue times:", {seg["id"]: round(seg["t"], 3) for seg in SEGMENTS if "id" in seg})
    else:
        mix_music(picture, out, total)
    print(f"-> {out}  ({total:.2f}s)")


if __name__ == "__main__":
    main()
