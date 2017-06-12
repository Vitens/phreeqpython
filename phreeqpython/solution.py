import re
import numbers

class Solution(object):
    """ PhreeqPy Solution Class """

    def __init__(self, phreeqpython, number):
        self.pp = phreeqpython
        self.factor = 1
        self.number = number

    def copy(self):
        """ Create a new copy, with unique solution number, from this solution """
        return self.pp.copy_solution(self.number)

    def add(self, element, mmol):
        """ Add a chemical to the solution """
        self.pp.change_solution(self.number, {element:mmol})

    def remove(self, element, mmol):
        """ Remove a chemical from the solution """
        mmol = -mmol
        self.pp.change_solution(self.number, {element:mmol})

    def remove_fraction(self, species, fraction):
        """ Remove a fraction of a chemical from the solution """
        current = self.total(species)
        to_remove = 1000 * current * fraction
        self.remove(species, to_remove)

    def saturate(self, phase, to_si=0, in_phase=10):
        """ Saturate (or desaturate) a phase to the given SI.
        This function can both desaturate a phase through precipitation, or saturate a phase
        through dissolution. The maximum amount that can be dissolved is given by in_phase
        """
        self.pp.equalize_solution(self.number, phase, to_si, in_phase)

    # this function can only precipitate
    def desaturate(self, phase, to_si=0):
        """ Desaturate a phase to the given SI.
        This function can only desaturate a phase through precipitation
        """
        self.pp.equalize_solution(self.number, phase, to_si, 0)

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

    def change_temperature(self, to_temperature):
        """ Change the temperature of a solution """
        self.pp.change_solution_temperature(self.number, to_temperature)

    def total(self, element):
        """ Returns to total of any given species or element (SLOW!) """
        total = 0
        regexp = "(^|[^A-Z])"+element
        for species, amount in self.species.items():
            if re.search(regexp, species):
                total += amount
        return total

    def total_activity(self, element):
        """ Returns to total of any given species or element (SLOW!) """
        total = 0
        regexp = "(^|[^A-Z])"+element
        for species, amount in self.species_activities.items():
            if re.search(regexp, species):
                total += amount
        return total

    def total_element(self, element):
        """ Returns to total any given element (FAST!) """
        return self.pp.ip.get_total_element(self.number, element)

    def activity(self, species):
        """ Returns the activity of a single species """
        return self.pp.ip.get_activity(self.number, species)

    def moles(self, species):
        """ Returns the moles of a single species """
        return self.pp.ip.get_moles(self.number, species)

    def molality(self, species):
        """ Returns the moles of a single species """
        return self.pp.ip.get_molality(self.number, species)

    def si(self, phase):
        """ return the SI of a certain phase """
        return self.pp.ip.get_si(self.number, phase)

    def forget(self):
        """ remove this solution from VIPhreeqc memory """
        self.pp.remove_solutions([self.number])

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
    def species(self):
        return self.pp.ip.get_species_moles(self.number)
    @property
    def species_moles(self):
        return self.pp.ip.get_species_moles(self.number)
    @property
    def species_molalities(self):
        return self.pp.ip.get_species_molalities(self.number)
    @property
    def species_activities(self):
        return self.pp.ip.get_species_activities(self.number)
    @property
    def masters_species(self):
        """ Returns a Phreeqc output like species table """
        return self.pp.ip.get_masters_species(self.number)
