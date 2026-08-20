---
icon: lucide/beaker
---

# Ca–F equilibrium with fluorite

The relation between fluoride and calcium in water, after [Appelo's fluorite example](http://hydrochemistry.eu/exmpls/ca_f.html). Calcite and fluorite stay at equilibrium while albite dissolves.

???+ info "You can run these examples"

    Click **Run** (or Ctrl+Enter), or **Run all** to execute every editor in order. Editors on this page **share a session**.

```pyodide session="caf" height="18-28" install="matplotlib,numpy,../../wheels/phreeqpython-1.6.2+pyodide-py3-none-any.whl"
from phreeqpython import PhreeqPython
import matplotlib.pyplot as plt

pp = PhreeqPython()
solution1 = pp.add_solution({
    'pH': '7 charge',
    'C': '1 CO2(g) -1',
    'Ca': '1 Calcite',
    'F': '1 Fluorite',
})

x, y, yy = [], [], []

for i in range(16):
    x.append(solution1.total_element('Ca', 'mg'))
    y.append(solution1.total_element('F', 'mg'))
    yy.append(solution1.pH)
    solution1.add('NaAlSi3O8', 7.5 / 15)
    solution1.equalize(
        ['Fluorite', 'Calcite', 'Quartz', 'Kaolinite'],
        ['', '', 0, 0],
        ['', '', 0, 0],
    )

print('points', len(x), 'final pH', round(yy[-1], 2))
```

```pyodide session="caf" height="14-22" install="matplotlib,numpy,../../wheels/phreeqpython-1.6.2+pyodide-py3-none-any.whl"
fig = plt.figure(figsize=[10, 5])
ax = plt.gca()
ax2 = ax.twinx()
ax.plot(x, y, 'rs-', label='F')
ax2.plot(x, yy, 'gd-', label='pH')
ax.set_ylim([0, 10])
ax.set_xlim([0, 160])
ax2.set_ylim([6.5, 7.5])
ax.set_xlabel('Ca (mg/l)')
ax.set_ylabel('F (mg/l)')
ax2.set_ylabel('pH (-)')
ax.grid()
plt.title('Fluorite equilibrium during Na-feldspar dissolution')
fig.legend(loc=1, bbox_to_anchor=(1, 1), bbox_transform=ax.transAxes)
show_plot(fig)
```
