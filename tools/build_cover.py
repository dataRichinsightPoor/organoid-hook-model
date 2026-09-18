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
    text(80,126,"DATA-RICH, INSIGHT-POOR",25,CYAN)
    for i,line in enumerate(["The Hook Is a","Property of","the System"]):
        text(76,216+i*95,line,77,bold=True)
    for i,line in enumerate([
        "Receptor copies are not payload delivery.",
        "Payload delivery is not fluorescence.",
        "Follow the accounting in a public model.",
    ]):
        text(80,548+i*43,line,27,MUTED)
    d.line((80,711,766,711),fill=BORDER,width=2)
    for x,value,lines in [
        (80,"5,304",["synthetic","simulations"]),
        (327,"4",["addition","orders"]),
        (554,"60",["coupled","model states"]),
    ]:
        text(x,737,value,44,CYAN,True)
        for j,line in enumerate(lines):
            text(x,795+j*30,line,24,MUTED)
    text(80,907,"SYNTHETIC · UNCALIBRATED",23,CYAN)
    text(80,946,"github.com/dataRichinsightPoor/",22,MUTED)
    text(80,974,"organoid-hook-model",22,MUTED)
    text(80,1020,"Ermelinda Damko",24,FG)

    text(860,125,"THE PUBLIC MODEL · 72 HOURS · NO WASH",22,CYAN)
    capture("reference-curves.png",860,174,980)
    text(864,584,"Same biology. Three secondary concentrations.",25,MUTED)
    text(864,618,"A recovered endpoint can conceal reduced delivery.",25,MUTED)
    text(860,684,"FOLLOW ONE SIMULATION",22,CYAN)
    capture("reference-trace.png",860,729,980)
    text(864,1031,"Reference: primary 8.254 nM · secondary 3 nM",20,MUTED)
    im.save(OUT/"cover-hook-system.png",optimize=True)
    im.resize((1200,675),Image.Resampling.LANCZOS).save(OUT/"cover-hook-system-linkedin.png",optimize=True)
    print("Saved cover-hook-system.png (1920×1080) and LinkedIn edition (1200×675).")


if __name__ == "__main__":
    compose()
