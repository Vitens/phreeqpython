---
icon: lucide/beaker
---

# Carbonic acid equilibrium

Carbonic acid (H₂CO₃), bicarbonate (HCO₃⁻) and carbonate (CO₃²⁻) form in water through:

- CO₂ + H₂O ⇌ H₂CO₃
- H₂CO₃ ⇌ HCO₃⁻ + H⁺
- HCO₃⁻ ⇌ CO₃²⁻ + H⁺

The distribution depends on pH. This example titrates 1 mmol NaHCO₃ from pH 0 to 14.

???+ info "You can run these examples"

    Click **Run** (or Ctrl+Enter). Editors on this page **share a session**: run them in order. The loop has many pH steps and can take a short while in the browser.

```pyodide session="carbonic" height="8-14" install="matplotlib,numpy,../../wheels/phreeqpython-1.6.2+pyodide-py3-none-any.whl"
from phreeqpython import PhreeqPython
import numpy as np
import matplotlib.pyplot as plt

pp = PhreeqPython()
solution = pp.add_solution_simple({'NaHCO3': 1.0})
print('pH {:.2f}, SC {:.2f} uS/cm'.format(solution.pH, solution.sc))
```

!!! warning "Changes are additive"

    `change_ph` doses acid or base **into the same solution**. Run the loop once. To start over, rerun the first editor.

```pyodide session="carbonic" height="14-22" install="matplotlib,numpy,../../wheels/phreeqpython-1.6.2+pyodide-py3-none-any.whl"
phs, co2, hco3, co3 = [], [], [], []

for pH in np.arange(0, 14.1, 0.2):
    solution.change_ph(pH)
    phs.append(pH)
    co2.append(solution.total('CO2') * 1000)
    hco3.append(solution.total('HCO3') * 1000)
    co3.append(solution.total('CO3') * 1000)

fig = plt.figure(figsize=[10, 5])
plt.plot(phs, co2, label='CO2')
plt.plot(phs, hco3, label='HCO3-')
plt.plot(phs, co3, label='CO3-2')
plt.xlabel('pH')
plt.ylabel('Concentration (mmol)')
plt.title('Carbonic acid, bicarbonate, carbonate')
plt.legend()
show_plot(fig)
```
