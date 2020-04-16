import re
import numbers
from .utility import convert_units
import numpy as np
import json

class Surface(object):
    """ PhreeqPy Solution Class """
    def __init__(self, phreeqpython, number):
        self.pp = phreeqpython
        self.number = number
        self.surface = json.loads(phreeqpython.ip.get_surface_json(number).decode("utf-8"))

    def copy(self):
        """ Create a new copy, with unique solution number, from this solution """
        return self.pp.copy_surface(self.number)

    def forget(self):
        """ Create a new copy, with unique solution number, from this solution """
        return self.pp.remove_surfaces([self.number])

    @property
    def ddl_limit(self):
        return float(self.surface["DDL_limit"])

    @property
    def ddl_viscosity(self):
        return int(self.surface["DDL_viscosity"])
    
    @property
    def debeye_lengths(self):
        return int(self.surface["debeye_lengths"])
    
    @property
    def dl_type(self):
        return int(self.surface["dl_type"])
    
    @property
    def n_solution(self):
        return int(self.surface["n_solution"])
    
    @property
    def only_counter_ions(self):
        return int(self.surface["only_counter_ions"])
    
    @property
    def sites_units(self):
        return int(self.surface["sites_units"])
    
    @property
    def solution_equilibria(self):
        return int(self.surface["solution_equilibria"])
    
    @property
    def thickness(self):
        return float(self.surface["thickness"])
    
    @property
    def transport(self):
        return int(self.surface["transport"])
    
    @property
    def surface_type(self):    
        return int(self.surface["type"])
    
    @property
    def specific_area(self):
        return float(self.surface['components'][2]['specific_area'])
    
    @property
    def grams(self):
        return float(self.surface['components'][2]['grams'])
    
    @property
    def mass_water(self):
        return float(self.surface['components'][2]['mass_water'])
    
    @property
    def la_psi(self):
        return float(self.surface['components'][2]['la_psi'])
    
    @property
    def capcitance0(self):
        return int(self.surface['components'][2]['capacitance0'])
    
    @property
    def capcitance1(self):
        return int(self.surface['components'][2]['capacitance1'])
    
    @property
    def charge_balance_Hfo(self):
        return float(self.surface['components'][2]['charge_balance'])
    
    @property
    def charge_balance_Hfo_s(self):
        return float(self.surface['components'][0]['charge_balance'])
    
    @property
    def charge_balance_Hfo_w(self):
        return float(self.surface['components'][1]['charge_balance'])
    
    @property
    def totals_Hfo_s(self):
        return float(self.surface['components'][0]['totals']['Hfo_s'])
    
    @property
    def totals_Hfo_w(self):
        return float(self.surface['components'][1]['totals']['Hfo_w'])

#   todo: move this calculation to VIPhreeqc
    @property
    def sigma(self):
        fcmol = 96493.5
        charge = self.charge_balance_Hfo
        area = self.specific_area
        gram = self.grams
        sigma = charge * fcmol / (area * gram)
        return sigma
    
    @property
    def print_surface(self):
        return self.surface