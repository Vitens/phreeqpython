---
icon: lucide/beaker
---

# Calcite dissolution

Calcite dissolution as a function of CO₂ pressure, after [Appelo's calcite example](http://hydrochemistry.eu/exmpls/calcite.html). Equilibrium along a CO₂ titration is compared with mixing two end members.

???+ info "You can run these examples"

    Click **Run** (or Ctrl+Enter), or **Run all** to execute every editor in order. Editors on this page **share a session**.

!!! warning "Changes are additive"

    The loop adds CO₂ to `solution0` in place. Run it once. To start over, rerun from the first editor.

```pyodide session="calcite" height="16-24" install="matplotlib,numpy,../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
from phreeqpython import PhreeqPython
import matplotlib.pyplot as plt

pp = PhreeqPython(database='phreeqc.dat')

solution0 = pp.add_solution({})
solution1 = pp.add_solution({}).equalize(['Calcite', 'CO2(g)'], [0, -1.7])
solution2 = pp.add_solution({}).equalize(['Calcite', 'CO2(g)'], [0, -3.5])
solution3 = solution1 * 0.5 + solution2 * 0.5

x, y = [], []
for i in range(30):
    solution0.add('CO2', 3.5 / 30)
    solution0.saturate('Calcite')
    x.append(solution0.sr('CO2(g)') * 100)
    y.append(solution0.total_element('Ca'))

print('points', len(x))
```

```pyodide session="calcite" height="12-18" install="matplotlib,numpy,../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
fig = plt.figure(figsize=[7, 7])
plt.plot(x, y, 'rs-', label='equilibrium')
plt.plot(
    [solution1.sr('CO2(g)') * 1e2, solution2.sr('CO2(g)') * 1e2],
    [solution1.total_element('Ca'), solution2.total_element('Ca')],
    '-gx',
    label='mixing line',
)
plt.plot(solution3.sr('CO2(g)') * 1e2, solution3.total_element('Ca'), '-b^', label='1:1')
plt.xlim([0, 3])
plt.ylim([0, 3])
plt.grid()
plt.legend()
plt.title('Calcite equilibrium')
show_plot(fig)
```
