"""Assemble the IsoShift video from separately recorded narration (READ_SHEET.md) and the slide PNGs.

Usage: python build_video.py AUDIO_DIR OUT_DIR [--words asr_words.json] [--screen clip.mp4] [--face face.mp4]

AUDIO_DIR holds 14 recordings in recording order (Windows Sound Recorder names: "Kayıt.m4a", "Kayıt (2).m4a" ...
"Kayıt (14).m4a"): segment 00 (intro) then 01 to 13. Each slide is held for its segment's audio. Segment 12 shows
the marimo screen clip (--screen, trimmed or slowed to fit) or, without one, the three app screenshots.
Writes OUT_DIR/isoshift_youtube.mp4 (01 to 13) and, with --face, OUT_DIR/isoshift_linkedin.mp4 (00 then 01 to 13);
captions.srt and captions_linkedin.srt next to this script are rebuilt from the real segment timings. Caption text is
READ_SHEET.md word for word; --words (faster-whisper word timings per segment) only places cue starts inside a segment.
"""
import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
REPO = HERE.parents[2]
SLIDES = {"01": "slide_01_title", "02": "slide_02_method", "03": "slide_03_headline", "04": "slide_03b_counts_zoom",
          "05": "slide_03c_weak_side_zoom", "06": "slide_04_stretch_check", "07": "slide_05_alooh_card",
          "08": "slide_06_m02_bridge", "09": "slide_07_ai_process", "10": "slide_07c_bond_trace",
          "11": "slide_07b_commit_timeline", "13": "slide_08_limits_repo"}
APP_SHOTS = ["01_f01_banner", "02_check_a_pair", "03_how_we_know"]
LEAD, PAD_IN, PAD_OUT, GAP, HOLD = 0.4, 0.12, 0.25, 0.35, 1.8  # seconds
EXTRA_HOLD = {"09": 5.0, "10": 4.0}  # silent reading time after short lines on dense slides
FPS = 30


def run(*cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)


def duration(p):
    return float(run("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)).stdout)


def speech_span(p):
    """(start, end) of speech: silencedetect at -45 dB, padded, clamped to the file."""
    d = duration(p)
    log = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(p), "-af", "silencedetect=n=-45dB:d=0.15", "-f", "null", "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    sil = [(float(a), float(b)) for a, b in re.findall(r"silence_start: ([\d.]+)[\s\S]*?silence_end: ([\d.]+)", log)]
    start = sil[0][1] if sil and sil[0][0] < 0.01 else 0.0
    end = sil[-1][0] if sil and sil[-1][1] > d - 0.02 else d
    return max(0.0, start - PAD_IN), min(d, end + PAD_OUT)


def read_sheet():
    rows = re.findall(r"^\| (\d\d) \| [^|]+ \| (.+) \|$", (HERE / "READ_SHEET.md").read_text(encoding="utf-8"), re.M)
    return dict(rows)


def cues_for(text, max_len=42):
    """Split into cues of at most two lines of max_len characters; a sentence end closes a full first line's cue."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > max_len:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    lines.append(cur)
    return ["\n".join(lines[i:i + 2]) for i in range(0, len(lines), 2)]


def cue_starts(cues, words, t0, t1):
    """Start time of each cue: char fraction of the cue start mapped onto the recognised words' timeline."""
    total = sum(len(c.replace("\n", " ")) + 1 for c in cues)
    fr, acc = [], 0
    for c in cues:
        fr.append(acc / total)
        acc += len(c.replace("\n", " ")) + 1
    if not words:
        return [t0 + f * (t1 - t0) for f in fr]
    wc = [len(w[0].strip()) + 1 for w in words]
    cum, s = [], 0
    for n in wc:
        cum.append(s / sum(wc))
        s += n
    out = []
    for f in fr:
        k = max(i for i, c in enumerate(cum) if c <= f + 1e-9)
        out.append(min(max(t0, words[k][1]), t1))
    out[0] = t0
    return out


def fmt(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(path, cues):
    body = "\r\n\r\n".join(f"{i}\r\n{fmt(a)} --> {fmt(b)}\r\n{t.replace(chr(10), chr(13) + chr(10))}"
                           for i, (a, b, t) in enumerate(cues, 1))
    path.write_bytes((body + "\r\n").encode("utf-8"))


def build(segs, files, words, tmp, out_mp4, srt_path, screen=None, face=None):
    """segs: ordered segment ids. Returns total length in seconds."""
    texts = read_sheet()
    audio_parts, video_parts, cues, t = [], [], [], 0.0
    for n, sid in enumerate(segs):
        f = files[sid]
        a, b = speech_span(f)
        lead = LEAD if n == 0 else 0.0
        tail = (HOLD if n == len(segs) - 1 else GAP) + EXTRA_HOLD.get(sid, 0.0)
        seg_len = lead + (b - a) + tail
        wav = tmp / f"a{sid}.wav"
        run("ffmpeg", "-y", "-v", "error", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", str(f), "-af",
            f"highpass=f=80,afftdn=nf=-25,afade=t=in:d=0.03,afade=t=out:st={b - a - 0.06:.3f}:d=0.06,"
            f"adelay={int(lead * 1000)}:all=1,apad=pad_dur={tail:.3f}",
            "-ac", "1", "-ar", "48000", str(wav))
        audio_parts.append(wav)
        w = [(x[0], x[1] - a + t + lead, x[2] - a + t + lead) for x in (words or {}).get(sid, {}).get("words", [])]
        cs = cues_for(texts[sid])
        st = cue_starts(cs, w, t + lead, t + lead + (b - a))
        ends = st[1:] + [t + lead + (b - a) + min(tail, 0.6)]
        cues += [(s, e - 0.02, c) for s, e, c in zip(st, ends, cs)]
        if sid == "00":
            video_parts.append(("face", face, seg_len))
        elif sid == "12":
            video_parts.append(("screen", screen, seg_len))
        else:
            video_parts.append(("img", HERE / f"{SLIDES[sid]}.png", seg_len))
        t += seg_len
    # audio: concat, then two-pass loudnorm to -16 LUFS
    lst = tmp / f"alist_{out_mp4.stem}.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in audio_parts), encoding="utf-8")
    raw = tmp / f"raw_{out_mp4.stem}.wav"
    run("ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), str(raw))
    meas = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(raw), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
                           "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    j = json.loads(meas[meas.rindex("{"):meas.rindex("}") + 1])
    norm = tmp / f"norm_{out_mp4.stem}.wav"
    run("ffmpeg", "-y", "-v", "error", "-i", str(raw), "-af",
        f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
        f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true",
        "-ar", "48000", str(norm))
    # video: one clip per segment, same size and rate, then concat
    clips = []
    for i, (kind, src, d) in enumerate(video_parts):
        c = tmp / f"v{out_mp4.stem}_{i:02d}.mp4"
        vf = f"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:white,fps={FPS},format=yuv420p"
        if kind == "img":
            run("ffmpeg", "-y", "-v", "error", "-loop", "1", "-t", f"{d:.3f}", "-i", str(src), "-vf", vf,
                "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-tune", "stillimage", "-an", str(c))
        elif kind == "screen" and src:
            sd = duration(src)
            speed = f"setpts={d / sd:.5f}*PTS," if sd < d else ""
            run("ffmpeg", "-y", "-v", "error", "-i", str(src), "-t", f"{d:.3f}", "-vf", speed + vf,
                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-an", str(c))
        elif kind == "screen":
            shots = tmp / "shots.txt"
            per = d / len(APP_SHOTS)
            shots.write_text("".join(f"file '{(REPO / 'docs' / 'screenshots' / (s + '.png')).as_posix()}'\nduration {per:.3f}\n"
                                     for s in APP_SHOTS) + f"file '{(REPO / 'docs' / 'screenshots' / (APP_SHOTS[-1] + '.png')).as_posix()}'\n",
                             encoding="utf-8")
            run("ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(shots), "-t", f"{d:.3f}", "-vf", vf,
                "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-an", str(c))
        else:  # face clip, video only (the intro audio comes from segment 00)
            run("ffmpeg", "-y", "-v", "error", "-i", str(src), "-t", f"{d:.3f}", "-vf",
                "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080," + f"fps={FPS},format=yuv420p,tpad=stop_mode=clone:stop_duration=10",
                "-t", f"{d:.3f}", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-an", str(c))
        clips.append(c)
    vl = tmp / f"vlist_{out_mp4.stem}.txt"
    vl.write_text("".join(f"file '{p.as_posix()}'\n" for p in clips), encoding="utf-8")
    run("ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(vl), "-i", str(norm),
        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
        "-movflags", "+faststart", str(out_mp4))
    write_srt(srt_path, cues)
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio_dir")
    ap.add_argument("out_dir")
    ap.add_argument("--words")
    ap.add_argument("--screen")
    ap.add_argument("--face")
    ap.add_argument("--seg", action="append", default=[], help='re-recorded segment, e.g. --seg "09=Kayıt (15).m4a"')
    a = ap.parse_args()
    src = Path(a.audio_dir)
    names = ["Kayıt.m4a"] + [f"Kayıt ({i}).m4a" for i in range(2, 15)]
    files = {f"{i:02d}": src / n for i, n in enumerate(names)}
    for s in a.seg:
        sid, name = s.split("=", 1)
        files[sid] = src / name
    words = json.loads(Path(a.words).read_text(encoding="utf-8")) if a.words else None
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    body = [f"{i:02d}" for i in range(1, 14)]
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        t = build(body, files, words, tmp, out / "isoshift_youtube.mp4", HERE / "captions.srt", screen=a.screen)
        print(f"youtube: {t:.1f} s -> {out / 'isoshift_youtube.mp4'}")
        if a.face:
            t = build(["00"] + body, files, words, tmp, out / "isoshift_linkedin.mp4", HERE / "captions_linkedin.srt",
                      screen=a.screen, face=a.face)
            print(f"linkedin: {t:.1f} s -> {out / 'isoshift_linkedin.mp4'}")


if __name__ == "__main__":
    main()
