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
import os
import shutil
import re
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
REPO = HERE.parents[2]
SLIDES = {"H0": "slide_00_hook", "01": "slide_01_title", "02": "slide_02_method", "03": "slide_03_headline", "04": "slide_03b_counts_zoom",
          "05": "slide_03c_weak_side_zoom", "06": "slide_04_stretch_check", "07": "slide_05_alooh_card",
          "08": "slide_06_m02_bridge", "09": "slide_07_ai_process", "10": "slide_07c_bond_trace",
          "11": "slide_07b_commit_timeline", "13": "slide_08_limits_repo"}
APP_SHOTS = ["01_f01_banner", "02_check_a_pair", "03_how_we_know"]
LEAD, PAD_IN, PAD_OUT, GAP, HOLD = 0.4, 0.12, 0.25, 0.35, 1.8  # seconds
EXTRA_HOLD = {"01": 1.8, "03": 1.0, "09": 5.0, "10": 4.0}  # silent beats: the rule lands (01), before the scoreboard (03); reading time (09, 10)
XFADE, ZOOM = 0.45, 0.035  # crossfade seconds, push-in over one slide
MUSIC = -17  # synthesized pad under the voice, dB (None for voice only)
FPS = 30
INTRO = HERE / "anim" / "intro"  # cold open frames (make_slides_v3.intro_frames), played before the narration
REVEAL = "03"  # the score swells into this segment (the result slide)
# the rule's beat: glow pulse on these slide regions (x0, y0, x1, y1 px), timed to the end of the hook ("end") or to
# the end of the count-up ("start"), with a stronger push-in and a music swell
BEATS = {"01": ("end", [(84, 452, 1010, 545), (84, 560, 960, 775)]), "04": ("start", [(84, 195, 960, 415)])}
BEAT_ZOOM = 0.07
HERO_SEG, HERO_MAX = "07", 7.0  # OUT_DIR/hero_alooh.mp4 opens this segment, then its slide takes over
BLOOM = ("format=gbrp,split[ba][bb];[bb]gblur=sigma=11[bg];[ba][bg]blend=all_mode=screen:all_opacity=0.30,"
         "format=yuv420p")  # soft glow on the bright parts of each slide
BG_W, BG_H = 960, 540  # living background, rendered small and scaled up (it is soft anyway)


def glow_mask(src, regions, dst):
    """The slide's text pixels inside regions, black elsewhere: the source of a glow pulse."""
    import numpy as np
    from PIL import Image
    im = np.asarray(Image.open(src).convert("RGB")).astype(float)
    bg = im[5, 5]
    keep = np.zeros(im.shape[:2], bool)
    for x0, y0, x1, y1 in regions:
        keep[y0:y1, x0:x1] = True
    keep &= np.abs(im - bg).sum(2) > 60
    Image.fromarray((im * keep[..., None]).astype(np.uint8)).save(dst)


def make_score(path, tot, intro, reveal, swells=(), seed=7):
    """Generated pad (Am, F, C, G, 9 s each, overlap-added), shimmer, soft low pulse, swells at the cold open and
    at the result reveal. Mono 48 kHz WAV, base RMS about 0.17 (the old aevalsrc chord's level)."""
    import numpy as np
    import wave
    sr, rng = 48000, np.random.default_rng(seed)
    t = np.arange(int(tot * sr)) / sr
    chords = [[110.0, 130.81, 164.81, 220.0], [87.31, 130.81, 174.61, 220.0],
              [130.81, 164.81, 196.0, 261.63], [98.0, 146.83, 196.0, 246.94]]
    L = 9.0
    pad, sub, shim = np.zeros_like(t), np.zeros_like(t), np.zeros_like(t)
    for k in range(int(tot / L) + 2):
        c, t0 = chords[k % 4], k * L - L
        i0, i1 = max(0, int(t0 * sr)), min(len(t), int((t0 + 2 * L) * sr))
        if i1 <= i0:
            continue
        tt = t[i0:i1]
        w = np.sin(np.pi * (tt - t0) / (2 * L)) ** 2  # hann, hop L: sums to 1
        s = np.zeros_like(tt)
        for j, f in enumerate(c):
            for det in (-0.0016, 0.0017):
                ph = rng.uniform(0, 6.28)
                s += (0.8 if j == 0 else 0.55) * (np.sin(2 * np.pi * f * (1 + det) * tt + ph)
                                                 + 0.22 * np.sin(4 * np.pi * f * (1 + det) * tt + ph))
        pad[i0:i1] += w * s / 4
        sub[i0:i1] += w * np.sin(np.pi * c[0] * tt)  # root an octave down
        shim[i0:i1] += w * (np.sin(8 * np.pi * c[0] * tt) + 0.7 * np.sin(12 * np.pi * c[0] * tt))
    beat = (t % 2.0)  # soft heartbeat every 2 s
    pulse = np.minimum(beat / 0.04, 1.0) * np.exp(-beat / 0.45)
    shim *= 0.05 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.06 * t))
    music = pad + 0.45 * sub * pulse + shim
    base = music[t > intro + 4]
    music *= 0.17 / max(np.sqrt(np.mean(base ** 2)), 1e-9)

    def smooth(x):
        x = np.clip(x, 0, 1)
        return x * x * (3 - 2 * x)

    g = 0.35 + 2.25 * smooth(t / max(intro, 0.1))  # cold open: rises to +8 dB ...
    g = np.where(t > intro, 1.0 + 1.6 * (1 - smooth((t - intro) / 3.5)), g)  # ... then settles under the voice
    g += 0.5 * np.exp(-0.5 * ((t - reveal + 0.6) / 1.6) ** 2)  # lift into the result slide
    for ts in swells:  # the rule's beats
        g += 1.5 * np.exp(-0.5 * ((t - ts) / 1.1) ** 2)
    music = np.tanh(music * g * 1.6) / 1.6
    pcm = (np.clip(music, -1, 1) * 32000).astype("<i2")
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())


def make_background(path, tot, windows, seed=3):
    """Living background: slow glowing particles drifting left over a faint moving nebula, dark enough that it only
    shows in the empty areas (blended with 'lighten'). windows: [(t0, t1, gain)], gain 0 hides it (cold open,
    screen clip) with 0.6 s ramps."""
    import numpy as np
    rng = np.random.default_rng(seed)
    n = int(round(tot * FPS)) + 2
    P, R = 120, 9
    x0, y0 = rng.uniform(0, BG_W, P), rng.uniform(0, BG_H, P)
    z = rng.uniform(0.25, 1.0, P)
    vx, vy = -(2.5 + 7 * z), rng.uniform(-1.5, 1.5, P)
    sig = 0.9 + 2.4 * z
    tw_f, tw_p = rng.uniform(0.04, 0.18, P), rng.uniform(0, 6.28, P)
    warm = rng.random(P) < 0.15
    col = np.where(warm[:, None], [[235, 160, 80]], [[90, 170, 225]]).astype(float)
    amp = (0.30 + 0.55 * z)
    off = np.arange(-R, R + 1)
    gy, gx = np.mgrid[0:BG_H // 4, 0:BG_W // 4]
    neb_c = np.array([[24, 46, 72], [30, 40, 70]], float)

    def gain(t):
        g = 1.0
        for a, b, v in windows:
            inside = min(max((t - a + 0.6) / 0.6, 0), 1) * min(max((b + 0.6 - t) / 0.6, 0), 1)
            g = g * (1 - inside) + v * inside
        return g

    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{BG_W}x{BG_H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "fast", "-crf", "14",
                          "-pix_fmt", "yuv444p", str(path)], stdin=subprocess.PIPE)
    for k in range(n):
        t = k / FPS
        gk = gain(t)
        img = np.zeros((BG_H, BG_W, 3))
        if gk > 0.003:
            neb = np.zeros((BG_H // 4, BG_W // 4, 3))
            for j, (cx, cy, s) in enumerate(((0.25 + 0.1 * np.sin(t / 23), 0.35 + 0.1 * np.cos(t / 31), 70),
                                             (0.75 + 0.1 * np.cos(t / 27), 0.70 + 0.08 * np.sin(t / 19), 85))):
                e = np.exp(-((gx - cx * BG_W / 4) ** 2 + (gy - cy * BG_H / 4) ** 2) / (2 * (s / 2) ** 2))
                neb += e[..., None] * neb_c[j]
            img += np.repeat(np.repeat(neb, 4, 0), 4, 1)
            x = (x0 + vx * t) % (BG_W + 40) - 20
            y = (y0 + vy * t) % (BG_H + 40) - 20
            b = amp * (0.55 + 0.45 * np.sin(2 * np.pi * tw_f * t + tw_p))
            ix, iy = np.floor(x).astype(int), np.floor(y).astype(int)
            XX = ix[:, None, None] + off[None, None, :]
            YY = iy[:, None, None] + off[None, :, None]
            wts = b[:, None, None] * np.exp(-((XX - x[:, None, None]) ** 2 + (YY - y[:, None, None]) ** 2)
                                             / (2 * sig[:, None, None] ** 2))
            ok = (XX >= 0) & (XX < BG_W) & (YY >= 0) & (YY < BG_H)
            ok = ok & np.ones_like(wts, bool)
            flat = (np.broadcast_to(YY, wts.shape) * BG_W + np.broadcast_to(XX, wts.shape))[ok]
            for c in range(3):
                cw = (wts * col[:, c][:, None, None])[ok]
                img[..., c] += np.bincount(flat, weights=cw, minlength=BG_H * BG_W).reshape(BG_H, BG_W)
            img *= gk
        p.stdin.write(np.clip(img, 0, 255).astype(np.uint8).tobytes())
    p.stdin.close()
    p.wait()


def run(*cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)


def duration(p):
    return float(run("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)).stdout)


def speech_span(p):
    """(start, end) of speech: silencedetect at -45 dB, padded, clamped to the file."""
    d = duration(p)
    log = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(p), "-af", "silencedetect=n=-45dB:d=0.15", "-f", "null", "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    sil = [(float(a), float(b)) for a, b in re.findall(r"silence_start: (-?[\d.]+)[\s\S]*?silence_end: (-?[\d.]+)", log)]
    start = sil[0][1] if sil and sil[0][0] < 0.01 else 0.0
    end = sil[-1][0] if sil and sil[-1][1] > d - 0.02 else d
    return max(0.0, start - PAD_IN), min(d, end + PAD_OUT)


def read_sheet():
    rows = re.findall(r"^\| (\d\d|H0) \| [^|]+ \| (.+) \|$", (HERE / "READ_SHEET.md").read_text(encoding="utf-8"), re.M)
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
    starts = {}
    n_intro = len(list(INTRO.glob("f*.png"))) if INTRO.is_dir() and segs[0] != "00" else 0
    intro_len = 0.0
    beats, swells = {}, []
    for n, sid in enumerate(segs):
        if sid == "01" and n_intro:  # cold open after the hook: music only, so audio and captions wait for it
            d_in = n_intro / FPS
            sil = tmp / "a_intro.wav"
            run("ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", f"{d_in:.3f}",
                "-c:a", "pcm_s16le", str(sil))
            audio_parts.append(sil)
            video_parts.append(("intro", INTRO, d_in))
            t += d_in
            intro_len = t
        starts[sid] = t
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
        if sid in BEATS:
            mode, regs = BEATS[sid]
            beats[len(video_parts)] = (mode, lead + (b - a), regs)
            swells.append(t + lead + (b - a) + 0.5 if mode == "end" else t - 0.2)
        hero = out_mp4.parent / "hero_alooh.mp4"
        if sid == HERO_SEG and hero.exists() and seg_len > 4.0:  # picture only: the narration is untouched
            h = min(HERO_MAX, duration(hero), seg_len - 3.0)
            video_parts.append(("hero", hero, h))
            video_parts.append(("img", HERE / f"{SLIDES[sid]}.png", seg_len - h))
        elif sid == "00":
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
    if MUSIC:
        tot = duration(norm)
        score = tmp / f"score_{out_mp4.stem}.wav"
        make_score(score, tot, intro_len, starts.get(REVEAL, tot / 3), swells)
        mixed = tmp / f"mix_{out_mp4.stem}.wav"
        stem = tmp / f"musicstem_{out_mp4.stem}.wav"
        run("ffmpeg", "-y", "-v", "error", "-i", str(norm), "-i", str(score),
            "-filter_complex",
            f"[0]asplit=2[v][key];[1]lowpass=f=2400,aecho=0.8:0.7:240|470|730:0.32|0.22|0.14,volume={MUSIC}dB,"
            f"afade=t=in:d=0.4,afade=t=out:st={max(tot - 4, 0):.3f}:d=4[m];"
            f"[m][key]sidechaincompress=threshold=0.03:ratio=5:attack=30:release=500[mdd];[mdd]asplit=2[md][ms];"
            f"[v][md]amix=inputs=2:normalize=0:duration=first[out]",
            "-map", "[out]", "-ar", "48000", str(mixed), "-map", "[ms]", "-ar", "48000", str(stem))
        meas = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(mixed), "-af",
                               "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                              capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
        j = json.loads(meas[meas.rindex("{"):meas.rindex("}") + 1])
        mixed2 = tmp / f"mixn_{out_mp4.stem}.wav"
        run("ffmpeg", "-y", "-v", "error", "-i", str(mixed), "-af",
            f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
            f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true",
            "-ar", "48000", str(mixed2))
        mixed = mixed2
        sd = os.environ.get("ISOSHIFT_STEM_DIR")
        if sd:  # for checking the music level under the voice
            shutil.copy(stem, Path(sd) / "music_stem.wav")
            shutil.copy(norm, Path(sd) / "voice_stem.wav")
        norm = mixed
    # video: one clip per segment (slow push-in on slides), joined by crossfades that keep the narration timing
    clips, n = [], len(video_parts)
    for i, (kind, src, d) in enumerate(video_parts):
        dd = d + (XFADE if i < n - 1 else 0.0)  # each clip overlaps the next by XFADE
        c = tmp / f"v{out_mp4.stem}_{i:02d}.mp4"
        vf = f"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:white,fps={FPS},format=yuv420p"
        if kind == "img":
            anim = HERE / "anim" / Path(src).stem
            nf = len(list(anim.glob("f*.png"))) if anim.is_dir() else 0
            lead_hold = XFADE if i > 0 else 0.0  # let the crossfade finish before the slide starts building
            a_len = lead_hold + nf / FPS
            still = dd - a_len if nf and dd > a_len + 1.0 else dd
            frames = int(round(still * FPS))
            z = BEAT_ZOOM if i in beats else ZOOM
            push = (f"scale=2880:1620,zoompan=z='1+{z}*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                    f":d=1:s=1920x1080:fps={FPS}," + BLOOM)
            cs = tmp / f"s{out_mp4.stem}_{i:02d}.mp4"
            if i in beats:  # glow pulse on the rule's numbers and line
                mode, trel, regs = beats[i]
                st_in = max(0.1, trel - 0.25 - (a_len if still < dd else 0.0)) if mode == "end" else 0.15
                mask = tmp / f"glow_{out_mp4.stem}_{i:02d}.png"
                glow_mask(src, regs, mask)
                run("ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-loop", "1", "-t", f"{still:.3f}", "-i", str(src),
                    "-framerate", str(FPS), "-loop", "1", "-t", f"{still:.3f}", "-i", str(mask), "-filter_complex",
                    f"[1]format=rgb24,fade=t=in:st={st_in:.3f}:d=0.4,fade=t=out:st={st_in + 0.8:.3f}:d=1.8,format=gbrp,"
                    f"split[m1][m2];[m1]gblur=sigma=26,lutrgb=r=val*2.4:g=val*2.4:b=val*2.4[mb];"
                    f"[mb][m2]blend=all_mode=lighten[env];[0]format=gbrp[s0];[s0][env]blend=all_mode=screen:all_opacity=0.9,"
                    + push, "-frames:v", str(frames), "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-an", str(cs))
            else:
                run("ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-loop", "1", "-t", f"{still:.3f}", "-i", str(src),
                    "-vf", push, "-frames:v", str(frames), "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-an", str(cs))
            if still < dd:  # build-up frames first, then the slow push-in on the final still
                ca = tmp / f"a{out_mp4.stem}_{i:02d}.mp4"
                run("ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-i", str(anim / "f%03d.png"), "-vf",
                    f"tpad=start_mode=clone:start_duration={lead_hold:.3f},fps={FPS}," + BLOOM,
                    "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-an", str(ca))
                lst2 = tmp / f"c{out_mp4.stem}_{i:02d}.txt"
                lst2.write_text(f"file '{ca.as_posix()}'" + chr(10) + f"file '{cs.as_posix()}'" + chr(10), encoding="utf-8")
                run("ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst2), "-c", "copy", str(c))
            else:
                cs.replace(c)
        elif kind == "intro":  # glow (blurred copy, screen blend) and a slow push through the lattice
            nfr = int(round(dd * FPS))
            run("ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-i", str(Path(src) / "f%03d.png"), "-vf",
                f"tpad=stop_mode=clone:stop_duration={XFADE + 0.2:.3f},format=gbrp,split[a][b];[b]gblur=sigma=16[g];"
                f"[a][g]blend=all_mode=screen:all_opacity=0.85,scale=2880:1620,"
                f"zoompan=z='1.10-0.10*on/{nfr}':x='iw/2-(iw/zoom/2)+40*on/{nfr}':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps={FPS},"
                f"format=yuv420p", "-frames:v", str(nfr), "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-an", str(c))
        elif kind == "hero":
            run("ffmpeg", "-y", "-v", "error", "-i", str(src), "-vf",
                vf + f",tpad=stop_mode=clone:stop_duration={XFADE + 1}", "-t", f"{dd:.3f}",
                "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-an", str(c))
        elif kind == "screen" and src:
            sd = duration(src)
            speed = f"setpts={d / sd:.5f}*PTS," if sd < d else ""
            run("ffmpeg", "-y", "-v", "error", "-i", str(src), "-vf",
                speed + vf + f",tpad=stop_mode=clone:stop_duration={XFADE + 1}", "-t", f"{dd:.3f}",
                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-an", str(c))
        elif kind == "screen":
            shots = tmp / "shots.txt"
            per = dd / len(APP_SHOTS)
            shots.write_text("".join(f"file '{(REPO / 'docs' / 'screenshots' / (s + '.png')).as_posix()}'" + chr(10) + f"duration {per:.3f}" + chr(10)
                                     for s in APP_SHOTS) + f"file '{(REPO / 'docs' / 'screenshots' / (APP_SHOTS[-1] + '.png')).as_posix()}'" + chr(10),
                             encoding="utf-8")
            run("ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(shots), "-t", f"{dd:.3f}", "-vf", vf,
                "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-an", str(c))
        else:  # face clip, video only (the intro audio comes from segment 00)
            run("ffmpeg", "-y", "-v", "error", "-i", str(src), "-vf",
                "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080," + f"fps={FPS},format=yuv420p,tpad=stop_mode=clone:stop_duration=10",
                "-t", f"{dd:.3f}", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-an", str(c))
        clips.append(c)
    inputs, chain, prev, off = [], [], "[0:v]", 0.0
    for c in clips:
        inputs += ["-i", str(c)]
    for i in range(1, n):
        off += video_parts[i - 1][2]
        out = f"[x{i}]"
        chain.append(f"{prev}[{i}:v]xfade=transition=fade:duration={XFADE}:offset={off:.3f}{out}")
        prev = out
    total = sum(p[2] for p in video_parts)
    hide, acc = [], 0.0
    for kind, _, d in video_parts:
        if kind == "intro":
            hide.append((-1.0, acc + d - 0.3, 0.0))
        elif kind != "img":
            hide.append((acc, acc + d + XFADE, 0.0))
        acc += d
    bgv = tmp / f"bg_{out_mp4.stem}.mp4"
    make_background(bgv, total, hide)
    inputs += ["-i", str(bgv)]
    chain.append(f"{prev}format=gbrp[comp];[{n}:v]scale=1920:1080:flags=bicubic,format=gbrp[bgl];"
                 f"[comp][bgl]blend=all_mode=lighten:shortest=1,"
                 f"fade=t=in:st=0:d=1.2,fade=t=out:st={total - 2.0:.3f}:d=2.0,format=yuv420p[vout]")
    run("ffmpeg", "-y", "-v", "error", *inputs, "-i", str(norm), "-filter_complex", ";".join(chain),
        "-map", "[vout]", "-map", f"{n + 1}:a", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out_mp4))
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
    if "H0" in files:
        body = ["H0"] + body
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
