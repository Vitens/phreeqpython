import re
import copy
import numbers
from .utility import convert_units
from .equilibriumphase import EquilibriumPhase
from .gas import Gas 

import numpy as np

class Solution(object):
    """An aqueous solution.
    
    A solution of zero or more chemical species in water.
    Defined by general solution properties like temperature, density, pH, ...
    and its composition of elements.
    
    An element is an atomic element, optionally further specified by a valence state: Na, Fe, Fe(3), S(-2), ...
    A species consists of one or more elements and can be ionic (Na+, HCO3-, Ca+2), molecular (H2CO3, CO2, O2) or atomic (Na, C, ...).
    
    For details, see [PhreeQC/Solution](https://water.usgs.gov/water-resources/software/PHREEQC/documentation/phreeqc3-html/phreeqc3-48.htm#50593793_30253).    
    """

    def __init__(self, phreeqpython, number, extraneous=None):
        self.pp = phreeqpython
        self.factor = 1
        self.number = number
        self.extraneous = {} if extraneous is None else extraneous

    def copy(self):
        """Returns an independent copy of the solution.
        
        Examples:
            >>> sol2 = sol.copy()        
        """        
        copied_solution = self.pp.copy_solution(self.number)
        copied_solution.extraneous = copy.deepcopy(self.extraneous)
        return copied_solution

    def change(self, composition, units='mmol'):
        """Change the solution by adding or removing species.
        
        Args:
            composition (dict): A dictionary of (species, amount) pairs.
            units (str): Optional, unit of the amounts.
            
        Returns:
            Solution: The altered solution.
            
        Examples:
            >>> sol.change({'K': 20.0, 'Na': -10.0})
            >>> sol.change({'CaSO4': 5.0}, units='mg')
            >>> sol.change({'NaCl': -10.0, 'Fe+2': -5.0})
        """
        converted_composition = {}
        for element, amount in composition.items():
            amount = convert_units(element, amount, units, 'mol')
            converted_composition[element] = amount
        self.pp.change_solution(self.number, converted_composition)
        return self

    def add(self, element, amount, units='mmol'):
        """Add a species to the solution.
        
        Args:
            element (str): An element or species.
            amount (float): Amount of the species added.
            units (str): Optional, unit of the amount.
            
        Returns:
            Solution: The altered solution.
        
        Examples:
            >>> sol.add('Fe', 5.0)
            >>> sol.add('CaCO3', 10.0, 'mg')
        """
        amount = convert_units(element, amount, units, 'mol')
        self.pp.change_solution(self.number, {element:amount})
        return self

    def remove(self, element, amount, units='mmol'):
        """Remove a species from the solution.
                
        Args:
            element (str): An element or species.
            amount (float): Amount of the species removed.
            units (str): Optional, unit of the amount.
            
        Returns:
            Solution: The altered solution.
        
        Examples:
            >>> sol.remove('Fe', 5.0)
            >>> sol.remove('CaCO3', 10.0, 'mg')
        """
        amount = -convert_units(element, amount, units, 'mol')
        self.pp.change_solution(self.number, {element:amount})
        return self

    def remove_fraction(self, species, fraction):
        """Remove a fraction of the species from the solution.
                
        Args:
            species (str): An element or species.
            fraction (float): Fraction of amount to remove.
            
        Returns:
            Solution: The altered solution.
        
        Examples:
            >>> sol.remove('K', 0.3)
            >>> sol.remove('H2O', 0.9)
        """
        current = self.total(species)
        to_remove = current * fraction
        self.remove(species, to_remove)
        return self

    def interact(self, gas_or_phase):
        """Equilibrate the solution with a multicomponent gas or solid phase.
        
        Args:
            gas_or_phase (Gas | Equilibriumphase): Previously defined multicomponent gas or solid phase.
        
        Returns:
            Solution: The solution after equilibrium with the gas or solid phase.
            
        Examples:
            >>> air = pp.add_gas({'O2(g)': 0.2, 'N2(g)': 0.78, 'CO2(g)': 0.000420})
            >>> sol.interact(air)
        """
        if isinstance(gas_or_phase, Gas):
            self.pp.interact_solution_gas(self.number, gas_or_phase.number)
        else:
            self.pp.interact_solution_phase(self.number, gas_or_phase.number)
        return self

    def equalize(self, phases, to_si=[0], in_phase=[10], with_chemical=[None]):
        """Equalize the solution with one or more pure phases.
        
        Args:
            phases (list): List of one or more pure gas or solid phases.
            to_si (list): Optional, list of target saturation indices for each phase.
            in_phase (list): Optional, list of maximum amounts available for each phase, in moles.
            with_chemical (list): Optional, list of alternative chemical added for each phase to reach the specified saturation index.
            
        Returns:
            Solution: The solution after equilibration.
            
        Notes:
            to_si: The saturation index (SI) for solid phases is SI = log10(IAP / Ksp).
                The SI for gases is SI = log10(p_gas), with p_gas the partial pressure.
            
        Examples:
            >>> sol.equalize(phases=['Calcite'])
            >>> sol.equalize(phases=['CO2(g)', 'CH4(g)'], to_si=[-0.4, -0.2])
            >>> sol.equalize(phases=['Calcite'], with_chemical='HCl')
        """
        self.pp.equalize_solution(self.number, phases, to_si, in_phase, with_chemical)
        return self

    def saturate(self, phase, to_si=0, in_phase=10):
        """Saturate the solution with a pure phase.
        
        Args:
            phase (str): A pure gas or solid phase.
            to_si (float): Optional, target saturation index for the phase.
            in_phase (float): Optional, maximum amount available of the phase.
        
        Returns:
            Solution: The solution after equilibration.
            
        Examples:
            >>> sol.saturate('Calcite')
            >>> sol.saturate('CO2(g)', to_si=-3.5) 
        """
        if(self.si(phase) < 0):
            self.pp.equalize_solution(self.number, phase, to_si, in_phase)
        return self

    # this function can only precipitate
    def desaturate(self, phase, to_si=0):
        """Desaturate a solution from a pure phase via precipitation or vaporization.
        
        Args:
            phase (str): A pure gas or solid phase.
            to_si (float): Optional, target saturation index for the phase.
            
        Returns:
            Solution: The solution after equilibration.
        
        Examples:
            >>> sol.desaturate('Gypsum')
            >>> sol.desaturate('CO2(g)', to_si=-3.5) 
        """
        self.pp.equalize_solution(self.number, phase, to_si, 0)
        return self

    def change_ph(self, to_pH, with_chemical=None):
        """Change the pH of the solution.
        
        Args:
            to_pH (float): target pH.
            with_chemical (str): Optional, acid of base to add, default is 'HCl' or 'NaOH'.
        
        Returns:
            Solution: The altered solution.
        
        Examples:
            >>> sol.change_ph(4.5)
            >>> sol.change_ph(4.5, 'H2SO4')
        """
        if not with_chemical:
            if to_pH < self.pH:
                self.pp.equalize_solution(self.number, "Fix_pH", -to_pH, 10, "HCl")
            else:
                self.pp.equalize_solution(self.number, "Fix_pH", -to_pH, 10, "NaOH")
        else:
            self.pp.equalize_solution(self.number, "Fix_pH", -to_pH, 10, with_chemical)
        return self

    def change_temperature(self, to_temperature):
        """Change the temperature of the solution.
        
        Args:
            to_temperature (float): Target temperature.
            
        Returns:
            Solution: The altered solution.        
        """
        self.pp.change_solution_temperature(self.number, to_temperature)
        return self

    def total(self, element, units='mmol'):
        """Returns the amount of an element or species in the solution.
        
        Args:
            element (str): Element or species.
            units (str): Optional, unit of the amount.
        
        Examples:
            >>> sol.total('Na')
            >>> sol.total('CO2')
            >>> sol.total('HCO3', 'mg')        
        """
        amount = self.pp.ip.get_total_ion(self.number, element)
        return convert_units(element, amount, to_units=units)

    def total_activity(self, element, units='mmol'):
        """Returns the activity of an element or species in the solution.
        
        Args:
            element (str): Element or species.
            units (str): Optional, unit of the activity.
        
        Notes:
            Slow function !
            
        Examples:
            >>> sol.activity('Ca')        
        """
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
    
    def chain(self):
        self.pp.start_chain(self.number)
    
    def end(self):
        self.pp.end()
        

    def kinetics(self, element, rate_function, time, m0=0, args=(), units='mmol'):
        try:
            from scipy.integrate import odeint
        except ImportError as exc:
            raise ImportError(
                "kinetics requires scipy. Install with "
                "'pip install phreeqpython[kinetics]' or install scipy manually."
            ) from exc

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
            self.add(element, y[i], units)
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
    def volume(self):
        return self.pp.ip.get_volume(self.number)
    @property
    def density(self):
        return self.pp.ip.get_density(self.number)
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
        return f"<PhreeqPython.{self.__class__.__name__} number {self.number}>"
