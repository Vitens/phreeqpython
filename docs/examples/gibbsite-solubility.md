---
icon: lucide/beaker
---

# Gibbsite solubility

Gibbsite solubility as a function of pH, after [Appelo's gibbsite example](http://hydrochemistry.eu/exmpls/gibbsite.html).

???+ info "You can run these examples"

    Click **Run** (or Ctrl+Enter), or **Run all** to execute every editor in order. Editors on this page **share a session**.

```pyodide session="gibbsite" height="12-18" install="matplotlib,numpy,../../wheels/phreeqpython-pyodide.whl"
from phreeqpython import PhreeqPython
import numpy as np
import matplotlib.pyplot as plt

pp = PhreeqPython('phreeqc.dat')
x, y = [], []

for ph in np.linspace(3, 12, 17):
    sol = pp.add_solution({'pH': ph, 'Al': '1e3 Gibbsite'})
    x.append(ph)
    y.append(sol.total_element('Al', units='mol'))

print('pH range', x[0], '–', x[-1])
```

```pyodide session="gibbsite" height="10-16" install="matplotlib,numpy,../../wheels/phreeqpython-pyodide.whl"
fig = plt.figure(figsize=[10, 5])
plt.plot(x, y, 'rs-')
plt.title('Gibbsite equilibrium')
plt.xlim(0, 14)
plt.yscale('log')
plt.xlabel('pH')
plt.ylabel('Al (mol/kgw)')
plt.grid()
show_plot(fig)
```
