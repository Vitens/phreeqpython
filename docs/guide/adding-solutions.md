---
icon: lucide/plus
---

# Adding solutions

A [`Solution`](../reference/solution.md#solution.Solution) is an aqueous composition that stays in the PHREEQC engine. You create it on a [`PhreeqPython`](../reference/phreeqpython.md#phreeqpython.PhreeqPython) instance.

There are two ways to define the composition: a complete PHREEQC `SOLUTION` block, or a known chemical recipe. Both assign a solution number automatically.

???+ info "You can run these examples"

    Click **Run** (or Ctrl+Enter), or **Run all** to execute every editor in order. The first run loads Pyodide and can take a few seconds. Editors on this page **share a session**.

## Adding a complete solution

Use [`add_solution`](../reference/phreeqpython.md#phreeqpython.PhreeqPython.add_solution) when you have an analytical composition, or you need PHREEQC `SOLUTION` options: pH, pe, units, density, charge balance, redox, or equilibrium with a phase.

The dictionary is written as identifier lines in a [`SOLUTION`](https://water.usgs.gov/water-resources/software/PHREEQC/documentation/phreeqc3-html/phreeqc3-48.htm) data block. Keys and values are the same identifiers and data items as in the [PHREEQC manual](https://pubs.usgs.gov/tm/06/a43/): `temp`, `pH`, `pe`, `units`, `density`, `redox`, element names, `Alkalinity`, and so on. Values may be numbers or strings when PHREEQC needs extra tokens (`as HCO3`, `charge`, a phase name).

PhreeqPython assigns the solution number; do not put a number in the dictionary.

```pyodide session="adding" height="16-26" install="../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
from phreeqpython import PhreeqPython

pp = PhreeqPython()

solution = pp.add_solution({
    'units': 'ppm',
    'pH': 8.22,
    'temp': 25.0,
    'Ca': 412.3,
    'Mg': 1291.8,
    'Na': 10768.0,
    'K': 399.1,
    'Cl': 19353.0,
    'Alkalinity': '141.682 as HCO3',
    'S(6)': 2712.0,
})
print(solution)
print('pH', round(solution.pH, 2), 'SC', round(solution.sc, 1))
```

That call sends:

```
SOLUTION 0
  units ppm
  pH 8.22
  temp 25.0
  Ca 412.3
  Mg 1291.8
  Na 10768.0
  K 399.1
  Cl 19353.0
  Alkalinity 141.682 as HCO3
  S(6) 2712.0
SAVE SOLUTION 0
END
```

Typical `SOLUTION` lines you can pass through the dictionary:

- `units`: `mmol/kgw`, `ppm`, `mg/L`, …
- `pH` / `pe`: a number, `charge`, or equilibrium with a phase (`'pH': '8 Gibbsite'`)
- element totals: `'Ca': 1`, `'S(6)': 2712.0`, `'Al': '0.2 mg/kgw'`
- charge balance: `'Cl': 'charge'`
- phase equilibrium on an element: `'Al': '1e3 Gibbsite'`

See the [SOLUTION keyword](https://water.usgs.gov/water-resources/software/PHREEQC/documentation/phreeqc3-html/phreeqc3-48.htm) in the PHREEQC Version 3 manual for the full identifier list and syntax.

## Adding a simple solution

Use [`add_solution_simple`](../reference/phreeqpython.md#phreeqpython.PhreeqPython.add_solution_simple) when the solution has a known chemical composition, for example a solution of 1 mmol NaOH. The dictionary keys are chemical formulas; the values are amounts. Optional arguments: `temperature` (default 25 °C) and `units` (default `mmol`; also `mol`, `mg`, or `ug`).

PhreeqPython creates an empty `SOLUTION` at that temperature, then adds the formulas in a PHREEQC [`REACTION`](https://water.usgs.gov/water-resources/software/PHREEQC/documentation/phreeqc3-html/phreeqc3-40.htm) step. Formula names follow PHREEQC (case-sensitive), as described in the [PHREEQC manual](https://pubs.usgs.gov/tm/06/a43/).

```pyodide session="adding" height="8-14" install="../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
naoh = pp.add_solution_simple({'NaOH': 1})
print(naoh)
print('pH', round(naoh.pH, 2))
print('Na mmol', round(naoh.total('Na'), 3))
```

That call sends:

```
SOLUTION 1
-temp 25
REACTION 1
NaOH 1.0
1 mmol
SAVE SOLUTION 1
END
```

Amounts are converted to mmol before the `REACTION`. Pass `units='mg'` (or another unit) when the dictionary is not already in mmol.