# Organoid Hook Model v0.1.0

An initial, uncalibrated research-software release for Data-Rich, Insight-Poor.

The no-install browser explorer presents 5,304 synthetic simulations from a finite-bath, no-wash mechanistic model. It includes all four addition orders, receptor-copy and trafficking scenarios, receptor degradation and downstream recovery kinetics, primary/secondary concentration sweeps, and alternative observation models.

The mathematical specification provides a derived equilibrium hook equation and peak location, the complete dynamical equations, all state variables and configurable parameters with units, dosing events, boundary conditions, conservation balances, and structural limitations. The companion article, “The Hook Is a Property of the System,” connects the mathematics to assay interpretation using screened public literature.

This release includes Python source, an editable Colab notebook, reproducible figure and atlas scripts, CSV/JSON/PNG browser exports, 34 passing local automated tests, and 12 independently recomputed reference conditions. GitHub Actions checks two Python versions.

All parameters are illustrative assumptions, not fitted experimental estimates. Code verification is not biological validation. The transport stress case is explicitly not spatially converged. The public-source screen is bounded to retrieved publications and disclosures; it is not legal clearance.

- [Browser explorer](https://datarichinsightpoor.github.io/organoid-hook-model/)
- [Complete mathematics](https://datarichinsightpoor.github.io/organoid-hook-model/equations.html)
- [Companion article](https://datarichinsightpoor.github.io/organoid-hook-model/article.html)
- [Editable notebook](https://colab.research.google.com/github/dataRichinsightPoor/organoid-hook-model/blob/main/examples/quickstart.ipynb)
