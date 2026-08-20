---
icon: lucide/play
---

# Running an analysis

After [installing](installation.md) PhreeqPython, an analysis is: create an engine, add a solution, query it, and remove it when you no longer need it. Nothing has to be listed in `SELECTED_OUTPUT` first.

???+ info "You can run these examples"

    Click **Run** (or Ctrl+Enter), or **Run all** to execute every editor in order. The first run loads Pyodide and can take a few seconds. Editors on this page **share a session**, so later cells reuse `pp` and `solution`.

## Create a PhreeqPython instance

Import the package and construct a [`PhreeqPython`](../reference/phreeqpython.md#phreeqpython.PhreeqPython) object. That object is the engine: it loads a thermodynamic database (default `vitens.dat`) and keeps the numbered PHREEQC entities in memory — [solutions](../reference/solution.md#solution.Solution), [gases](../reference/gas.md#gas.Gas), and [equilibrium phases](../reference/equilibriumphase.md#equilibriumphase.EquilibriumPhase).

```pyodide session="analysis" height="6-10" install="../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
from phreeqpython import PhreeqPython

pp = PhreeqPython()
print('solutions in the engine', pp.get_solution_list())
```

Every [`Solution`](../reference/solution.md#solution.Solution) (and gas or phase) you create is stored on this instance. Mixing, copying, and reacting always go through that same engine.

!!! warning "Do not mix solutions from different instances"

    A `Solution` is a handle to a number *inside one engine*. `a + b` (and any other interaction) only works when both solutions belong to the same `PhreeqPython` instance. Creating a second instance starts a second, independent PHREEQC engine; solutions from one cannot be mixed, copied, or reacted with solutions from the other.

Set `pp.ip.debug = True` (or [`PhreeqPython(debug=True)`](../reference/phreeqpython.md#phreeqpython.PhreeqPython.__init__)) to print the PHREEQC snippets before they are sent.

## Add a solution

[`add_solution`](../reference/phreeqpython.md#phreeqpython.PhreeqPython.add_solution) creates water in the engine from PHREEQC `SOLUTION` keywords (pH, units, element totals, …). PhreeqPython assigns a number automatically: the first solution is `0`, then `1`, `2`, and so on. The Python object is a handle to that numbered solution ([`solution.number`](../reference/solution.md#solution.Solution.number)).

```pyodide session="analysis" height="12-20" install="../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
solution = pp.add_solution({
    'pH': 7,
    'units': 'mmol/kgw',
    'Na': 1,
    'Cl': 1,
})
print(solution)
print('number', solution.number)
print('solutions in the engine', pp.get_solution_list())
```

Copies and mixtures also get a new number. `add_solution_simple` is for a known chemical composition (for example 1 mmol NaOH); see [Adding solutions](../guide/adding-solutions.md).

## Query a solution

After each calculation you can read [`Solution`](../reference/solution.md#solution.Solution) properties directly; [`pH`](../reference/solution.md#solution.Solution.pH), [`total`](../reference/solution.md#solution.Solution.total), speciation, saturation indices, etc.

```pyodide session="analysis" height="8-14" install="../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
print('pH', solution.pH)
print('Na mmol', solution.total('Na'))
print('Cl mmol', solution.total('Cl'))
print('SC', round(solution.sc, 1), 'uS/cm')
```

## Forget a solution

PHREEQC keeps every numbered solution in the engine until you delete it. `add_solution`, [`copy()`](../reference/solution.md#solution.Solution.copy), and mixing (`+` / `*`) each allocate a new number, so a long-running model — especially a loop that copies solutions, or a kinetic rate function that makes a temporary copy — can accumulate unused solutions and grow in memory.

Call [`forget()`](../reference/solution.md#solution.Solution.forget) when you are done with a solution. That sends a PHREEQC `DELETE` for its number. Use [`get_solution_list()`](../reference/phreeqpython.md#phreeqpython.PhreeqPython.get_solution_list) to see which numbers are still in the engine.

```pyodide session="analysis" height="6-10" install="../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
print('before', pp.get_solution_list())
solution.forget()
print('after', pp.get_solution_list())
```