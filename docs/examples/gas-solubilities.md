---
icon: lucide/beaker
---

# Gas solubilities

O₂, N₂, CH₄, and CO₂ (in 4 M NaCl, Pitzer) as a function of pressure. Markers are literature / tabulated values shipped with the example.

The browser version uses fewer pressure steps than the original notebook so it finishes in a reasonable time.

???+ info "You can run these examples"

    Click **Run** (or Ctrl+Enter), or **Run all** to execute every editor in order. Editors on this page **share a session**. Each gas is a separate cell; CO₂ is the slowest.

```pyodide session="solubility" height="8-12" install="matplotlib,numpy,pandas,../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
from phreeqpython import PhreeqPython
import numpy as np
import matplotlib.pyplot as plt

pp = PhreeqPython(database='phreeqc.dat')
print('database', 'phreeqc.dat')
```

## Oxygen

```pyodide session="solubility" height="14-22" install="matplotlib,numpy,pandas,../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
pressure_range = np.linspace(0.01, 100, 25)
o2 = []
for p in pressure_range:
    sol = pp.add_solution({'temp': 27})
    gas = pp.add_gas({'O2(g)': p}, pressure=p, fixed_pressure=True)
    sol.interact(gas)
    o2.append(sol.total('O2', 'mol'))
    sol.forget()
    gas.forget()

fig = plt.figure(figsize=[8, 5])
plt.plot(pressure_range, o2, label='PhreeqPython')
load_tsv('O2_27.dat').plot(style='x', ax=plt.gca())
plt.title('Oxygen')
plt.xlabel('Pressure / atm')
plt.ylabel('O2 / (mol/kgw)')
plt.legend()
show_plot(fig)
```

## Nitrogen

```pyodide session="solubility" height="14-22" install="matplotlib,numpy,pandas,../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
pressure_range = np.linspace(0.01, 1000, 25)
n2 = []
for p in pressure_range:
    sol = pp.add_solution({'temp': 25})
    gas = pp.add_gas({'N2(g)': p}, pressure=p, fixed_pressure=True)
    sol.interact(gas)
    n2.append(sol.total_element('N', 'mol') / 2)
    sol.forget()
    gas.forget()

fig = plt.figure(figsize=[8, 5])
plt.plot(pressure_range, n2, label='PhreeqPython')
load_tsv('n2_25C.dat').plot(style='x', ax=plt.gca())
plt.title('Nitrogen')
plt.xlabel('Pressure / atm')
plt.ylabel('N2 / (mol/kgw)')
plt.legend()
show_plot(fig)
```

## Methane

```pyodide session="solubility" height="16-24" install="matplotlib,numpy,pandas,../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
fig = plt.figure(figsize=[8, 5])
colors = ['C0', 'C1', 'C2']
for temp in [25, 50, 100]:
    pressure_range = np.linspace(0.01, 1000, 20)
    ch4 = []
    for p in pressure_range:
        sol = pp.add_solution({'temp': temp})
        gas = pp.add_gas({'CH4(g)': p}, pressure=p, fixed_pressure=True)
        sol.interact(gas)
        ch4.append(sol.total('CH4', 'mol'))
        sol.forget()
        gas.forget()
    color = colors.pop(0)
    plt.plot(pressure_range, ch4, color=color, label=f'{temp} °C')
    plt.plot(load_tsv(f'ch4_{temp}c.dat'), 'x', color=color)

plt.title('Methane')
plt.xlabel('Pressure / atm')
plt.ylabel('CH4 / (mol/kgw)')
plt.legend()
show_plot(fig)
```

## CO₂ in 4 M NaCl

Uses the Pitzer database.

```pyodide session="solubility" height="16-24" install="matplotlib,numpy,pandas,../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
pitzer = PhreeqPython(database='pitzer.dat')
fig = plt.figure(figsize=[8, 5])
colors = ['C0', 'C1', 'C2']
data = load_tsv('co2_4m_NaCl.dat')
index = 0
for temp in [80, 120, 160]:
    pressure_range = np.linspace(0.01, 100, 20)
    co2 = []
    for p in pressure_range:
        sol = pitzer.add_solution({'temp': temp})
        sol.add('NaCl', 4, 'mol')
        gas = pitzer.add_gas({'CO2(g)': p}, pressure=p, fixed_pressure=True)
        sol.interact(gas)
        co2.append(sol.total_element('C', units='mol'))
        sol.forget()
        gas.forget()
    color = colors.pop(0)
    plt.plot(pressure_range * 1.013, co2, color=color, label=f'{temp} °C')
    plt.plot(data.iloc[:, index], 'x', color=color)
    index += 1

plt.title('CO2 in 4 M NaCl')
plt.xlabel('Pressure / bar')
plt.ylabel('CO2 / (mol/kgw)')
plt.legend()
show_plot(fig)
```
