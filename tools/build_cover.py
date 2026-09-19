"""Compose the publication cover from actual dark-mode browser captures.

Inputs were captured at the Reference preset, simultaneous addition, 72 h.
Trace: 100,000 initial surface receptors/cell; A=8.25404185268019 nM, S=3 nM.
No scientific data or UI elements are synthesized by this compositor.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures"
BG = "#101319"
FG = "#e5e9f0"
MUTED = "#a4afbd"
CYAN = "#70d4df"
BORDER = "#394452"
FONT = Path("/usr/share/fonts/truetype/dejavu")
TITLE = "You Rescued the Curve. Did You Rescue Delivery?"
SUBTITLE = (
    "How a disappearing hook can conceal a persistent payload deficit, and what "
    "an interactive organoid model reveals about the gap between delivery and "
    "cell-death fluorescence."
)


def font(size, bold=False):
    return ImageFont.truetype(str(FONT / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")), size)


def compose():
    im = Image.new("RGB", (1920, 1080), BG)
    d = ImageDraw.Draw(im)
    def text(x, y, s, size, color=FG, bold=False):
        d.text((x,y),s,font=font(size,bold),fill=color)
    def capture(name, x, y, width):
        img=Image.open(OUT/"cover-inputs"/name).convert("RGB")
        img=img.resize((width,round(width*img.height/img.width)),Image.Resampling.LANCZOS)
        im.paste(img,(x,y))
        d.rounded_rectangle((x-1,y-1,x+width,y+img.height),radius=12,outline=BORDER,width=2)
        return img.height

    d.line((80,106,145,106),fill=CYAN,width=3)
    text(80,126,"Data-Rich, Insight-Poor — CCXXIV",25,CYAN)
    for i,line in enumerate(["You Rescued","the Curve.","Did You Rescue","Delivery?"]):
        text(76,200+i*77,line,68,bold=True)
    lines = wrap(SUBTITLE, font(28), 700, d)
    for i,line in enumerate(lines):
        text(80,545+i*41,line,28,MUTED)
    d.line((80,835,766,835),fill=BORDER,width=2)
    text(80,907,"SYNTHETIC · UNCALIBRATED",23,CYAN)
    text(80,946,"github.com/dataRichinsightPoor/",22,MUTED)
    text(80,974,"organoid-hook-model",22,MUTED)
    text(80,1020,"Ermelinda Damko",24,FG)

    text(860,125,"THE PUBLIC MODEL · 72 HOURS · ACCUMULATION",22,CYAN)
    capture("reference-curves.png",860,174,980)
    text(864,584,"Same biology. Three secondary concentrations.",25,MUTED)
    text(864,618,"A recovered endpoint can conceal reduced delivery.",25,MUTED)
    text(860,684,"FOLLOW ONE SIMULATION",22,CYAN)
    capture("reference-trace.png",860,729,980)
    text(864,1031,"Reference: primary 8.254 nM · secondary 3 nM",20,MUTED)
    im.save(OUT/"cover-hook-system.png",optimize=True)
    im.resize((1200,675),Image.Resampling.LANCZOS).save(OUT/"cover-hook-system-linkedin.png",optimize=True)
    print("Saved cover-hook-system.png (1920×1080) and LinkedIn edition (1200×675).")


def wrap(value, face, width, draw):
    lines = []
    for word in value.split():
        if not lines or draw.textlength(lines[-1] + " " + word, font=face) > width:
            lines.append(word)
        else:
            lines[-1] += " " + word
    assert " ".join(lines) == value
    return lines


def compose_substack():
    """A dedicated 1456×1048 layout, not a crop of the widescreen cover."""
    im = Image.new("RGB", (1456, 1048), BG)
    d = ImageDraw.Draw(im)
    def text(x, y, value, size, color=FG, bold=False):
        d.text((x,y), value, font=font(size,bold), fill=color)
    d.line((56,50,112,50), fill=CYAN, width=3)
    text(56,69,"Data-Rich, Insight-Poor — CCXXIV",22,CYAN)
    for i,line in enumerate(["You Rescued the Curve.", "Did You Rescue Delivery?"]):
        text(52,125+i*78,line,66,bold=True)
    for i,line in enumerate(wrap(SUBTITLE, font(26), 1320, d)):
        text(56,303+i*37,line,26,MUTED)
    d.line((56,446,1400,446), fill=BORDER, width=1)
    text(56,475,"THE PUBLIC MODEL · 72 HOURS · ACCUMULATION",20,CYAN)
    graph = Image.open(OUT/"cover-inputs/reference-curves.png").convert("RGB")
    graph = graph.resize((900,round(900*graph.height/graph.width)),Image.Resampling.LANCZOS)
    im.paste(graph,(48,521))
    text(987,533,"A recovered endpoint",22)
    text(987,568,"can conceal",22)
    text(987,603,"reduced delivery.",22,CYAN,True)
    text(987,690,"5,304 synthetic",22,MUTED)
    text(987,725,"simulations.",22,MUTED)
    text(987,794,"Explore the model.",22)
    text(987,829,"Inspect the equations.",22)
    text(56,944,"SYNTHETIC · UNCALIBRATED",19,CYAN)
    text(56,985,"github.com/dataRichinsightPoor/organoid-hook-model",18,MUTED)
    text(1190,984,"Ermelinda Damko",19)
    im.save(OUT/"cover-hook-system-substack.png",optimize=True)
    print("Saved cover-hook-system-substack.png (1456×1048).")


if __name__ == "__main__":
    compose()
    compose_substack()
