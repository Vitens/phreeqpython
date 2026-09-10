---
icon: lucide/info
title: About PhreeqPython
hide:
  - toc
---

![PhreeqPython logo](../resources/logo.png){ .logo-home }

## About PhreeqPython

PhreeqPython is an object-oriented Python wrapper around [VIPhreeqc](https://github.com/Vitens/VIPhreeqc), Vitens' extension of the [PHREEQC](https://www.usgs.gov/software/phreeqc-version-3) geochemical calculation engine (Parkhurst & Appelo).

Rather than writing a PHREEQC input script and running it as a single calculation, PhreeqPython keeps solutions, gases, and phases in memory as objects. You can change them stepwise, query properties such as pH, speciation, and saturation indices at any point, and mix or react them further without rebuilding the whole simulation.

That makes it practical to run dynamic simulations and real-time models, and to use PHREEQC together with the rest of the Python ecosystem, like NumPy, pandas, Matplotlib, or web and control applications.

## Development
PhreeqPython is developed at [Vitens](https://www.vitens.nl/), the largest drinking water company in the Netherlands, where it supports treatment and distribution modelling. It is partly derived from [PhreeqPy](http://www.phreeqpy.com/) (Mike Müller) and ships with bundled VIPhreeqc libraries for Windows, macOS, Linux, and WebAssembly (Pyodide).


## Acknowledgements
This project makes use of the (Phreeqc) (David Parkhurst & Tony Apello) calcution engine and is (partly) derived from the (PhreeqPy) extension for IPhreeqc (Mike Müller)

## License
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
