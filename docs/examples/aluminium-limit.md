---
icon: lucide/beaker
---

# Aluminium drinking-water limit

Al concentration exceeds a 0.2 mg/kgw drinking-water limit at low and high pH, after [Appelo's aluminium example](http://hydrochemistry.eu/exmpls/al_conc.html). The pH values below are where that Al total is in equilibrium with gibbsite.

???+ info "You can run these examples"

    Click **Run** (or Ctrl+Enter).

```pyodide session="al" height="8-12" install="../../wheels/phreeqpython-1.6.2-py3-none-any.whl"
from phreeqpython import PhreeqPython

pp = PhreeqPython('phreeqc.dat')
print('Lower limit pH', pp.add_solution({'Al': '0.2 mg/kgw', 'pH': '4 Gibbsite'}).pH)
print('Upper limit pH', pp.add_solution({'Al': '0.2 mg/kgw', 'pH': '8 Gibbsite'}).pH)
```
