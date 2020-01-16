import re
import numbers
from .utility import convert_units
import numpy as np

class Gas(object):
    """ PhreeqPy Solution Class """
    def __init__(self, phreeqpython, number):
        self.pp = phreeqpython
        self.number = number

    def copy(self):
        """ Create a new copy, with unique solution number, from this solution """
        return self.pp.copy_gas(self.number)

    def forget(self):
        """ Create a new copy, with unique solution number, from this solution """
        return self.pp.remove_gases([self.number])

    @property
    def pressure(self):
        return self.pp.ip.get_gas_pressure(self.number)
    @property
    def volume(self):
        return self.pp.ip.get_gas_volume(self.number) 
    @property
    def total_moles(self):
        return self.pp.ip.get_gas_total_moles(self.number) 

    @property
    def components(self):
        return self.pp.ip.get_gas_components_moles(self.number) 
    @property
    def fractions(self):
        return self.pp.ip.get_gas_components_fractions(self.number) 
    @property
    def partial_pressures(self):
        return self.pp.ip.get_gas_components_pressures(self.number) 

    @property
    def dry_fractions(self):
        try:
            total = self.total_moles - self.components['H2O(g)']
        except:
            total = self.total_moles

        return {name: value/total for (name, value) in self.components.items()}
