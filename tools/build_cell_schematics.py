"""Draw qualitative cellular schematics of the committed, uncalibrated model.

These diagrams explain model structure, not molecular anatomy or simulated
inventories. Rate labels are read from the same presets used to build the atlas.
No numerical datasets are regenerated.
"""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont
from organoid_hook import Parameters
from build_atlas import TRAFFIC, ORDERS
from build_mechanism_lab import CASES

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures"
BG, PANEL, IN = "#101319", "#171d26", "#1d2935"
FG, MUTED, LINE = "#e5e9f0", "#b6c1cf", "#647489"
CYAN, GOLD = "#70d4df", "#f1b86c"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans"


class Canvas:
    def __init__(self, h, title, subtitle):
        self.im = Image.new("RGB", (2000, h), BG)
        self.d = ImageDraw.Draw(self.im)
        self.text(60, 35, "Data-Rich, Insight-Poor — CCXXIV", 27, MUTED)
        self.text(60, 88, title, 52, FG, True)
        self.text(60, 163, subtitle, 29, MUTED)

    def text(self, x, y, text, size=30, color=FG, bold=False):
        font = ImageFont.truetype(FONT + ("-Bold.ttf" if bold else ".ttf"), size)
        self.d.text((x, y), text, fill=color, font=font, spacing=12)

    def line(self, pts, color=LINE, width=4):
        self.d.line(pts, fill=color, width=width, joint="curve")

    def arrow(self, pts, color=CYAN, width=4):
        self.line(pts, color, width)
        x, y = pts[-1]
        px, py = pts[-2]
        a = math.atan2(y - py, x - px)
        self.d.polygon([(x, y),
                        (x - 14 * math.cos(a - .45), y - 14 * math.sin(a - .45)),
                        (x - 14 * math.cos(a + .45), y - 14 * math.sin(a + .45))],
                       fill=color)

    def circle(self, x, y, r, fill=IN, outline=LINE, width=3):
        self.d.ellipse((x-r, y-r, x+r, y+r), fill=fill, outline=outline, width=width)

    def antibody(self, x, y, secondary=False):
        self.line([(x-16, y-18), (x, y), (x+16, y-18)], CYAN, 5)
        self.line([(x, y), (x, y+23)], CYAN, 5)
        if secondary:
            self.d.rectangle((x+12, y-30, x+33, y-9), fill=GOLD)

    def receptor(self, x, y, primary=True, secondary=True):
        self.line([(x-16, y-12), (x-16, y), (x+16, y), (x+16, y-12)], FG, 5)
        self.line([(x, y), (x, y+28)], FG, 5)
        if primary:
            self.antibody(x, y-35, secondary)

    def card(self, x, y, w, h, label):
        self.d.rounded_rectangle((x, y, x+w, y+h), 15, fill=PANEL)
        self.text(x+28, y+22, label, 35, FG, True)

    def footer(self, y, extra="Arrows are qualitative; icon counts are not molecular inventories."):
        self.text(60, y, "Conceptual schematics of an uncalibrated model • Not to scale", 28, MUTED)
        self.text(60, y+43, extra, 26, MUTED)

    def save(self, name):
        p = OUT / name
        self.im.save(p, optimize=True, dpi=(200, 200))
        print(p.name, self.im.size)


def cell(c, x, y, mode="reference"):
    """Same cellular cutaway, with only the affected step highlighted."""
    c.d.ellipse((x+10, y+25, x+380, y+345), fill=IN, outline=LINE, width=4)
    c.receptor(x+185, y+30)
    c.text(x+230, y+5, "T", 29, CYAN, True)
    c.arrow([(x+185, y+64), (x+185, y+109)])
    c.circle(x+185, y+156, 44)
    c.receptor(x+185, y+164)
    c.text(x+243, y+142, "W", 29, CYAN, True)
    # Return of intact endosomal complex to the surface.
    c.arrow([(x+142, y+156), (x+80, y+156), (x+80, y+76)], MUTED)
    c.text(x+24, y+178, "recycle", 23, MUTED)
    release_color = GOLD if mode == "poor_release" else CYAN
    c.arrow([(x+181, y+201), (x+137, y+246)], release_color)
    c.circle(x+120, y+269, 27, outline=release_color)
    c.text(x+110, y+250, "P", 29, release_color, True)
    c.arrow([(x+150, y+269), (x+235, y+269)])
    qcolor = GOLD if mode in ("fast_repair", "slow_repair") else FG
    c.circle(x+269, y+269, 29, outline=qcolor)
    c.text(x+256, y+250, "Q", 29, qcolor, True)
    c.arrow([(x+269, y+301), (x+269, y+335)], qcolor)
    c.text(x+191, y+355, "recovery", 26, qcolor)
    if mode == "poor_release":
        c.text(x+16, y+219, "η ↓", 28, GOLD, True)
    if mode in ("fast_repair", "slow_repair"):
        c.text(x+305, y+308, "↑" if mode == "fast_repair" else "↓", 31, GOLD, True)


def organoid(c, x, y, sparse=False):
    """Three-shell tissue section; symbol density is purely schematic."""
    for r, fill in [(162, "#263441"), (111, "#202d38"), (60, IN)]:
        c.circle(x+195, y+185, r, fill=fill)
    for radius, count in [(139, 9), (83, 5), (23, 3)]:
        for i in range(count):
            a = 2*math.pi*i/count
            xx, yy = x+195+radius*math.cos(a), y+185+radius*math.sin(a)
            c.circle(xx, yy, 17, fill=PANEL, outline=LINE)
            if not sparse or radius != 23 or i == 0:
                c.line([(xx-7, yy-17), (xx-7, yy-24),
                        (xx+7, yy-24), (xx+7, yy-17)], CYAN, 3)
    c.arrow([(x+5, y+185), (x+95, y+185)], GOLD)
    c.text(x+36, y+370, "rim", 26, MUTED)
    c.text(x+246, y+370, "core", 26, MUTED)
    c.line([(x+68, y+365), (x+79, y+291)])
    c.line([(x+277, y+365), (x+215, y+212)])
    if sparse:
        c.text(x+85, y+5, "target-poor core", 27, GOLD)
    else:
        c.text(x+40, y+5, "slower bath → core access", 26, GOLD)


def mechanism_figure():
    c = Canvas(2780, "Where the scenarios act", "Seven mechanism-lab cases, located along the delivery-to-readout sequence")
    sequence = ["reference", "poor_release", "fast_repair", "slow_repair",
                "reporter_loss", "core_low", "transport", "key"]
    descriptions = {
        "reference": ("Reference", [
            "Surface assembly T is internalized.",
            "Endosomal W can recycle or",
            "be processed into productive P.",
            "P drives reversible damage Q;",
            "death and reporter entry follow.",
            "", "η = 0.2; recovery half-time = 24 h"]),
        "poor_release": ("Poor productive release", [
            "The bottleneck is after uptake.",
            "η falls from 0.2 to 0.001.",
            "The same processed W supplies",
            "less productive payload P.",
            "", "Binding and trafficking equations",
            "are otherwise unchanged."]),
        "fast_repair": ("Fast protein recovery", [
            "Recovery removes Q faster.",
            "Half-time: 24 h → 2 h.",
            "Binding and delivery are unchanged;",
            "less damage may persist long",
            "enough for death commitment.",
            "", "Q is a generic damage/deficit state."]),
        "slow_repair": ("Slow protein recovery", [
            "Recovery removes Q more slowly.",
            "Half-time: 24 h → 96 h.",
            "Binding and delivery are unchanged;",
            "damage persists longer and can",
            "accumulate across the exposure.",
            "", "This is not a receptor-turnover change."]),
        "reporter_loss": ("Reporter persistence stress test", [
            "Loss occurs after permeabilization.",
            "Reporter-accessible material D",
            "moves into the unobserved state X.",
            "The death trajectory is unchanged.",
            "", "Loss rate: 0 → 0.08 h⁻¹.",
            "Hypothesis only; off by default."]),
        "core_low": ("Target-poor core", [
            "Receptor copies vary with position.",
            "Core/rim copy ratio: 1 → 0.03.",
            "Core cells remain in the model;",
            "they carry fewer surface targets.",
            "", "Geometry and diffusion retain",
            "their reference values."]),
        "transport": ("Large / slow transport", [
            "Radius: 150 → 250 μm.",
            "Diffusion: 3 → 0.1 μm²/s.",
            "Larger distance and slower access",
            "can favor peripheral capture.",
            "", "Three-shell stress test;",
            "not spatially converged."]),
    }
    for i, key in enumerate(sequence):
        x, y = 40+(i%2)*980, 240+(i//2)*600
        if key == "key":
            c.card(x, y, 960, 575, "Reading the cell")
            c.receptor(x+72, y+151)
            c.text(x+150, y+91, "T  Surface receptor–primary–secondary", 29)
            c.text(x+150, y+140, "W  Internalized ternary complex", 29)
            c.text(x+45, y+237, "P  Productive intracellular payload", 31, CYAN)
            c.text(x+45, y+291, "Q  Reversible damage / protein deficit", 31)
            c.text(x+45, y+369, "Cyan Y: primary antibody", 28, CYAN)
            c.text(x+45, y+414, "Gold square: secondary–toxin conjugate", 28, GOLD)
            c.text(x+45, y+488, "Gold arrows mark the changed step.", 29, GOLD)
            continue
        title, lines = descriptions[key]
        c.card(x, y, 960, 575, title)
        if key in ("transport", "core_low"):
            organoid(c, x+16, y+103, sparse=key == "core_low")
        elif key == "reporter_loss":
            c.d.ellipse((x+44, y+145, x+384, y+422), fill=IN, outline=LINE, width=4)
            c.text(x+75, y+171, "membrane compromised", 22, MUTED)
            c.circle(x+142, y+280, 42, outline=CYAN)
            c.text(x+128, y+257, "D", 34, CYAN, True)
            c.arrow([(x+190, y+280), (x+272, y+280)], GOLD)
            c.circle(x+312, y+280, 35, outline=MUTED)
            c.text(x+299, y+257, "X", 34, MUTED, True)
            c.text(x+79, y+348, "observable → lost", 28, GOLD)
            c.text(x+59, y+460, "Loss ≠ survival or recovery", 26, MUTED)
        else:
            cell(c, x+15, y+115, key)
        for j, line in enumerate(lines):
            c.text(x+430, y+115+j*49, line, 25 if len(line)>37 else 27,
                   GOLD if ("→" in line or "η =" in line) else MUTED)
    c.footer(2660)
    c.save("cell-scenarios.png")


def traffic_figure():
    c = Canvas(1860, "Receptor traffic changes the route", "Three joint trafficking presets; receptor degradation is varied separately")
    names = ["Slow internalization", "Rapid recycling", "Endosomal retention"]
    explanations = [
        ["Slower entry into the internal pool.",
         "Longer surface residence does not",
         "establish productive payload delivery."],
        ["Faster uptake with rapid return.",
         "Recycling returns intact receptor",
         "species; it competes with processing."],
        ["Uptake with relatively slow return.",
         "Retention gives processing more time,",
         "but does not guarantee greater killing."],
    ]
    for i, (key, rates) in enumerate(TRAFFIC.items()):
        x, y = 40, 245+i*475
        c.card(x, y, 1920, 450, names[i])
        c.d.ellipse((85, y+142, 548, y+415), fill=IN, outline=LINE, width=4)
        c.receptor(293, y+145)
        c.arrow([(293, y+180), (293, y+254)], CYAN, 3 if key=="slow" else 7)
        c.circle(293, y+308, 45)
        c.text(278, y+286, "W", 33, FG)
        c.arrow([(242, y+308), (156, y+308), (156, y+186)], GOLD,
                8 if key=="recycling" else 3)
        c.text(91, y+353, "return", 25, GOLD)
        c.arrow([(345, y+308), (467, y+308)], MUTED)
        c.text(379, y+348, "process", 25, MUTED)
        c.text(593, y+111, "Internalization rates (h⁻¹)", 31, CYAN, True)
        c.text(593, y+165, f"Free R: {rates['kint_free']:g}", 31)
        c.text(593, y+217, f"Primary-bound B: {rates['kint_primary']:g}", 31)
        c.text(593, y+269, f"Ternary T: {rates['kint_ternary']:g}", 31)
        c.text(593, y+340, f"Recycling: {rates['krecycle']:g} h⁻¹", 31, GOLD)
        for j, s in enumerate(explanations[i]):
            c.text(1190, y+133+j*55, s, 29, MUTED)
        c.text(1190, y+330, "Arrow weights are qualitative.", 27, MUTED)
    c.text(60, 1704, "Independent atlas axes: 10⁴ / 10⁵ / 10⁶ starting copies per cell; endosomal half-time 4 / 24 / 96 h.", 29)
    c.footer(1760, "Presets alter several rates together. They are not single-parameter causal comparisons.")
    c.save("cell-trafficking.png")


def addition_figure():
    c = Canvas(2210, "Addition order changes the starting state", "Accumulation exposure: added reagents remain; binding and trafficking continue")
    labels = ["Simultaneous", "Primary first", "Secondary first", "Precomplexed"]
    explanations = [
        ["Both reagents are available at t = 0.",
         "Soluble C and surface T can form",
         "through either assembly route."],
        ["Primary can bind and internalize",
         "before secondary arrives at 6 h.",
         "No toxin delivery in the primary-only interval."],
        ["Secondary remains available in the bath.",
         "The model has no specific entry route",
         "for S alone; primary arrives at 6 h."],
        ["An equilibrium mixture enters at t = 0:",
         "free A, free S, and soluble complex C.",
         "C can bind receptor; it is not a dead end."],
    ]
    assert ORDERS == ["simultaneous", "primary_first", "secondary_first", "precomplexed"]
    for i, key in enumerate(ORDERS):
        y = 245+i*435
        c.card(40, y, 1920, 410, labels[i])
        # State at the first addition, not a simulated snapshot.
        c.d.ellipse((90, y+197, 505, y+380), fill=IN, outline=LINE, width=4)
        c.receptor(292, y+200, primary=False, secondary=False)
        c.text(228, y+317, "cell", 28, MUTED)
        if key != "secondary_first":
            c.antibody(171, y+139, secondary=key=="precomplexed")
            c.text(129, y+84, "C" if key=="precomplexed" else "A", 28, CYAN)
        if key != "primary_first":
            c.d.rectangle((367, y+123, 393, y+149), fill=GOLD)
            c.text(369, y+81, "S", 28, GOLD)
        if key == "precomplexed":
            c.antibody(262, y+102)
            c.text(298, y+88, "A", 26, CYAN)
        if key == "primary_first":
            c.arrow([(171, y+178), (257, y+201)], CYAN)
        c.text(585, y+98, "0 h", 31, FG, True)
        c.text(888, y+98, "6 h", 31, FG, True)
        c.arrow([(613, y+175), (1009, y+175)], MUTED)
        c.line([(613, y+160), (613, y+192)], FG)
        c.line([(917, y+160), (917, y+192)], FG)
        first = {"simultaneous":"A + S", "primary_first":"A",
                 "secondary_first":"S", "precomplexed":"A + S + C"}[key]
        c.text(567, y+220, first, 32, CYAN)
        if key in ("primary_first", "secondary_first"):
            c.text(888, y+220, "+ S" if key=="primary_first" else "+ A", 32, GOLD)
        else:
            c.text(841, y+220, "retain", 30, MUTED)
        for j, s in enumerate(explanations[i]):
            c.text(1090, y+118+j*53, s, 27, MUTED)
        c.text(1090, y+321, "Joint exposure starts: " + ("6 h" if i in (1,2) else "0 h"), 29, CYAN)
    c.text(60, 2014, "Once both reagents are present:  A + S ⇌ C     A + R ⇌ B     S + B ⇌ T     C + R ⇌ T", 31)
    c.footer(2091, "Drawings show initial availability, not occupancies. Atlas endpoints are timed from the first addition.")
    c.save("cell-addition-orders.png")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    # Fail rather than silently letting the figure prose drift from preset values.
    p = Parameters()
    assert (p.release_efficiency, p.protein_recovery_half_life_h,
            p.radius_um, p.diffusion_um2_s, p.core_copy_ratio, p.reporter_loss_h) == (.2, 24, 150, 3, 1, 0)
    expected = {"poor_release": {"release_efficiency": .001},
                "fast_repair": {"protein_recovery_half_life_h": 2},
                "slow_repair": {"protein_recovery_half_life_h": 96},
                "reporter_loss": {"reporter_loss_h": .08},
                "core_low": {"core_copy_ratio": .03},
                "transport": {"radius_um": 250, "diffusion_um2_s": .1}}
    assert set(CASES) == {"reference", *expected}
    assert all(CASES[k][1] == v for k, v in expected.items())
    mechanism_figure()
    traffic_figure()
    addition_figure()
