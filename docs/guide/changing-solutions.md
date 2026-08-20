---
icon: lucide/pencil
---

# Changing solutions

These methods update solutions that already exist in the engine: change their composition, mix them, equilibrate them with phases, or delete them.

???+ info "You can run these examples"

    Click **Run** (or Ctrl+Enter), or **Run all** to execute every editor in order. The first run loads Pyodide and can take a few seconds. Editors on this page **share a session**.

!!! warning "Changes are additive"

    These methods change `solution` **in place**. If you run a change cell again, the reaction is applied again. To start over, rerun the first editor.

```pyodide session="changing" height="8-12" install="../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
from phreeqpython import PhreeqPython

pp = PhreeqPython()
solution = pp.add_solution_simple({'NaCl': 2})
print('Na mmol', round(solution.total('Na'), 3), 'Cl mmol', round(solution.total('Cl'), 3))
```

## Modifying solution composition

[`add`](../reference/solution.md#solution.Solution.add), [`remove`](../reference/solution.md#solution.Solution.remove), [`remove_fraction`](../reference/solution.md#solution.Solution.remove_fraction), and [`change`](../reference/solution.md#solution.Solution.change) add or take out species through a PHREEQC `REACTION`. [`change_ph`](../reference/solution.md#solution.Solution.change_ph) and [`change_temperature`](../reference/solution.md#solution.Solution.change_temperature) set pH and temperature.

### Adding components

[`add`](../reference/solution.md#solution.Solution.add) adds a single component. The default unit is mmol.

```pyodide session="changing" height="6-10" install="../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
solution.add('KCl', 1, units='mmol')
print('K mmol', round(solution.total('K'), 3), 'Cl mmol', round(solution.total('Cl'), 3))
```

### Removing components

[`remove`](../reference/solution.md#solution.Solution.remove) removes a single component.

```pyodide session="changing" height="6-10" install="../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
solution.remove('NaCl', 0.5)
print('Na mmol', round(solution.total('Na'), 3), 'Cl mmol', round(solution.total('Cl'), 3))
```

Use [`remove_fraction`](../reference/solution.md#solution.Solution.remove_fraction) to remove a fraction of an element.

```pyodide session="changing" height="6-10" install="../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
sol = pp.add_solution_simple({'NaCl': 1})
sol.remove_fraction('Na', 0.5)
sol.remove_fraction('Cl', 0.5)
print('Na mmol', round(sol.total('Na'), 3), 'Cl mmol', round(sol.total('Cl'), 3))
```

### Changing several components at once

[`change`](../reference/solution.md#solution.Solution.change) does several additions and/or removals in a single `REACTION` step. The dictionary keys are formulas or elements; positive amounts are added, negative amounts are removed.

```pyodide session="changing" height="8-12" install="../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
solution.change({'KCl': 1, 'NaCl': -0.5})
print('Na mmol', round(solution.total('Na'), 3))
print('K mmol', round(solution.total('K'), 3))
print('Cl mmol', round(solution.total('Cl'), 3))
```

### Temperature and pH

[`change_temperature`](../reference/solution.md#solution.Solution.change_temperature) sets the temperature. [`change_ph`](../reference/solution.md#solution.Solution.change_ph) titrates with HCl or NaOH (or another acid or base you pass) until the target pH.

```pyodide session="changing" height="8-14" install="../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
calcite = pp.add_solution({'Ca': 1, 'C': 2, 'pH': 8})
print('SI Calcite at 25 C', round(calcite.si('Calcite'), 2))

calcite.change_temperature(80)
print('SI Calcite at 80 C', round(calcite.si('Calcite'), 2))

calcite.change_ph(7)
print('pH', round(calcite.pH, 2))
```

## Mixing solutions

Scale and add solutions with [`*`](../reference/solution.md#solution.Solution.__mul__) and [`+`](../reference/solution.md#solution.Solution.__add__). [`copy()`](../reference/solution.md#solution.Solution.copy) makes an independent duplicate. Mixing and copying each allocate a new number in the engine.

!!! warning "Mixing conserves total mass"

    `a + b` mixes the two full solutions. Two 1 kg (about 1 L) solutions become about 2 kg (about 2 L). It is not a 1:1 blend that is then made up to 1 L. Use fractions when you want a 1 kg mixture: `a * 0.5 + b * 0.5`.

```pyodide session="changing" height="12-18" install="../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
a = pp.add_solution_simple({'NaCl': 1})
b = pp.add_solution_simple({'NaCl': 3})
half = a * 0.5 + b * 0.5
full = a + b
print('half Cl mmol', round(half.total('Cl'), 3), 'mass', round(half.mass, 3))
print('full Cl mmol', round(full.total('Cl'), 3), 'mass', round(full.mass, 3))

duplicate = full.copy()
print('copy SC', round(duplicate.sc, 1))
```

## Phase interactions

Solutions can be equilibrated with pure phases using [`saturate`](../reference/solution.md#solution.Solution.saturate), [`desaturate`](../reference/solution.md#solution.Solution.desaturate), and [`equalize`](../reference/solution.md#solution.Solution.equalize).

- [`saturate`](../reference/solution.md#solution.Solution.saturate) dissolves a phase until a target saturation index if the solution is undersaturated.
- [`desaturate`](../reference/solution.md#solution.Solution.desaturate) precipitates (or degasses) until a target saturation index.
- [`equalize`](../reference/solution.md#solution.Solution.equalize) brings one or more phases to their target SI in a single step.

```pyodide session="changing" height="12-18" install="../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
mineral = pp.add_solution({'Ca': 1, 'C': 2, 'pH': 8})
print('SI Calcite', round(mineral.si('Calcite'), 2))

mineral.saturate('Calcite', to_si=0.5)
print('after saturate', round(mineral.si('Calcite'), 2))

mineral.desaturate('Calcite')
print('after desaturate', round(mineral.si('Calcite'), 2), 'Ca mmol', round(mineral.total('Ca'), 3))

mineral.equalize(['Calcite', 'CO2(g)'], [0, -3.5])
print('after equalize SI Calcite', round(mineral.si('Calcite'), 2), 'pH', round(mineral.pH, 2))
```

To reuse a phase assemblage, create an [`EquilibriumPhase`](../reference/equilibriumphase.md#equilibriumphase.EquilibriumPhase) or [`Gas`](../reference/gas.md#gas.Gas) on the `PhreeqPython` instance and call [`interact`](../reference/solution.md#solution.Solution.interact). The [Gases](gases.md) guide covers fixed-pressure and fixed-volume gas phases.

```pyodide session="changing" height="8-14" install="../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
water = pp.add_solution({'pH': 7})
eq = pp.add_equilibrium_phase(['Calcite', 'CO2(g)'], [0, -1.5], [10, 10])
water.interact(eq)
print('pH', round(water.pH, 2), 'Ca mmol', round(water.total('Ca'), 3))
print('Calcite remaining', round(eq.components['Calcite'], 3))
```

## Forgetting solutions

PHREEQC keeps every numbered solution in the engine until you delete it. [`add_solution`](../reference/phreeqpython.md#phreeqpython.PhreeqPython.add_solution), `copy()`, and mixing each allocate a new number, so a long-running model (a loop that copies solutions, or a kinetic rate function that makes a temporary copy) can accumulate unused solutions and grow in memory.

Call [`forget()`](../reference/solution.md#solution.Solution.forget) when you are done with a solution. That sends a PHREEQC `DELETE` for its number. Use [`get_solution_list()`](../reference/phreeqpython.md#phreeqpython.PhreeqPython.get_solution_list) to see which numbers are still in the engine.

```pyodide session="changing" height="6-10" install="../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
print('before', pp.get_solution_list())
duplicate.forget()
print('after', pp.get_solution_list())
```

The Python object still exists, but the engine no longer has that number. Querying it afterwards is not meaningful (pH comes back as `-999`). Do not `forget()` a solution you still need.

See the [API reference for Solution](../reference/solution.md) for every method, and the [Examples](../examples/index.md) for more examples of how to use PhreeqPython.
