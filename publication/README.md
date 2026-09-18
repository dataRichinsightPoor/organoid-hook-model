# The Hook Is a Property of the System: Publication Kit

Data-Rich, Insight-Poor · Ermelinda Damko

This package prepares the same essay for publication on LinkedIn and Substack. It contains no platform-specific promotional copy inside the manuscript and does not publish to either service.

## Manuscript and images

Use `the-hook-is-a-property-of-the-system.md` as the editorial copy. It contains the complete essay, natural inline source links, and eleven peer-reviewed references. Inline notation uses ordinary characters; the four displayed equations have image positions in the text.

Insert the corresponding files from `equations/light/` at those positions. The white-background images are intended for a light article body; equivalent files in `equations/dark/` are supplied for a dark composition. Each image is captured at three-times browser pixel density from the public article's actual mathematical typesetting. Image descriptions are included in the manuscript.

The cover and the two numbered scientific figures are in `figures/`. Keep the figure captions and the synthetic, uncalibrated labels: they identify what the evidence is. The wide cover is 1920 × 1080; the alternate cover is 1200 × 675.

In the plain-character manuscript, kdeg, kP, kperm, and kloss correspond to the subscripted rate constants in the equation images. Ceq and Teq denote the equilibrium complexes, Wc denotes the per-initial-cell endosomal inventory, and KA and KS denote the two dissociation constants. No parameter or equation has changed.

## Suggested framing

Title: The Hook Is a Property of the System

Subtitle: Why restoring a cytotoxicity curve can leave a delivery deficit unresolved

Series: Data-Rich, Insight-Poor

The essay is self-contained. Link readers to the [public atlas](https://datarichinsightpoor.github.io/organoid-hook-model/) for interactive comparisons, the [worked simulation](https://datarichinsightpoor.github.io/organoid-hook-model/#follow-one-simulation) for the numerical trace, and the [repository](https://github.com/dataRichinsightPoor/organoid-hook-model) for equations, parameters, and tests. The essay already includes these links where they support the argument.

Before posting, inspect image sizing, source links, and symbol rendering in each editor's preview. No employer-linked experimental data or proprietary reagent parameters are introduced by this package; the bounded source-screening record remains in `docs/provenance.md` and is not legal clearance.

## Reproduction

Run `python tools/build_reading_pages.py` and `python tools/build_publication.py` from the repository root. With Node.js, Playwright, and its Chromium browser installed, run `node tools/export_equation_images.mjs` to recapture the equations from the public article. The module also accepts a local article URL through its exported `exportEquationImages` function.
