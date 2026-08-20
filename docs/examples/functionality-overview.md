---
icon: lucide/beaker
---

# Functionality overview

A tour of the main `Solution` methods: create, query, change, mix, copy, and forget.

???+ info "You can run these examples"

    Click **Run** (or Ctrl+Enter), or **Run all** to execute every editor in order. The first run loads Pyodide and can take a few seconds. Editors on this page **share a session**.

## Adding solutions

```pyodide session="overview" height="14-24" install="../../wheels/phreeqpython-1.6.2+pyodide-py3-none-any.whl"
from phreeqpython import PhreeqPython

pp = PhreeqPython()

# Simple, through a reaction block
solution = pp.add_solution_simple({'CaCl2': 1.0, 'NaHCO3': 2.0}, temperature=15)

# More control: standard PHREEQC SOLUTION keywords (PHREEQC example 3 — mixing)
solution2 = pp.add_solution({
    'units': 'ppm',
    'pH': 8.22,
    'pe': 8.451,
    'density': 1.023,
    'temp': 25.0,
    'Ca': 412.3,
    'Mg': 1291.8,
    'Na': 10768.0,
    'K': 399.1,
    'Si': 4.28,
    'Cl': 19353.0,
    'Alkalinity': '141.682 as HCO3',
    'S(6)': 2712.0,
})
print('pH', round(solution.pH, 2), 'SC', round(solution.sc, 2))
```

## Basic properties

```pyodide session="overview" height="8-14" install="../../wheels/phreeqpython-1.6.2+pyodide-py3-none-any.whl"
print('Solution pH: {:.3}'.format(solution.pH))
print('Solution sc: {:3.2f}'.format(solution.sc))
print('Solution pe: {:.3}'.format(solution.pe))
print('Temperature: {:.3}'.format(solution.temperature))
print('Mass:        {:.3}'.format(solution.mass))
```

## Speciation, elements, phases

```pyodide session="overview" height="8-16" install="../../wheels/phreeqpython-1.6.2+pyodide-py3-none-any.whl"
print('Species (mmol):')
for name, amount in list(solution.species.items())[:8]:
    print(f'  {name:12} {amount:.4g}')
print('...')
print('Cl mmol', solution.total_element('Cl', units='mmol'))
print('HCO3 mg', solution.total('HCO3', units='mg'))
print('SI Calcite', round(solution.si('Calcite'), 2))
```

## Modifying solutions

!!! warning "Changes are additive"

    These calls change `solution` **in place**. Run this cell once. To start over, rerun **Adding solutions**.

```pyodide session="overview" height="10-16" install="../../wheels/phreeqpython-1.6.2+pyodide-py3-none-any.whl"
solution.add('NaOH', 1, 'mmol')
solution.remove('NaCl', 1, 'mmol')
solution.remove_fraction('CO3', 0.5)

solution.saturate('Calcite', 1.0)
solution.desaturate('Calcite', 0.0)

solution.change_ph(5, 'HCl')
print('pH', round(solution.pH, 2))

solution.change_temperature(10)
print('T', solution.temperature)
```

## Mixing

```pyodide session="overview" height="12-18" install="../../wheels/phreeqpython-1.6.2+pyodide-py3-none-any.whl"
solution1 = pp.add_solution_simple({'NaCl': 1})
solution2 = pp.add_solution_simple({'NaCl': 3})
solution3 = solution1 * 0.5 + solution2 * 0.5
solution4 = solution1 + solution2

print('Solution 3  Cl mmol', round(solution3.total('Cl'), 3), 'mass', solution3.mass)
print('Solution 4  Cl mmol', round(solution4.total('Cl'), 3), 'mass', solution4.mass)
```

## Copy and forget

```pyodide session="overview" height="6-10" install="../../wheels/phreeqpython-1.6.2+pyodide-py3-none-any.whl"
solution5 = solution4.copy()
print(solution5.sc)
solution5.forget()
```
