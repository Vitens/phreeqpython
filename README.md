<p align="center">		
   <img src="https://github.com/Vitens/phreeqpython/blob/master/logo.png" alt="Phreeqpython Logo"/>		
 </p>
 
PhreeqPython is an object oriented wrapper around the ([VIPhreeqc](https://www.github.com/Vitens/VIPhreeqc)) extension of the Phreeqc chemical calculation engine ([Parkhurst&Appello](http://wwwbrr.cr.usgs.gov/projects/GWC_coupled/phreeqc/)), written in Python.

## Features
PhreeqPython greatly simplifies adding solutions and querying their properties:

```python
pp = PhreeqPython()
# add a solution consisting of 1 mmol CaCl2 and 2 mmol NaHCO3
solution = pp.add_solution({'CaCl2':1.0,'NaHCO3':2.0})
print solution.pH               # 8.12
print solution.sc               # 427.32
print solution.si('Calcite')    # 0.38
print solution.species['HCO3-'] # 0.0019
print solution.elements['Cl']   # 0.002 mol
```
Allows for simple chemical and precipitation/dissolution reactions:
```python
solution.add('NaOH',0.5)
print solution.pH               # 9.47
solution.desaturate('Calcite')  # desaturate to SI 0
print solution.total('Ca')      # 1 mmol
```
And even allows for addition, devision and multiplication of solutions to form new mixtures:
```python
solution2 = pp.add_solution({'KCl':1.0})
# create mixture of 50% solution and 50% solution2
solution3 = solution * 0.5 + solution2 * 0.5
print solution3.total('K','mol')      # 0.0005 mol
```

## Installation
* ```pip install -U phreeqpython```

## Requirements
* 64 bit Python
* Windows, OSX or Linux
  * Using PhreeqPython on Windows requires installing [Visual C++ Redistributable 2015](https://www.microsoft.com/en-us/download/details.aspx?id=48145)

## Unit Tests
| **Mac/Linux** | **Windows** | **Coverage** |
|---|---|---|
| [![Build Status](https://travis-ci.org/Vitens/phreeqpython.svg?branch=master)](https://travis-ci.org/Vitens/phreeqpython) | [![Build status](https://ci.appveyor.com/api/projects/status/lr1jwspxdkgo85bv?svg=true)](https://ci.appveyor.com/project/Vitens/phreeqpython) | [![codecov](https://codecov.io/gh/Vitens/phreeqpython/branch/master/graph/badge.svg)](https://codecov.io/gh/Vitens/phreeqpython) |


## Acknowledgements
This project makes use of the ([Phreeqc](http://wwwbrr.cr.usgs.gov/projects/GWC_coupled/phreeqc/)) (David Parkhurst & Tony Apello) calcution engine and is (partly) derived from the ([PhreeqPy]([http://www.phreeqpy.com])) extension for IPhreeqc (Mike Müller)

## About Vitens

Vitens is the largest drinking water company in The Netherlands. We deliver top quality drinking water to 5.6 million people and companies in the provinces Flevoland, Fryslân, Gelderland, Utrecht and Overijssel and some municipalities in Drenthe and Noord-Holland. Annually we deliver 350 million m³ water with 1,400 employees, 100 water treatment works and 49,000 kilometres of water mains.

One of our main focus points is using advanced water quality, quantity and hydraulics models to further improve and optimize our treatment and distribution processes.

## Licence

Copyright 2016 Vitens

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
