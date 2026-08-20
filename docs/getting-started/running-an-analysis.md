---
icon: lucide/play
---

# Running an analysis

After [installing](installation.md) PhreeqPython, an analysis is: create an engine, add a solution, then query or change it. Nothing has to be listed in `SELECTED_OUTPUT` first.

???+ info "You can run this example"

    Click **Run** (or Ctrl+Enter). The first run loads Pyodide and can take a few seconds.

```pyodide session="analysis" height="14-22" install="../../wheels/phreeqpython-1.6.2+pyodide-py3-none-any.whl"
from phreeqpython import PhreeqPython

pp = PhreeqPython()
solution = pp.add_solution({
    'pH': 7,
    'units': 'mmol/kgw',
    'Na': 1,
    'Cl': 1,
})
solution.add('KCl', 1)

print('pH', solution.pH)
print('K mmol', solution.total('K'))
print('Cl mmol', solution.total('Cl'))
```

That is the whole loop: `add_solution` creates water in the engine, `add` reacts KCl into it, and `pH` / `total` read properties back.

Set `pp.ip.debug = True` (or `PhreeqPython(debug=True)`) to print the PHREEQC snippets before they are sent.

Next: the [Solutions](../guide/solutions.md) guide covers creating, querying, and changing solutions in more detail. The [Examples](../examples/index.md) tab has worked calculations you can run in the browser.
