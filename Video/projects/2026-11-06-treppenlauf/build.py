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

SEGMENTS = [
    # --- Scene 1: hook
    dict(src="IMG_2631.MOV", ss=2.6, dur=2.6, zoom=(1.0, 1.12),
         text=T(560, ("15 LEUTE", 130, YELLOW), ("haben tatsächlich für", 64, WHITE),
                ("Treppenläufe gestimmt?!", 64, WHITE))),
    # --- Scene 2: disbelief
    dict(src="IMG_2625.MOV", ss=5.0, dur=1.6, zoom=(1.05, 1.15),
         text=T(600, ("WIR HATTEN", 110, WHITE), ("DIE WAHL.", 110, WHITE), ("", 30, WHITE),
                ("Lauf-ABC", 56, WHITE), ("Last K, Fast K", 56, WHITE), ("Treppenläufe", 56, WHITE))),
    dict(src="IMG_2628.MOV", ss=0.8, dur=1.8, zoom=(1.12, 1.12),
         text=T(560, ("Ich habe für", 72, WHITE), ("LAUF-ABC", 120, YELLOW), ("gestimmt.", 72, WHITE))),
    dict(src="IMG_2626.MOV", ss=0.8, dur=1.8, zoom=(1.0, 1.3), ease=True,
         text=T(600, ("15 LEUTE", 130, YELLOW), ("WOLLEN", 110, WHITE), ("TREPPENLAUF?!", 100, WHITE))),
    dict(src="IMG_2629.MOV", ss=0.2, dur=0.4, zoom=(1.0, 1.0)),
    # --- Scene 3: confirmation (DM screenshot)
    dict(img="IMG_2654.PNG", dur=2.0, zoom=(1.0, 1.08), focus=dm(585, 1800),
         text=T(420, ("Also habe ich Leo gefragt,", 60, WHITE), ("wie viele dafür", 60, WHITE),
                ("gestimmt haben …", 60, WHITE), box=True)),
    dict(img="IMG_2654.PNG", dur=1.4, zoom=(2.0, 2.6), ease=True, focus=dm(340, 1820), hit=True,
         text=T(470, ("15.", 330, YELLOW))),
    # --- Scene 4: reality — quick cuts (re-time to music beat later)
    # From here on lengths are in beats of the sports track; the drop lands on the first cut.
    dict(src="IMG_2631.MOV", ss=4.0, beats=2, zoom=(1.1, 1.18)),
    dict(src="IMG_2632.MOV", ss=0.4, beats=2, zoom=(1.15, 1.05)),
    dict(src="IMG_2633.MOV", ss=0.2, beats=2, zoom=(1.0, 1.12)),
    dict(src="IMG_2632.MOV", ss=3.6, beats=2, zoom=(1.1, 1.2)),
    dict(src="IMG_2630.MOV", ss=4.4, beats=4, speed=0.5, zoom=(1.0, 1.1)),
    dict(src="IMG_2631.MOV", ss=6.0, beats=2, zoom=(1.2, 1.1)),
    dict(src="IMG_2634.MOV", ss=0.0, beats=2, zoom=(1.0, 1.1)),
    dict(src="IMG_2625.MOV", ss=7.2, beats=2, zoom=(1.1, 1.2)),
    # --- Scene 5: twist
    dict(src="IMG_2634.MOV", ss=2.4, beats=4, zoom=(1.05, 1.1),
         text=T(520, ("Okay …", 100, WHITE), ("ich muss zugeben.", 72, WHITE))),
    dict(src="IMG_2634.MOV", ss=4.2, beats=5, zoom=(1.1, 1.2),
         text=T(520, ("War doch", 90, WHITE), ("ZIEMLICH GEIL.", 110, YELLOW))),
]

# --- Music (HeyGen catalog tracks, imported via media-use into .media/audio/bgm/)
BGM = ROOT / ".media" / "audio" / "bgm"
PLAYFUL = dict(file=BGM / "bgm_002.wav", start=0.0, until=10.2, vol=0.45)   # lo-fi plucky, 115 BPM
HYPE = dict(file=BGM / "bgm_001.wav", drop=46.97, at=11.6, lead=0.7, vol=0.9)  # sports, 127.7 BPM
BEAT = 60 / 127.7
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


def build_segment(i, seg):
    out = WORK / f"seg_{i:02d}.mp4"
    dur = seg["dur"]
    frames = round(dur * FPS)
    zp = zoompan(*seg.get("zoom", (1.0, 1.0)), frames, seg.get("ease", False), seg.get("focus", (0.5, 0.5)))
    inputs, fc = [], []
    if "src" in seg:
        speed = seg.get("speed", 1.0)
        inputs += ["-ss", str(seg["ss"]), "-t", f"{dur * speed + 0.1:.3f}", "-i", str(RAW / seg["src"])]
        fc.append(f"[0:v]{GRADE},setpts=(PTS-STARTPTS)/{speed},fps={FPS},scale=2160:3840,{zp},{LOOK}[base]")
        fc.append(f"[0:a]atempo={speed},aresample=48000,volume={ORIG_VOL},"
                  f"afade=t=in:d=0.03,afade=t=out:st={dur - 0.04:.3f}:d=0.04[aud]")
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
            inputs += ["-f", "lavfi", "-t", f"{dur:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
        fc.append("[1:a]aformat=channel_layouts=stereo,aresample=48000[aud]")
    vlabel = "base"
    if seg.get("text"):
        png = WORK / f"text_{i:02d}.png"
        render_text(seg["text"], png)
        idx = len([x for x in inputs if x == "-i"])
        inputs += ["-loop", "1", "-i", str(png)]
        fc.append(f"[base][{idx}:v]overlay=0:0:shortest=1[txt]")
        vlabel = "txt"
    fc.append(f"[{vlabel}]format=yuv420p,setsar=1[v]")
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc),
         "-map", "[v]", "-map", "[aud]", "-t", f"{dur:.3f}", "-r", str(FPS),
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
        frame = end
    return frame / FPS


def mix_music(picture, out, total):
    lead_at = HYPE["at"] - HYPE["lead"]
    hype_len = total - lead_at
    fc = (f"[1:a]atrim={PLAYFUL['start']}:{PLAYFUL['start'] + PLAYFUL['until']},asetpts=PTS-STARTPTS,"
          f"volume={PLAYFUL['vol']},afade=t=in:d=0.05,afade=t=out:st={PLAYFUL['until'] - 0.05}:d=0.05[p];"
          f"[2:a]atrim=start={HYPE['drop'] - HYPE['lead']},asetpts=PTS-STARTPTS,volume={HYPE['vol']},"
          f"afade=t=in:d={HYPE['lead']}:curve=exp,afade=t=out:st={hype_len - 1.2:.3f}:d=1.2,"
          f"adelay={int(lead_at * 1000)}:all=1[h];"
          f"[0:a][p][h]amix=inputs=3:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11,"
          f"aresample=48000[a]")
    run(["ffmpeg", "-v", "error", "-y", "-i", str(picture), "-i", str(PLAYFUL["file"]),
         "-i", str(HYPE["file"]), "-filter_complex", fc, "-map", "0:v", "-map", "[a]",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
         "-movflags", "+faststart", str(out)])


def main():
    version = sys.argv[1] if len(sys.argv) > 1 else "v1"
    WORK.mkdir(parents=True, exist_ok=True)
    EXPORTS.mkdir(exist_ok=True)
    (WORK / "dm_crop.png").unlink(missing_ok=True)
    total = assign_durations()
    t = 0.0
    parts = []
    for i, seg in enumerate(SEGMENTS):
        print(f"[{i:02d}] {t:5.2f}s  {seg.get('src', seg.get('img'))}  {seg['dur']:.3f}s")
        parts.append(build_segment(i, seg))
        t += seg["dur"]
    lst = WORK / "concat.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    picture = WORK / "picture.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-c", "copy", str(picture)])
    out = EXPORTS / f"treppenlauf_{version}.mp4"
    mix_music(picture, out, total)
    print(f"-> {out}  ({total:.2f}s)")


if __name__ == "__main__":
    main()
