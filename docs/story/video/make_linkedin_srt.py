"""Build captions_linkedin.srt: captions.srt shifted by the 4 s face intro, plus one intro cue."""
import re
from pathlib import Path

HERE = Path(__file__).parent
OFFSET_MS = 4000
INTRO = "Hi, I'm Can. This is IsoShift."

TS = re.compile(r"(\d\d):(\d\d):(\d\d),(\d\d\d)")


def fmt(ms):
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def shift(match):
    h, m, s, ms = map(int, match.groups())
    return fmt(((h * 60 + m) * 60 + s) * 1000 + ms + OFFSET_MS)


src = (HERE / "captions.srt").read_text(encoding="ascii").replace("\r\n", "\n").strip()
cues = src.split("\n\n")
out = [f"1\n{fmt(0)} --> {fmt(OFFSET_MS - 200)}\n{INTRO}"]
for i, cue in enumerate(cues, start=2):
    lines = cue.split("\n")
    out.append("\n".join([str(i), TS.sub(shift, lines[1])] + lines[2:]))
(HERE / "captions_linkedin.srt").write_bytes(("\r\n\r\n".join(out) + "\r\n").replace("\n", "\r\n").replace("\r\r\n", "\r\n").encode("ascii"))
print(len(out), "cues")
