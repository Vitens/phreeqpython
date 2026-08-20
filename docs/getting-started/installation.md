---
icon: lucide/download
---

# Installation

PhreeqPython is available on PyPI and can be installed with `pip` or `uv`. The wheel comes bundled with a [VIPhreeqc](https://github.com/Vitens/VIPhreeqc) shared library and several default databases, so you do not need a separate PHREEQC install.

=== "pip"

    ``` bash
    pip install -U phreeqpython
    ```

=== "uv"

    ``` bash
    uv add phreeqpython
    ```

    Or, without a project:

    ``` bash
    uv pip install phreeqpython
    ```

## Platforms

PhreeqPython is **64-bit only** and ships a native library per platform:

| Platform | Library | Notes |
| --- | --- | --- |
| Windows | `viphreeqc.dll` | Needs the [Visual C++ Redistributable 2015](https://www.microsoft.com/en-us/download/details.aspx?id=48145) (or later 2015–2022) |
| macOS | `viphreeqc.dylib` | |
| Linux | `viphreeqc.so` | |
| WebAssembly | `viphreeqcwasm.so` | Pyodide / browser (used by these docs) |

Requires **Python 3** (64-bit). There is no 32-bit build.

## Dependencies

Installed automatically with the package:

- [`numpy`](https://numpy.org/)
- [`periodictable`](https://periodictable.readthedocs.io/)

### Optional: kinetics

`solution.kinetics()` uses SciPy to integrate a Python rate function:

=== "pip"

    ``` bash
    pip install 'phreeqpython[kinetics]'
    ```

=== "uv"

    ``` bash
    uv add 'phreeqpython[kinetics]'
    ```

That extra only adds [`scipy`](https://scipy.org/). It is not PHREEQC's `KINETICS` keyword.

## From source

=== "pip"

    ``` bash
    git clone https://github.com/Vitens/phreeqpython.git
    cd phreeqpython
    pip install .
    ```

    Latest `master` without cloning:

    ``` bash
    pip install git+https://github.com/Vitens/phreeqpython.git
    ```

=== "uv"

    ``` bash
    git clone https://github.com/Vitens/phreeqpython.git
    cd phreeqpython
    uv pip install .
    ```

    Latest `master` without cloning:

    ``` bash
    uv add git+https://github.com/Vitens/phreeqpython.git
    ```

## Check the install

``` python
from phreeqpython import PhreeqPython

pp = PhreeqPython()
print(pp.add_solution({'pH': 7}).pH)
```

If the native library cannot be loaded on Windows, install the Visual C++ Redistributable linked above and retry.

Next: [Running an analysis](running-an-analysis.md).
