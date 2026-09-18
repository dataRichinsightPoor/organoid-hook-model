"""Render the SAME Markdown article and equations into static browser pages."""
import html
import re
import shutil
from pathlib import Path
import markdown

ROOT=Path(__file__).resolve().parents[1]
for name,source,title in [
 ("equations.html","model.md","Equations & variables"),
 ("article.html","the-hook-is-a-property-of-the-system.pplx.md","The Hook Is a Property of the System"),
]:
    text=(ROOT/"docs"/source).read_text()
    math=[]
    def protect(m):
        math.append(m.group(0))
        return f"MATHPLACEHOLDER{len(math)-1}END"
    text=re.sub(r"\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)",protect,text)
    body=markdown.markdown(text,extensions=["tables","fenced_code"])
    for i,value in enumerate(math):
        body=body.replace(f"MATHPLACEHOLDER{i}END",html.escape(value))
    body=body.replace("../figures/","figures/")
    page=f"""<!doctype html><html lang="en" data-theme="light"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | Organoid Hook Model</title>
<link href="https://api.fontshare.com/v2/css?f[]=satoshi@400,500,700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
<script>window.MathJax={{tex:{{inlineMath:[['\\\\(','\\\\)']],displayMath:[['\\\\[','\\\\]']]}},options:{{enableMenu:true}}}};</script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-mml-chtml.js"></script>
</head><body><header><div class="brand">Data-Rich, Insight-Poor / Organoid Hook Model</div>
<nav><a href="index.html">Open explorer</a><a href="equations.html">Equations</a><a href="article.html">Article</a><button id="reader-theme">Dark mode</button></nav></header>
<main class="reader"><p class="math-help">Synthetic, uncalibrated research software · v0.1.0.
Equations render in your browser; if the math service is blocked, the complete TeX remains visible.
<a href="https://github.com/dataRichinsightPoor/organoid-hook-model/blob/main/docs/{source}">View the underlying Markdown</a>.</p>
{body}</main><script>document.getElementById('reader-theme').onclick=function(){{var d=document.documentElement.dataset.theme==='dark';document.documentElement.dataset.theme=d?'light':'dark';this.textContent=d?'Dark mode':'Light mode';}};</script></body></html>"""
    (ROOT/"viewer"/name).write_text(page)
(ROOT/"viewer/figures").mkdir(exist_ok=True)
for p in (ROOT/"figures").glob("*.png"):
    shutil.copyfile(p,ROOT/"viewer/figures"/p.name)
print("Built article.html, equations.html, and browser figure copies.")
