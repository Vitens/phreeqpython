---
icon: lucide/cloud
---

# Gases

A [`Gas`](../reference/gas.md#gas.Gas) is a PHREEQC `GAS_PHASE` that stays in the engine, like a [`Solution`](../reference/solution.md#solution.Solution). You create it on a [`PhreeqPython`](../reference/phreeqpython.md#phreeqpython.PhreeqPython) instance with [`add_gas`](../reference/phreeqpython.md#phreeqpython.PhreeqPython.add_gas), then query pressure, volume, and composition, or [`interact`](../reference/solution.md#solution.Solution.interact) it with a solution. To hold a single gas at a fixed partial pressure (for example `CO2(g)` at 10^-3.5 atm), use [`equalize`](../reference/solution.md#solution.Solution.equalize) / [`saturate`](../reference/solution.md#solution.Solution.saturate) instead of a `Gas` object.

PHREEQC has two kinds of gas phase. They cannot be combined:

- **Fixed pressure**: total pressure stays constant; volume can change (an open headspace, or a piston).
- **Fixed volume**: volume stays constant; pressure can change (a closed bottle).

See the [`GAS_PHASE` keyword](https://water.usgs.gov/water-resources/software/PHREEQC/documentation/phreeqc3-html/phreeqc3-17.htm) in the [PHREEQC manual](https://pubs.usgs.gov/tm/06/a43/) for the full identifier list.

???+ info "You can run these examples"

    Click **Run** (or Ctrl+Enter), or **Run all** to execute every editor in order. The first run loads Pyodide and can take a few seconds. Editors on this page **share a session**.

## Creating a gas

The `components` dictionary lists gas names from the database (`CO2(g)`, `O2(g)`, `N2(g)`, `CH4(g)`, `H2O(g)`, …). The values are **initial partial pressures in atm**. PHREEQC converts those, with `volume` and temperature, to moles (`n = PV/RT` for an ideal gas). Include gases with partial pressure `0` if they may enter the phase later.

Default: `pressure=1` atm, `volume=1` L, `fixed_pressure=True`.

## Fixed pressure

Total pressure is held at a fixed `pressure`. After reaction with a solution, the volume adjusts so that the pressure stays constant.

```pyodide session="gases" height="12-18" install="../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
from phreeqpython import PhreeqPython

pp = PhreeqPython()
air = pp.add_gas(
    {'N2(g)': 0.78, 'O2(g)': 0.21, 'CO2(g)': 0.0004},
    pressure=1.0,
    volume=1.0,
    fixed_pressure=True,
)
print('P', round(air.pressure, 4), 'atm, V', round(air.volume, 4), 'L')
print('partial pressures', {k: round(v, 4) for k, v in air.partial_pressures.items()})
```

## Fixed volume

Volume is held at a fixed `volume`. After reaction, the pressure (and partial pressures) can change.

You can only pass `equilibrate_with` for a fixed-volume gas. PHREEQC then calculates the initial gas composition from that solution; the numbers in `components` are ignored except as a list of which gases may be present.

```pyodide session="gases" height="14-22" install="../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
headspace = pp.add_gas(
    {'CH4(g)': 0.5, 'N2(g)': 0.5},
    pressure=1.0,
    volume=1.0,
    fixed_pressure=False,
    fixed_volume=True,
)
print('P', round(headspace.pressure, 4), 'atm, V', round(headspace.volume, 4), 'L')
print('moles', {k: round(v, 4) for k, v in headspace.components.items()})

sol = pp.add_solution({}).equalize(['Calcite', 'CO2(g)'], [0, -1.5])
from_sol = pp.add_gas(
    {'CO2(g)': 0, 'N2(g)': 0, 'H2O(g)': 0},
    volume=1.0,
    fixed_pressure=False,
    fixed_volume=True,
    equilibrate_with=sol,
)
print('equilibrated P_CO2', round(from_sol.partial_pressures.get('CO2(g)', 0), 4))
```

`add_gas` raises `ValueError` if both `fixed_pressure` and `fixed_volume` are true, or if `equilibrate_with` is set on a fixed-pressure gas.

## Interact

[`solution.interact(gas)`](../reference/solution.md#solution.Solution.interact) brings the solution and gas to equilibrium and saves **both** back to the engine. The Python objects are updated in place.

The example is 1 L of air over 1 kg of pure water at 25 °C. Dissolved oxygen after `interact` is the air-saturated value at that temperature.

```pyodide session="gases" height="16-24" install="../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
air = pp.add_gas(
    {'N2(g)': 0.78, 'O2(g)': 0.21, 'CO2(g)': 0.0004},
    pressure=1.0,
    volume=1.0,
    fixed_pressure=True,
)
water = pp.add_solution({'temp': 25})
print('O2 before interact', round(water.total('O2', 'mg'), 3), 'mg/kgw')
water.interact(air)
print('O2 after interact ', round(water.total('O2', 'mg'), 2), 'mg/kgw')
print('O2 after interact ', round(water.total('O2', 'mmol'), 3), 'mmol')
print('P', round(air.pressure, 4), 'atm, V', round(air.volume, 4), 'L')
```

Use [`copy()`](../reference/gas.md#gas.Gas.copy) when you need an independent gas for another step, and [`forget()`](../reference/gas.md#gas.Gas.forget) when you are done (same idea as for solutions).

## Composition and pressures

After each calculation you can read:

- [`pressure`](../reference/gas.md#gas.Gas.pressure): total pressure, atm
- [`volume`](../reference/gas.md#gas.Gas.volume): liters
- [`total_moles`](../reference/gas.md#gas.Gas.total_moles)
- [`components`](../reference/gas.md#gas.Gas.components): moles of each gas
- [`fractions`](../reference/gas.md#gas.Gas.fractions): mole fractions (including water vapour)
- [`partial_pressures`](../reference/gas.md#gas.Gas.partial_pressures): atm
- [`dry_fractions`](../reference/gas.md#gas.Gas.dry_fractions): mole fractions excluding `H2O(g)`

```pyodide session="gases" height="10-16" install="../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
print('total moles', round(air.total_moles, 4))
print('components', {k: round(v, 5) for k, v in air.components.items()})
print('fractions', {k: round(v, 4) for k, v in air.fractions.items()})
print('partial P', {k: round(v, 4) for k, v in air.partial_pressures.items()})
print('dry fractions', {k: round(v, 4) for k, v in air.dry_fractions.items()})
```

Futher examples: [gas solubilities](../examples/gas-solubilities.md) and [fixed-pressure vs fixed-volume after organic-matter reaction](../examples/gas-phase.md). See the [API reference for Gas](../reference/gas.md) for every property.
