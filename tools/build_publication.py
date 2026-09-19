"""Export the editorial manuscript with portable inline notation and image slots."""
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "publication"
OUT.mkdir(exist_ok=True)
PUBLIC = "https://datarichinsightpoor.github.io/organoid-hook-model"
INLINE = {
    r"C_{\mathrm{eq}}": "Ceq", r"T_{\mathrm{eq}}": "Teq",
    "A_0": "A₀", "S_0": "S₀", "R_0": "R₀", "K_A": "KA", "K_S": "KS",
    r"\Sigma=A_0+S_0+K_S": "Σ = A₀ + S₀ + KS",
    "W_c": "Wc", r"k_{\mathrm{deg}}": "kdeg", "d": "d", r"\eta": "η",
    "P": "P", "P_{50}": "P₅₀", "t": "t", "k_P": "kP",
    r"\eta d\,k_{\mathrm{deg}}W_c": "η d kdeg Wc",
    "j": "j", "u": "u", "r_j(u)": "rⱼ(u)",
    r"k_{\mathrm{perm}}E_j(u)": "kperm Eⱼ(u)",
    "E_j": "Eⱼ", r"k_{\mathrm{perm}}": "kperm",
    r"\omega_j=w_jo_j/\sum_\ell w_\ell o_\ell": "ωⱼ = wⱼoⱼ / Σℓ wℓoℓ",
    "w_j": "wⱼ", "o_j": "oⱼ", r"\ell": "ℓ",
    r"k_{\mathrm{loss}}": "kloss", "F": "F",
    r"k_{\mathrm{loss}}=0": "kloss = 0",
}
EQUATIONS = [
    ("01-assembly", "Soluble antibody complex and receptor-bound ternary complex at equilibrium."),
    ("02-high-dose-limit", "At large primary excess, ternary complex declines in inverse proportion to primary concentration."),
    ("05-secondary-excess", "With sufficient secondary excess, nearly all primary is loaded and the surface ternary fraction approaches receptor saturation."),
    ("03-payload-balance", "Current productive payload changes by delivery minus first-order loss."),
    ("04-fluorescence-history", "Normalized fluorescence is an optically weighted integral of permeabilization history and reporter persistence."),
]
text = (ROOT / "docs/the-hook-is-a-property-of-the-system.md").read_text()
counter = 0

def display(match):
    global counter
    name, alt = EQUATIONS[counter]
    counter += 1
    return f"![{alt}](equations/light/{name}.png)"

text = re.sub(r"\\\[[\s\S]*?\\\]", display, text)
text = re.sub(r"\\\(([\s\S]*?)\\\)", lambda m: INLINE[m.group(1)], text)
assert counter == 5 and r"\(" not in text and r"\[" not in text
text = text.replace("../figures/", f"{PUBLIC}/figures/")
text = text.replace("](equations/light/", f"]({PUBLIC}/equation-images/light/")
(OUT / "the-hook-is-a-property-of-the-system.md").write_text(text)
(OUT / "figures").mkdir(exist_ok=True)
for filename in ("cover-hook-system.png", "cover-hook-system-linkedin.png",
                 "cover-hook-system-substack.png",
                 "mechanism-map.png", "readout-separation.png",
                 "cell-scenarios.png", "cell-trafficking.png", "cell-addition-orders.png",
                 "cell-hook-assembly.png"):
    shutil.copyfile(ROOT / "figures" / filename, OUT / "figures" / filename)
for theme in ("light", "dark"):
    destination = ROOT / "viewer/equation-images" / theme
    destination.mkdir(parents=True, exist_ok=True)
    for equation in (OUT / "equations" / theme).glob("*.png"):
        shutil.copyfile(equation, destination / equation.name)
print("Built illustrated publication manuscript with public image addresses; copied figures and equation images.")
