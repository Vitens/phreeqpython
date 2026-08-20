---
icon: lucide/beaker
---

# Gypsum precipitation upon evaporation

Gypsum precipitation as water is evaporated, after [Appelo's evaporation example](http://hydrochemistry.eu/exmpls/evap.html). Bromide is a conservative tracer for concentration.

???+ info "You can run these examples"

    Click **Run** (or Ctrl+Enter).

!!! warning "Changes are additive"

    Each step **removes water** from the same solutions. Run the cell once. To start over, rerun it after reloading the page, or wrap the setup and loop together and run once.

```pyodide session="gypsum" height="22-32" install="matplotlib,numpy,../../wheels/phreeqpython-1.6.2+pyodide-py3-none-any.whl"
from phreeqpython import PhreeqPython
import matplotlib.pyplot as plt

pp = PhreeqPython('phreeqc.dat')

sol1 = pp.add_solution({'Ca': 3.5, 'S(6)': 3.5, 'Br': 1e-6})
x, y, y2 = [], [], []
for i in range(20):
    sol1.remove('H2O', 55.3 / 20, units='mol')
    sol1.desaturate('Gypsum')
    x.append(sol1.total_element('Br', units='mol') / sol1.mass / 1e-9)
    y.append(sol1.total_element('S', units='mol') / sol1.mass)
    y2.append(sol1.total_element('Ca', units='mol') / sol1.mass)

sol2 = pp.add_solution({'Ca': 3.5, 'S(6)': 7.0, 'Br': 1e-6})
y3, y4 = [], []
for i in range(20):
    sol2.remove('H2O', 55.3 / 20, units='mol')
    sol2.desaturate('Gypsum')
    y3.append(sol2.total_element('S', units='mol') / sol2.mass)
    y4.append(sol2.total_element('Ca', units='mol') / sol2.mass)

fig = plt.figure(figsize=[10, 5])
plt.plot(x, y, 'rs-', label='SO4(=Ca)')
plt.plot(x, y2, 'gd-', label='Ca')
plt.plot(x, y3, 'b^-', label='SO4(=2*Ca)')
plt.plot(x, y4, 'yd-', label='Ca (2× SO4)')
plt.yscale('log')
plt.xscale('log')
plt.xlabel('Concentration factor (Br)')
plt.ylabel('mol / kgw')
plt.legend()
plt.grid()
show_plot(fig)
```
