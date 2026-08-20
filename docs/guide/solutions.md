---
icon: lucide/droplets
---

# Solutions

A `Solution` is an aqueous composition that stays in the PHREEQC engine. You create it on a `PhreeqPython` instance, then query or change it in place.

???+ info "You can run these examples"

    Click **Run** (or Ctrl+Enter), or **Run all** to execute every editor in order. The first run loads Pyodide and can take a few seconds. Editors on this page **share a session**.

## Creating a solution

`add_solution_simple` takes salts as a reaction. `add_solution` uses PHREEQC `SOLUTION` keywords (pH, units, element totals, charge balance, …).

```pyodide session="solutions" height="14-22" install="../../wheels/phreeqpython-1.6.2+pyodide-py3-none-any.whl"
from phreeqpython import PhreeqPython

pp = PhreeqPython()

solution = pp.add_solution_simple({'CaCl2': 1.0, 'NaHCO3': 2.0}, temperature=15)

seawater = pp.add_solution({
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
print('pH', round(solution.pH, 2), 'SC', round(solution.sc, 2))
```

Pass `database='phreeqc.dat'` (or another bundled `.dat`) to `PhreeqPython(...)` when you need a different thermodynamic database.

## Querying properties

After each calculation you can read bulk properties, totals, speciation, and saturation indices — no `SELECTED_OUTPUT` block.

```pyodide session="solutions" height="10-16" install="../../wheels/phreeqpython-1.6.2+pyodide-py3-none-any.whl"
print('pH', round(solution.pH, 2))
print('SC', round(solution.sc, 2), 'uS/cm')
print('T', solution.temperature, 'C')
print('Cl mmol', solution.total_element('Cl'))
print('HCO3 mg', round(solution.total('HCO3', units='mg'), 2))
print('SI Calcite', round(solution.si('Calcite'), 2))
print('HCO3- mmol', round(solution.species['HCO3-'], 4))
```

Useful accessors:

- `pH`, `pe`, `sc`, `temperature`, `mass`, `volume`, `density`, `I`
- `total(species)` / `total_element(element)` — amounts, default mmol
- `species`, `elements`, `phases` — dictionaries
- `si(phase)` / `sr(phase)` — saturation index and ratio

## Changing a solution

`add`, `remove`, `change`, `change_ph`, `change_temperature`, `saturate`, and `desaturate` update the same numbered solution in the engine.

!!! warning "Changes are additive"

    These methods change `solution` **in place**. If you run this cell again, another 1 mmol of NaOH is added. To start over, rerun **Creating a solution**.

```pyodide session="solutions" height="10-16" install="../../wheels/phreeqpython-1.6.2+pyodide-py3-none-any.whl"
solution.add('NaOH', 1, 'mmol')
print('pH after NaOH', round(solution.pH, 2))

solution.desaturate('Calcite')
print('Ca mmol', round(solution.total('Ca'), 3))
print('SI Calcite', round(solution.si('Calcite'), 2))

solution.change_temperature(10)
print('T', solution.temperature)
```

## Mixing and copies

Scale and add solutions with `*` and `+`. `copy()` makes an independent duplicate; `forget()` removes a solution from the engine.

```pyodide session="solutions" height="10-16" install="../../wheels/phreeqpython-1.6.2+pyodide-py3-none-any.whl"
a = pp.add_solution_simple({'NaCl': 1})
b = pp.add_solution_simple({'NaCl': 3})
mix = a * 0.5 + b * 0.5
print('mix Cl mmol', round(mix.total('Cl'), 3), 'mass', mix.mass)

duplicate = mix.copy()
print('copy SC', round(duplicate.sc, 1))
duplicate.forget()
```

See the [API reference for Solution](../reference/solution.md) for every method, and the [Examples](../examples/index.md) for full calculations.
