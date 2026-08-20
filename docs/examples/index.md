---
icon: lucide/beaker
---

# Examples

Worked examples from the PhreeqPython notebooks, as live editors in the browser. Click **Run** (or Ctrl+Enter) on each cell. Editors on a page **share a session**, so run them in order.

The original Jupyter notebooks remain in [`examples/`](https://github.com/Vitens/phreeqpython/tree/master/examples) if you prefer to run them locally.

## General

- [Functionality overview](functionality-overview.md) — create solutions, query properties, mix, copy
- [Carbonic acid equilibrium](carbonic-acid.md) — CO₂ / HCO₃⁻ / CO₃²⁻ vs pH

## Equilibrium

- [Ca–F and fluorite](ca-f-fluorite.md) — fluoride vs calcium during feldspar dissolution
- [Calcite dissolution](calcite-dissolution.md) — calcite vs CO₂ pressure, including mixing
- [Gibbsite solubility](gibbsite-solubility.md) — dissolved Al vs pH
- [Aluminium drinking-water limit](aluminium-limit.md) — pH where 0.2 mg/kgw Al is in equilibrium with gibbsite
- [Gypsum on evaporation](gypsum-evaporation.md) — gypsum precipitation as water is removed

## Kinetics

- [Quartz dissolution](quartz-kinetics.md) — `solution.kinetics()` and SciPy `odeint`
- [Monod kinetics](monod-kinetics.md) — methanogenic phenol biodegradation

## Gas

- [Solubilities](gas-solubilities.md) — O₂, N₂, CH₄, and CO₂ in 4 M NaCl
- [Gas-phase calculations](gas-phase.md) — fixed-pressure vs fixed-volume gas after organic-matter reaction
