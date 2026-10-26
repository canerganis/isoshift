import re
import pathlib

here = pathlib.Path(__file__).parent
t = (here / "M03_note.tex").read_text(encoding="utf-8")
body = t[t.index(r"\begin{abstract}"):t.index(r"\end{document}")]
for a, b in [(r"\begin{abstract}", "<h3>Abstract</h3><p>"), (r"\end{abstract}", "</p>"),
             (r"\begin{equation}", "$$"), (r"\end{equation}", "$$"),
             (r"\AA\ ", "Å "), (r"\AA", "Å"), (r"\%", "%"), (r"\c{s}", "ş"), ('\\"u', "ü"), (r"\ ", " ")]:
    body = body.replace(a, b)
body = re.sub(r"\\section\*?\{([^}]*)\}", r"</p><h3>\1</h3><p>", body)
body = re.sub(r"\\href\{([^}]*)\}\{([^}]*)\}", r'<a href="\1">\2</a>', body)
body = re.sub(r"\\url\{([^}]*)\}", r'<a href="\1">\1</a>', body)
body = re.sub(r"\\emph\{([^}]*)\}", r"<i>\1</i>", body)
body = body.replace("``", "&ldquo;").replace("''", "&rdquo;")
body = re.sub(r"\\texttt\{([^}]*)\}", lambda m: "<code>" + m.group(1).replace("\\_", "_") + "</code>", body)
body = body.replace("\n\n", "</p><p>")
head = """<!doctype html><html><head><meta charset="utf-8"><title>M03 short-bond slope</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"></script>
<style>body{font-family:Georgia,serif;max-width:46em;margin:2.5em auto;line-height:1.45;font-size:11pt;color:#111}
h1{font-size:17pt;text-align:center;margin-bottom:.3em}.au{text-align:center;font-size:10pt}
h3{font-size:12pt;margin-top:1.2em}code{font-size:9.5pt}a{color:#1a4d8f}</style></head><body>
<h1>An analytic estimate of the short-bond slope for the H/D isotope effect on polymorph stability</h1>
<div class="au">Muhammet Can Ergani&#351;<br>Independent researcher, Ankara, T&uuml;rkiye<br>
ORCID <a href="https://orcid.org/0009-0001-1397-6366">0009-0001-1397-6366</a><br>23 October 2026</div>
"""
tail = """</p><script>renderMathInElement(document.body,{delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}]});</script></body></html>"""
(here / "M03_note.html").write_text(head + body + tail, encoding="utf-8")
print("ok")
