---
icon: lucide/beaker
---

# Kinetic dissolution of quartz

Quartz dissolution over five years, after [Appelo's quartz kinetics example](http://hydrochemistry.eu/exmpls/kin_qu.html). The first method uses `solution.kinetics()`; the second integrates the same rate with SciPy `odeint`.

???+ info "You can run these examples"

    Click **Run** (or Ctrl+Enter), or **Run all** to execute every editor in order. Editors on this page **share a session**. SciPy is installed with the first cell; the loops can take a few seconds.

```pyodide session="quartz" height="18-26" install="matplotlib,numpy,scipy,../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
from phreeqpython import PhreeqPython
import numpy as np
import matplotlib.pyplot as plt

pp = PhreeqPython('phreeqc.dat')

def ratefun(sol, quartz_dissolved, m0, A0, V):
    m = m0 - quartz_dissolved
    rate = (A0 / V) * (m / m0) ** 0.67 * 10 ** -13.7 * (1 - sol.sr('Quartz'))
    return rate * 1e3

solution1 = pp.add_solution({})
year = 365 * 24 * 3600
t, y = np.array([]), []

for time, sol in solution1.kinetics(
    'SiO2',
    rate_function=ratefun,
    time=np.linspace(0, 5 * year, 15),
    m0=158.5,
    args=(23.13, 0.16),
):
    t = np.append(t, time)
    y.append(sol.total_element('Si', units='mmol'))

fig = plt.figure(figsize=[10, 5])
plt.plot(t / year, y, 'rs-')
plt.xlim([0, 5])
plt.ylim([0, 0.12])
plt.xlabel('Years')
plt.ylabel('mmol/l')
plt.title('Quartz dissolution (kinetics helper)')
plt.grid()
show_plot(fig)
```

## Same rate with odeint

```pyodide session="quartz" height="18-26" install="matplotlib,numpy,scipy,../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
from scipy.integrate import odeint

def rate_quartz(quartz_dissolved, time, sol, A0, V, m0):
    temp = sol.copy()
    temp.add('SiO2', quartz_dissolved[0], 'mol')
    m = m0 - quartz_dissolved[0]
    rate = (A0 / V) * (m / m0) ** 0.67 * 10 ** -13.7 * (1 - temp.sr('Quartz'))
    temp.forget()
    return rate

solution2 = pp.add_solution({})
tt = np.linspace(0, 5 * year, 15)
yy = odeint(rate_quartz, 0, tt, args=(solution2, 23.13, 0.16, 158.5))

fig = plt.figure(figsize=[10, 5])
plt.plot(tt / year, yy * 1e3, 'rs-')
plt.xlim([0, 5])
plt.ylim([0, 0.12])
plt.xlabel('Years')
plt.ylabel('mmol/l')
plt.title('Quartz dissolution (odeint)')
plt.grid()
show_plot(fig)
```
