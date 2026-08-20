---
icon: lucide/cog
---

# How it works

PHREEQC is a geochemical calculation engine. PhreeqPython does not replace that engine: it talks to it through [VIPhreeqc](https://github.com/Vitens/VIPhreeqc), keeps results in memory, and lets you query or change them from Python.

## Classic (Batch) PHREEQC

PHREEQC is built around **input files** and **tabular output**. You write a complete script (`SOLUTION`, `REACTION`, `EQUILIBRIUM_PHASES`, …), run it once, and read the results from an output file or a `SELECTED_OUTPUT` table — often filled with `USER_PUNCH`.

``` mermaid
flowchart LR
  A[Input file] --> B[PHREEQC]
  B --> C[Output file]
  B --> D[Selected output table]
```

That workflow is a good fit for a **once-through analysis**. The drawback of tabular output is that you have to **define beforehand** which columns you want: pH, conductivity, specific molalities, saturation indices, and so on. If you later need another species or property, you change the input and run the whole script again.

It also gets awkward and slow for **large, interactive models** with many different solutions: each step means rewriting an input file, rerunning PHREEQC, and parsing tables, instead of keeping those solutions in memory and querying them as you go.

## IPhreeqc: PHREEQC as a library

[IPhreeqc](https://www.usgs.gov/software/phreeqc-version-3) is the USGS module that runs PHREEQC as a **library** instead of the standalone batch program. From Python you send the same input (`SOLUTION`, `REACTION`, `USER_PUNCH`, …) as a string and read the selected-output table from memory. No input or output files.

``` mermaid
flowchart LR
  P[Python] -->|write| I[Input]
  I -->|run| E[IPhreeqc]
  E --> O[Selected output]
  O -->|parse| P
```

That replaces the file round-trip, so you can drive PHREEQC from an interactive Python model. The calculation model is unchanged: you still declare `SELECTED_OUTPUT` / `USER_PUNCH` before the run, and each step is still write input, run, parse the table.

## VIPhreeqc: query the engine directly

IPhreeqc still returns a **selected-output table**. [VIPhreeqc](https://github.com/Vitens/VIPhreeqc) extends IPhreeqc with getters for solution and phase properties that still live in the engine: speciation, pH, conductivity, saturation indices, and similar values.

You no longer have to declare `SELECTED_OUTPUT` up front. After a calculation, PhreeqPython can call getters such as `GetPH` and `GetSpecies` on the engine. PHREEQC keeps the solutions; PhreeqPython sends commands and reads those properties back.

``` mermaid
flowchart LR
  PP[PhreeqPython] -->|snippets| E[PHREEQC]
  E -->|"GetPH, GetSpecies, ..."| PP
  E --> S[Solutions]
```

## What PhreeqPython adds

PhreeqPython sits on top of VIPhreeqc. Python methods generate **short PHREEQC snippets**, send them to the engine, and wrap the numbered solutions (and gases, phases) as objects.

The snippet generation is hidden behind those objects. `add_solution(...)` becomes a `SOLUTION` block; `solution.add(...)` becomes `USE SOLUTION` plus `REACTION`. PHREEQC stores each result as a numbered solution, so later calls can use, change, or query any of them.

``` mermaid
flowchart LR
  PP[PhreeqPython] -->|snippets| E[PHREEQC]
  E -->|"GetPH, GetSpecies, ..."| PP
  E --> S0[Solution 0]
  E --> S1[Solution 1]
  E --> S2[Solution 2]
```

That is why PhreeqPython can keep a **stateful** simulation: change a solution, inspect it, change it again, without rewriting and rerunning a full input file.

## Example: add a solution, then add KCl

Create water at pH 7 with 1 mmol/kgw Na and Cl, then add 1 mmol KCl.

=== "Python"

    ``` python
    from phreeqpython import PhreeqPython

    pp = PhreeqPython()
    solution = pp.add_solution({
        'pH': 7,
        'units': 'mmol/kgw',
        'Na': 1,
        'Cl': 1,
    })
    solution.add('KCl', 1)

    print(solution.pH)          # 7.0
    print(solution.total('K'))  # 1.0 mmol
    print(solution.total('Cl')) # 2.0 mmol
    ```

=== "Generated PHREEQC"

    `add_solution` sends:

    ```
    SOLUTION 0
      pH 7
      units mmol/kgw
      Na 1
      Cl 1
    SAVE SOLUTION 0
    END
    ```

    `solution.add('KCl', 1)` then sends:

    ```
    USE SOLUTION 0
    REACTION 1
    KCl 0.001
    1 mol
    SAVE SOLUTION 0
    END
    ```

    The second snippet **reuses** solution 0. Amounts in `REACTION` are in moles, so 1 mmol KCl is written as `0.001` with `1 mol`. After both steps you can query pH, totals, speciation, conductivity, or anything else VIPhreeqc exposes — none of that had to be listed in the input.

=== "Classic PHREEQC"

    ```
    SELECTED_OUTPUT
      -file output.tsv

    USER_PUNCH
      -headings pH K_mmol Cl_mmol
      -start
    10 PUNCH -LA("H+")
    20 PUNCH TOT("K") * 1000
    30 PUNCH TOT("Cl") * 1000
      -end

    SOLUTION 1
      pH 7
      units mmol/kgw
      Na 1
      Cl 1
    REACTION 1
      KCl 0.001
      1 mol
    END
    ```

    `TOT` is mol/kgw, so multiply by 1000 for mmol. pH is `-LA("H+")`. If you later need another species or property, you add another `PUNCH` line and run the whole script again.

The classic script puts both steps in one file and uses `USER_PUNCH` (with `SELECTED_OUTPUT`) to define the output columns before the run. In PhreeqPython those queries are ordinary Python attributes and methods, after each step.

## See the generated input

Set `pp.ip.debug = True` (or `PhreeqPython(debug=True)`) to print every snippet before it is sent to the engine.

``` python
pp = PhreeqPython()
pp.ip.debug = True
```

The editor below runs the example in the browser. Click **Run** (or Ctrl+Enter); the output is the PHREEQC that PhreeqPython generated, then a few queried properties.

```pyodide height="14-28" install="../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
from phreeqpython import PhreeqPython

pp = PhreeqPython()
pp.ip.debug = True

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
