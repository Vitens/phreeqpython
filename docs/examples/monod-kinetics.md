---
icon: lucide/beaker
---

# Monod kinetics

Methanogenic biodegradation of phenol, after [Appelo's phenol example](http://hydrochemistry.eu/exmpls/phenol.html). A custom master species is added, then a Monod rate is integrated with SciPy.

???+ info "You can run these examples"

    Click **Run** (or Ctrl+Enter), or **Run all** to execute every editor in order. Editors on this page **share a session**.

```pyodide session="monod" height="10-16" install="matplotlib,numpy,scipy,../../wheels/phreeqpython-1.6.2+pyodide-py3-none-any.whl"
from phreeqpython import PhreeqPython
from scipy.integrate import odeint
import numpy as np
import matplotlib.pyplot as plt

pp = PhreeqPython('phreeqc.dat')
pp.add_master_species(element='Phenol', master_species='Phenol', alkalinity=0, gfw=1, egfw=1)
pp.add_species('Phenol = Phenol', 0)
print('Phenol master species added')
```

```pyodide session="monod" height="16-24" install="matplotlib,numpy,scipy,../../wheels/phreeqpython-1.6.2+pyodide-py3-none-any.whl"
def rate_phenol(phenol, _, sol, k_max, k_half):
    S = phenol[0] * 1e-3
    if S < 1e-9:
        return 0
    rate = -k_max * S / (k_half + S)
    return rate * 1e3

solution1 = pp.add_solution({'Phenol': 38.1})
t = np.linspace(0, 3.3e6, 20)
y = odeint(rate_phenol, 38.1, t, args=(solution1, 1.61e-8, 1.7e-3))

fig = plt.figure(figsize=[10, 5])
plt.plot(t / 86400, y, 'r-')
plt.xlabel('Time / days')
plt.ylabel('mg Phenol / L')
plt.title('Phenol degradation')
plt.xlim(0, 40)
plt.grid()
show_plot(fig)
```
