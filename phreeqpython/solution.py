import re
import numbers
from .utility import convert_units
from scipy.integrate import odeint
import numpy as np

class Solution(object):
    """ PhreeqPy Solution Class """

    def __init__(self, phreeqpython, number):
        self.pp = phreeqpython
        self.factor = 1
        self.number = number

    def copy(self):
        """ Create a new copy, with unique solution number, from this solution """
        return self.pp.copy_solution(self.number)

    def add(self, element, amount, units='mmol'):
        """ Add a chemical to the solution """
        # convert to mol
        amount = convert_units(element, amount, units, 'mol')
        self.pp.change_solution(self.number, {element:amount})
        return self

    def remove(self, element, amount, units='mmol'):
        """ Remove a chemical from the solution """
        amount = -convert_units(element, amount, units, 'mol')
        self.pp.change_solution(self.number, {element:amount})
        return self


    def remove_fraction(self, species, fraction):
        """ Remove a fraction of a chemical from the solution """
        current = self.total(species)
        to_remove = current * fraction
        self.remove(species, to_remove)
        return self

    def interact(self, gas):
        self.pp.interact_solution_gas(self.number, gas.number)
        return self


    def equalize(self, phases, to_si=[0], in_phase=[10], with_chemical=[None]):
        """ equalize one or more phases with the solution """
        self.pp.equalize_solution(self.number, phases, to_si, in_phase, with_chemical)

        return self

    def saturate(self, phase, to_si=0, in_phase=10):
        """ Saturate a single phase to the given SI.
        This function can saturate one or multiple phases
        through dissolution. The maximum amount that can be dissolved is given by in_phase
        """
        if(self.si(phase) < 0):
            self.pp.equalize_solution(self.number, phase, to_si, in_phase)

        return self

    # this function can only precipitate
    def desaturate(self, phase, to_si=0):
        """ Desaturate a phase to the given SI.
        This function can only desaturate a phase through precipitation
        """
        self.pp.equalize_solution(self.number, phase, to_si, 0)

        return self

    # change the ph
    def change_ph(self, to_pH, with_chemical=None):
        """ Change the pH of a solution by dosing either HCl and NaOH, or a user supplied acid or base """
        # default to NaOH and HCl
        if not with_chemical:
            if to_pH < self.pH:
                # dose HCl to lower pH
                self.pp.equalize_solution(self.number, "Fix_pH", -to_pH, 10, "HCl")
            else:
                # dose NaOH to raise pH
                self.pp.equalize_solution(self.number, "Fix_pH", -to_pH, 10, "NaOH")
        else:
            self.pp.equalize_solution(self.number, "Fix_pH", -to_pH, 10, with_chemical)
        return self

    def change_temperature(self, to_temperature):
        """ Change the temperature of a solution """
        self.pp.change_solution_temperature(self.number, to_temperature)
        return self

    def total(self, element, units='mmol'):
        """ Returns to total of any given species or element (SLOW!) """
        total = 0
        regexp = "(^|[^A-Z])"+element
        for species, amount in self.species.items():
            if re.search(regexp, species):
                total += convert_units(element, amount, to_units=units)
        return total

    def total_activity(self, element, units='mmol'):
        """ Returns to total of any given species or element (SLOW!) """
        total = 0
        regexp = "(^|[^A-Z])"+element
        for species, amount in self.species_activities.items():
            if re.search(regexp, species):
                total += convert_units(element, amount, to_units=units)
        return total

    def total_element(self, element, units='mmol'):
        """ Returns to total any given element (FAST!) """
        return convert_units(element, self.pp.ip.get_total_element(self.number, element), 'mol', units)

    def activity(self, species, units='mmol'):
        """ Returns the activity of a single species """
        return convert_units(species, self.pp.ip.get_activity(self.number, species), 'mol', units)

    def moles(self, species, units='mmol'):
        """ Returns the moles of a single species """
        return convert_units(species, self.pp.ip.get_moles(self.number, species), 'mol', units)

    def molality(self, species, units='mmol'):
        """ Returns the molality of a single species """
        return convert_units(species, self.pp.ip.get_molality(self.number, species), 'mol', units)

    def si(self, phase):
        """ return the SI of a certain phase """
        return self.pp.ip.get_si(self.number, phase)

    def sr(self, phase):
        """ return the SI of a certain phase """
        return 10**self.pp.ip.get_si(self.number, phase)

    def forget(self):
        """ remove this solution from VIPhreeqc memory """
        self.pp.remove_solutions([self.number])

    def kinetics(self, element, rate_function, time, m0=0, args=()):

        def calc_rate(y, t, m0, *args):
            temp = self.copy()
            temp.add(element, y[0])
            rate = rate_function(temp, y[0], m0, *args)
            temp.forget()
            return rate

        y = odeint(calc_rate, 0, time, args=(m0,)+args)

        y = np.insert(np.diff(y[:,0]), 0, 0)

        for i in range(len(time)):
            t = time[i]
            self.add(element, y[i])
            yield(t, self)

    # Magic functions
    def __add__(self, other):
        """ add two solutions """
        if not isinstance(other,Solution):
            raise TypeError("Invalid operation, only addition of two solutions is allowed")
        mixture= {self:self.factor, other:other.factor}
        #print mixture
        mixture = self.pp.mix_solutions({self:self.factor,other:other.factor})
        # reset factors to 1
        self.factor = 1
        other.factor = 1

        return mixture

    def __truediv__(self, other):
        """ Python 3 support """
        return self.__div__(other)

    def __div__(self, other):
        """ set devision factor """
        if not isinstance(other,numbers.Real):
            raise TypeError("Invalid operation, only division by a number is allowed")
        self.factor = 1/float(other)
        return self

    def __mul__(self, other):
        """ set multiplication factor """
        if not isinstance(other,numbers.Real):
            raise TypeError("Invalid operation, only division by a number is allowed")
        self.factor = float(other)
        return self

    # Accessor methods
    @property
    def I(self):
        """ Solution ionic strength """
        return self.pp.ip.get_mu(self.number)
    def mu(self):
        """ Solution ionic strength """
        return self.I
    @property
    def pH(self):
        """ Solution pH """
        return self.pp.ip.get_ph(self.number)
    @property
    def sc(self):
        return self.pp.ip.get_sc(self.number)
    @property
    def temperature(self):
        return self.pp.ip.get_temperature(self.number)
    @property
    def mass(self):
        return self.pp.ip.get_mass(self.number)
    @property
    def pe(self):
        return self.pp.ip.get_pe(self.number)
    @property
    def phases(self):
        return self.pp.ip.get_phases_si(self.number)
    @property
    def elements(self):
        return self.pp.ip.get_elements_totals(self.number)
    @property
    def species(self, units='mmol'):
        return self.pp.ip.get_species_moles(self.number)
    @property
    def species_moles(self, units='mmol'):
        return self.pp.ip.get_species_moles(self.number)
    @property
    def species_molalities(self, units='mmol'):
        return self.pp.ip.get_species_molalities(self.number)
    @property
    def species_activities(self, units='mmol'):
        return self.pp.ip.get_species_activities(self.number)
    @property
    def masters_species(self):
        """ Returns a Phreeqc output like species table """
        return self.pp.ip.get_masters_species(self.number)

    # pretty printing
    def __str__(self):
        return "<PhreeqPython.Solution."+self.__class__.__name__ + " with number '" + self.number + "'>"
