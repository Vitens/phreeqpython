---
icon: lucide/search
---

# Querying solutions

After each calculation you can read bulk properties, totals, speciation, and saturation indices on a [`Solution`](../reference/solution.md#solution.Solution), with no `SELECTED_OUTPUT` block.

???+ info "You can run these examples"

    Click **Run** (or Ctrl+Enter), or **Run all** to execute every editor in order. The first run loads Pyodide and can take a few seconds. Editors on this page **share a session**.

Create a solution first (see [Adding solutions](adding-solutions.md)), then read properties from the object:

```pyodide session="querying" height="16-26" install="../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
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

print('pH', round(solution.pH, 2))
print('SC', round(solution.sc, 2), 'uS/cm')
print('T', solution.temperature, 'C')
print('Cl mmol', solution.total_element('Cl'))
print('HCO3 mg', round(solution.total('HCO3', units='mg'), 2))
print('SI Calcite', round(solution.si('Calcite'), 2))
print('HCO3- mmol', round(solution.species['HCO3-'], 4))
```

Useful accessors ([Solution](../reference/solution.md#solution.Solution)):

- [`pH`](../reference/solution.md#solution.Solution.pH), [`pe`](../reference/solution.md#solution.Solution.pe), [`sc`](../reference/solution.md#solution.Solution.sc), [`temperature`](../reference/solution.md#solution.Solution.temperature), [`mass`](../reference/solution.md#solution.Solution.mass), [`volume`](../reference/solution.md#solution.Solution.volume), [`density`](../reference/solution.md#solution.Solution.density), [`I`](../reference/solution.md#solution.Solution.I)
- [`total(species)`](../reference/solution.md#solution.Solution.total) / [`total_element(element)`](../reference/solution.md#solution.Solution.total_element): amounts, default mmol
- [`species`](../reference/solution.md#solution.Solution.species), [`elements`](../reference/solution.md#solution.Solution.elements), [`phases`](../reference/solution.md#solution.Solution.phases): dictionaries
- [`si(phase)`](../reference/solution.md#solution.Solution.si) / [`sr(phase)`](../reference/solution.md#solution.Solution.sr): saturation index and ratio

See the [API reference for Solution](../reference/solution.md) for every property.
