import re
import numbers
from .utility import convert_units
import numpy as np

class Surface(object):
    """ PhreeqPy Solution Class """
    def __init__(self, phreeqpython, number):
        self.pp = phreeqpython
        self.number = number

    def copy(self):
        """ Create a new copy, with unique solution number, from this solution """
        return self.pp.copy_surface(self.number)

    def forget(self):
        """ Create a new copy, with unique solution number, from this solution """
        return self.pp.remove_surfaces([self.number])

    @property
    def thickness(self):
        return self.pp.ip.get_surface_thickness(self.number)

    @property
    def surface_charge_balance(self):
        return self.pp.ip.get_surface_charge_balance(self.number)