---
icon: lucide/beaker
---

# Gas-phase calculations

Fixed-pressure vs fixed-volume gas after reaction of organic matter, after [PHREEQC example 7](https://wwwbrr.cr.usgs.gov/projects/GWC_coupled/phreeqc/phreeqc3-html/phreeqc3-62.htm#50528271_44022).

???+ info "You can run these examples"

    Click **Run** (or Ctrl+Enter), or **Run all** to execute every editor in order. Editors on this page **share a session**. The reaction loop can take a few seconds.

```pyodide session="gasphase" height="8-12" install="matplotlib,numpy,pandas,../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
from phreeqpython import PhreeqPython
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

pp = PhreeqPython(database='phreeqc.dat')
```

Add NH₄ / NH₃ species used in the original PHREEQC input:

```pyodide session="gasphase" height="16-24" install="matplotlib,numpy,pandas,../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
pp.ip.run_string("""
SOLUTION_MASTER_SPECIES
N(-3)    NH4+           0.0     N
SOLUTION_SPECIES
NH4+ = NH3 + H+
        log_k           -9.252
        delta_h 12.48   kcal
        -analytic    0.6322    -0.001225     -2835.76

NO3- + 10 H+ + 8 e- = NH4+ + 3 H2O
        log_k           119.077
        delta_h -187.055        kcal
        -gamma    2.5000    0.0000
PHASES
NH3(g)
        NH3 = NH3
        log_k           1.770
        delta_h -8.170  kcal
""")
print('NH3 species loaded')
```

```pyodide session="gasphase" height="22-32" install="matplotlib,numpy,pandas,../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
solution1 = pp.add_solution({})
solution1.equalize(['Calcite', 'CO2(g)'], [0, -1.5])

fixed_pressure = pp.add_gas(
    {'CO2(g)': 0, 'CH4(g)': 0, 'N2(g)': 0, 'H2O(g)': 0},
    pressure=1.1,
    fixed_pressure=True,
)
fixed_volume = pp.add_gas(
    {'CO2(g)': 0, 'CH4(g)': 0, 'N2(g)': 0, 'H2O(g)': 0},
    volume=23.19,
    fixed_pressure=False,
    fixed_volume=True,
    equilibrate_with=solution1,
)

mmol = [1, 2, 3, 4, 8, 16, 32, 64, 125, 250, 500, 1000]
fp_vol, fp_pres, fp_frac = [], [], []
fv_vol, fv_pres, fv_frac = [], [], []

for m in mmol:
    sol = solution1.copy()
    fp = fixed_pressure.copy()
    sol.add('CH2O(NH3)0.07', m, 'mmol')
    sol.interact(fp)
    fp_vol.append(fp.volume)
    fp_pres.append(fp.pressure)
    fp_frac.append(fp.partial_pressures)
    sol.forget()
    fp.forget()

    sol = solution1.copy()
    fv = fixed_volume.copy()
    sol.add('CH2O(NH3)0.07', m, 'mmol')
    sol.interact(fv)
    fv_vol.append(fv.volume)
    fv_pres.append(fv.pressure)
    fv_frac.append(fv.partial_pressures)
    sol.forget()
    fv.forget()

print('steps', len(mmol))
```

## Total gas pressure and volume

```pyodide session="gasphase" height="16-24" install="matplotlib,numpy,pandas,../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
fig = plt.figure(figsize=[8, 5])
ax1 = plt.gca()
ax2 = ax1.twinx()
ax1.plot(mmol, np.log10(fp_pres), 'x-', color='tab:purple', label='Fixed P — pressure')
ax1.plot(mmol, np.log10(fv_pres), 's-', color='tab:purple', label='Fixed V — pressure')
ax1.plot(np.nan, np.nan, 'x-', color='tab:blue', label='Fixed P — volume')
ax1.plot(np.nan, np.nan, 's-', color='tab:blue', label='Fixed V — volume')
ax2.plot(mmol, fp_vol, 'x-')
ax2.plot(mmol, fv_vol, 's-', color='tab:blue')
ax2.set_xscale('log')
ax2.set_yscale('log')
ax1.set_xlim([1e0, 1e3])
ax2.set_xlim([1e0, 1e3])
ax1.set_ylim([-5, 1])
ax2.set_ylim([1e-3, 1e5])
ax1.legend(loc=4)
ax1.grid()
ax1.set_xlabel('Organic matter reacted, in millimoles')
ax1.set_ylabel('Log(Pressure, in atmospheres)')
ax2.set_ylabel('Volume, in liters')
show_plot(fig)
```

## Gas composition

```pyodide session="gasphase" height="14-22" install="matplotlib,numpy,pandas,../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
fig = plt.figure(figsize=[12, 5])
fig.add_subplot(1, 2, 1)
pd.DataFrame(fp_frac, index=mmol).apply(np.log10)[2:].plot(style='-x', ax=plt.gca())
plt.title('Fixed-pressure gas composition')
plt.xscale('log')
plt.ylim([-5, 1])
plt.grid()
plt.xlim(1e0, 1e3)
plt.xlabel('Organic matter reacted, in millimoles')
plt.ylabel('Log(Partial pressure, in atmospheres)')

fig.add_subplot(1, 2, 2)
pd.DataFrame(fv_frac, index=mmol).apply(np.log10).plot(style='-o', ax=plt.gca())
plt.title('Fixed-volume gas composition')
plt.xscale('log')
plt.xlabel('Organic matter reacted, in millimoles')
plt.ylabel('Log(Partial pressure, in atmospheres)')
plt.grid()
plt.ylim([-5, 1])
show_plot(fig)
```
