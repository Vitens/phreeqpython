---
icon: lucide/list-checks
---

# Supported features

PhreeqPython wraps a subset of PHREEQC as Python objects. Those objects stay in the engine, so you can query and change them stepwise. Anything without an object API is listed under [Not supported yet](#not-supported-yet).

???+ info "You can run these examples"

    Click **Run** (or Ctrl+Enter), or **Run all** to execute every editor in order. The first run loads Pyodide and can take a few seconds. Editors on this page **share a session**, so later cells can reuse `pp` and `solution`.

## Object-oriented PHREEQC

Solutions, gases, and equilibrium phases are objects. You create them on a `PhreeqPython` instance, call methods, and read properties. PhreeqPython generates the PHREEQC snippets and keeps the numbered entities in memory.

```pyodide session="features" height="8-16" install="../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
from phreeqpython import PhreeqPython

pp = PhreeqPython()
solution = pp.add_solution({
    'pH': 7,
    'units': 'mmol/kgw',
    'Ca': 1,
    'C': 2,
    'Na': 2,
    'Cl': 2,
})
print(solution.pH)
```

Mixing uses ordinary Python operators (`solution * 0.5 + other * 0.5`). Copies, dumps, and custom master species / solution species are also available.

## Speciation and solution properties

After each calculation you can read speciation and bulk properties without a `SELECTED_OUTPUT` block:

- pH, pe, temperature, ionic strength
- specific conductivity, density, mass, volume
- element totals and aqueous species (moles, molalities, activities)
- saturation indices and saturation ratios for mineral and gas phases

```pyodide session="features" height="6-12" install="../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
print(solution.pH)
print(solution.sc)
print(solution.species['HCO3-'])
print(solution.si('Calcite'))
```

## Reactions and phases

Change a solution in place, or equilibrate it with one or more pure phases:

- add, remove, or change amounts (`add`, `remove`, `change`)
- set pH or temperature
- saturate, desaturate, or equalize with named phases (`Calcite`, `Gypsum`, …)
- keep a reusable `EquilibriumPhase` and `interact` with it

!!! warning "Changes are additive"

    `solution.add('NaOH', 0.5)` changes the solution **in place**. If you run this cell again, another 0.5 mmol of NaOH is added. To start over, rerun the first editor, which creates a new `solution`.

```pyodide session="features" height="6-12" install="../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
solution.add('NaOH', 0.5)
print('pH', solution.pH)
solution.desaturate('Calcite')
print('Ca mmol', solution.total('Ca'))
print('SI Calcite', solution.si('Calcite'))
```

## Gases

Gas phases are objects as well: fixed pressure or fixed volume, optional equilibration when created, then interaction with a solution.

```pyodide session="features" height="8-16" install="../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
air = pp.add_gas({'O2(g)': 0.2, 'N2(g)': 0.78, 'CO2(g)': 0.00042})
solution.interact(air)

print(air.pressure)
print(air.partial_pressures)
print('pH', solution.pH)
```

You can query moles, mole fractions, partial pressures, and dry fractions after each interaction.

## Not supported yet

These PHREEQC capabilities have no PhreeqPython objects yet:

- **Ion exchange** (`EXCHANGE`)
- **Transport and advection** (`TRANSPORT`, `ADVECTION`)
- **Surface complexation** (`SURFACE`)
- **Solid solutions** (`SOLID_SOLUTIONS`)
- **Inverse modelling** (`INVERSE_MODELING`)
- **Native PHREEQC kinetics** (`KINETICS`, `RATES`)
