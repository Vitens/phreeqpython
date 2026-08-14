import re
import copy
import numbers
from .utility import convert_units
from .equilibriumphase import EquilibriumPhase
from .gas import Gas 

import numpy as np

class Solution(object):
    """An aqueous solution.
    
    See phreeqpython.add_solution() for details on creating a solution.    
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
            to_si: for solid phases, SI = log10(IAP / Ksp),
                for gases, SI = log10(p_gas), with p_gas the partial pressure.
            
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
        """Returns the amount of a species in the solution.
        
        Args:
            element (str): Chemical species.
            units (str): Optional, unit of the amount.
        
        Returns:
            float: Amount of the species (mmol).
        
        Examples:
            >>> sol.total('Na+')
            >>> sol.total('CO2')
            >>> sol.total('HCO3-', 'mg')        
        """
        amount = self.pp.ip.get_total_ion(self.number, element)
        return convert_units(element, amount, to_units=units)

    def total_element(self, element, units='mmol'):
        """Returns the total amount of an element in the solution.
                
        Args:
            element (str): Element (atomic species).
            units (str): Optional, unit of the amount.
            
        Returns:
            float: Total amount of the element (mmol).
        
        Examples:
            >>> sol.total_element('C')
            >>> sol.total_element('S', 'mg')        
        """
        return convert_units(element, self.pp.ip.get_total_element(self.number, element), 'mol', units)
    
    def activity(self, species, units='mmol'):
        """Returns the activity of a species in the solution.
        
        Args:
            element (str): Chemical species.
            units (str): Optional, unit of the activity.
        
        Returns:
            float: Activity of the species (mmol/kgw).
            
        CHECK:
        this returns a concentration (/kgw), not a total amount.
        Confusing with the units shown.
        
        Examples:
            >>> sol.activity('Ca+2')
            >>> sol.activity('NaSO4-', 'mg')        
        """
        return convert_units(species, self.pp.ip.get_activity(self.number, species), 'mol', units)
    
    def total_activity(self, element, units='mmol'):
        """Returns the total of the activities of all species of the element in the solution.
        
        Args:
            element (str): Element (atomic species).
            units (str): Optional, unit of the activity.
            
        Returns:
            float: Total activity of the element (mmol/kgw).
        
        Notes:
            Slow function !
            
        Examples:
            >>> sol.activity('Ca')
            >>> sol.activity('C', 'mg')        
        """
        total = 0
        regexp = "(^|[^A-Z])"+element
        for species, amount in self.species_activities.items():
            if re.search(regexp, species):
                total += convert_units(element, amount, to_units=units)
        return total

    def moles(self, species, units='mmol'):
        """Returns the amount of a species in the solution.
        
        CHECK: confusing, says moles, but can also return in 'mg'.
        Also, seems to always return the same value as sol.total().
        Better to remove this method?
        
        Args:
            element (str): Chemical species.
            units (str): Optional, unit of the amount.
        
        Examples:
            >>> sol.moles('Na+')
            >>> sol.moles('HCO3-', 'mg')        
        """
        return convert_units(species, self.pp.ip.get_moles(self.number, species), 'mol', units)

    def molality(self, species, units='mmol'):
        """Returns the molality of a species in the solution.
        
        CHECK: confusing, units given in 'mmol'... , but returns 'mmol/kgw'?
        Checked with {'-water': 2.0, ...} as solution: sol.total() and sol.moles() return 'mmol', 
        but sol.molality() returns ~half the value, so takes count of the total mass.
        Should we show different units?
        
        Args:
            element (str): Chemical species.
            units (str): Optional, unit of the amount.
        
        Returns:
            float: Molality of the species (mmol/kgw).
        
        Examples:
            >>> sol.molality('Na+')
            >>> sol.molality('HCO3-', 'mg')        
        """
        return convert_units(species, self.pp.ip.get_molality(self.number, species), 'mol', units)

    def si(self, phase):
        """Returns the saturation index (SI) of a phase in the solution.
        
        Args:
            phase (str): Gas or solid phase.
        
        Returns:
            float: The SI of the phase (-).
            
        Notes:
            For solid phases, SI = log10(IAP / Ksp), with IAP the ion activity product and Ksp the solubility product constant.
            For gases, SI = log10(p_gas), with p_gas the partial pressure.
        
        Examples:
            >>> sol.si('Calcite')
            >>> sol.si('CO2(g)')
        """
        return self.pp.ip.get_si(self.number, phase)

    def sr(self, phase):
        """Returns the saturation ratio (SR) of a phase in the solution.
        
        Args:
            phase (str): Gas or solid phase.
        
        Returns:
            float: The SR of the phase (-).
            
        Notes:
            For solid phases, SR = IAP / Ksp, with IAP the ion activity product and Ksp the solubility product constant.
            For gases, SR = p_gas, with p_gas the partial pressure.
        
        Examples:
            >>> sol.sr('Calcite')
            >>> sol.sr('CO2(g)')
        """
        return 10**self.pp.ip.get_si(self.number, phase)

    def forget(self):
        """Remove this solution from the PhreeQC simulation.
        
        See also phreeqpython.add_solution() to add solutions to a PhreeQC simulation.        
        """
        self.pp.remove_solutions([self.number])
    
    def chain(self):
        """
        CHECK: this calls the PhreeQC 'USE SOLUTION' keyword, but not clear
        when you would need to use this, not intuitive.
        What are the use cases?
        
        """
        self.pp.start_chain(self.number)
    
    def end(self):
        """
        CHECK: calls the keyword 'END' on the PhreeQC simulation?
        Not better to only define that at the simulation side (pp)?
        Its use for a solution is not clear.
        """
        self.pp.end()
        

    def kinetics(self, element, rate_function, time, m0=0, args=(), units='mmol'):
        """CHECK:
            the kinetics examples show different ways of setting up kinetics (with and without this function).
            Still experimental?
            
            PhreeQC has the kinetics keyword, but would require to parse the rate function(s) into BASIC, hard...
            but PhreeQC allows kinetics over the whole simulation (e.g. solution, gas, other phases)
            Not better to move kinetics functionality to the simulation level (phreeqpython = pp)?
        
        """
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
        """Add two solutions.
       
        CHECK: 
        Remark for creating these:
            >>> sol3 = sol1*0.2 + sol2*0.8
            >>> sol3 = sol1*0.2
            >>> sol3 = sol1/4.0
            
        currently, sol.factor is used to track the coefficient in making these mixtures.
        
        But doing this:
        sol3 = sol1*2
        does not increase sol3.mass, it only sets sol3.factor, which is not what the user wants.
        
        Also:
        sol3 = sol1*1 + sol1*2
        gives: sol3.mass = 2, not 3, because the second term sets sol1.factor = 2, and then the addition is evaluated
        
        Wouldn't it be easier and more intuitive to do as follows?:
        sol1*2 calls:
        def __mul__(self, factor):
            mixture = self.pp.mix_solutions({self: factor})
            return mixture
        
        No need anymore to track the factors, and the resulting solutions always reflect the proper amount.
        sol3 = sol1*0.2 + sol2*0.8
        will then call mix_solutions 3 times, small price to pay?            
        """
        if not isinstance(other, Solution):
            raise TypeError("Invalid operation, only addition of two solutions is allowed")
        mixture = self.pp.mix_solutions({self:self.factor, other:other.factor})
        self.factor = 1
        other.factor = 1
        return mixture

    def __truediv__(self, other):
        """ Python 3 support """
        return self.__div__(other)

    def __div__(self, other):
        """Set devision factor."""
        if not isinstance(other, numbers.Real):
            raise TypeError("Invalid operation, only division by a number is allowed")
        self.factor = 1/float(other)
        return self

    def __mul__(self, other):
        """Set multiplication factor."""
        if not isinstance(other,numbers.Real):
            raise TypeError("Invalid operation, only division by a number is allowed")
        self.factor = float(other)
        return self

    # Accessor methods
    @property
    def I(self):
        """float: The ionic strength of the solution, (mol/L)."""
        return self.pp.ip.get_mu(self.number)
    
    @property
    def mu(self):
        """float: The ionic strength of the solution (mol/L)."""
        return self.I
    
    @property
    def pH(self):
        """float: The pH of the solution (-)."""
        return self.pp.ip.get_ph(self.number)
    
    @property
    def sc(self):
        """float: The specific conductance of the solution (µS/cm)."""
        return self.pp.ip.get_sc(self.number)
    
    @property
    def temperature(self):
        """float: The temperature of the solution (°C)."""
        return self.pp.ip.get_temperature(self.number)
    
    @property
    def mass(self):
        """float: The mass of water in the solution (kg).
        
        CHECK:
        not very intuitive, one would expect this to return the solution mass, not the water part.
        I did a few checks with high salt concentrations:
        sol.volume * sol.density always accurately returns the solution mass.
        
        Proposal:
        sol.mass = sol.volume * sol.density
        sol.mass_water = the water mass      
        """
        return self.pp.ip.get_mass(self.number)
    
    @property
    def volume(self):
        """float: The volume of the solution (L)."""
        return self.pp.ip.get_volume(self.number)
    
    @property
    def density(self):
        """float: The density of the solution (kg/L)."""
        return self.pp.ip.get_density(self.number)
    
    @property
    def pe(self):
        """float: The electron activity of the solution (-).
        
        Notes:
            pe = -log({e-}), with {e-} the electron activity.
            pe < 0: high electron activity, reducing environment.
            pe > 0: low electron activity, oxidizing environment.        
        """
        return self.pp.ip.get_pe(self.number)
    
    @property
    def phases(self):
        """dict: All phases in the solution and their saturation index (-).
        
        Example:
            >>> sol.phases
            {   'Calcite': 0.155,
                'CO2(g)': -0.341,
                ...
            }
        
        Notes: 
            saturation index: SI = log10(AIP / Ksp)
        """
        return self.pp.ip.get_phases_si(self.number)
    
    @property
    def elements(self):
        """dict: All elements in the solution and their amount (mol).
        
        Example:
            >>> sol.elements
            {   'C(4)': 0.50,
                'Ca': 0.20,
                ... 
            }
        """
        return self.pp.ip.get_elements_totals(self.number)
    
    @property
    def species(self, units='mmol'):
        """dict: All species in the solution and their amount (mol).
        
        Example:
            >>> sol.species
            {   'Ca+2': 0.0036,
                'CO3-2': 2.18e-05,
                ...
            }
        
        CHECK:
        units not used, and probably not accessible via a property?
        amount is in mol, not mol/L or mol/kgw, can be confusing when sol.mass <> 1.0 kg,
        better return a concentration (mol/kgw or mol/kgs)?
        """
        return self.pp.ip.get_species_moles(self.number)
    
    @property
    def species_moles(self, units='mmol'):
        """dict: All species in the solution and their amount (mol).
        
        CHECK:
        calls same function, no difference with property above?
        better drop this one?
        
        """
        return self.pp.ip.get_species_moles(self.number)
    
    @property
    def species_molalities(self, units='mmol'):
        """dict: All species in the solution and their concentration (mol/kgw).
        
        CHECK:
        units not used.
        this property returns a concentration (mol/kgw), while sol.species returns 
        absolute amount (mol). Not very intuitive.
        Maybe we could define the default units on the simulation level (phreeqpython = pp)?
        And have an accessible function to convert if needed (pp.units(...))?
        
        Example:
            >>> sol.species_molalities
            {   'Ca+2': 0.045,
                'CO3-2': 3.18e-05,
                ...
            }

        """
        return self.pp.ip.get_species_molalities(self.number)
    
    @property
    def species_activities(self, units='mmol'):
        """dict: All species in the solution and their activities (mol/kgw).
        
        Example:
            >>> sol.species_activities
            {   'Ca+2': 0.045,
                'CO3-2': 3.18e-05,
                ...
            }        
        """
        return self.pp.ip.get_species_activities(self.number)
    
    @property
    def masters_species(self):
        """dict: All master species in the solution and their species.
        
        CHECK:
        shouldn't this be: master_species ?

        Example:
            >>> sol.masters_species        
            {   'C(4)': ['CO2', 'CO3-2', 'CaCO3', 'HCO3-'],
                'Ca': ['Ca+2', 'CaCO3', 'CaHCO3+', 'CaOH+'],
                'Cl': ['Cl-'],
                ...
            }
        """
        return self.pp.ip.get_masters_species(self.number)

    # pretty printing
    def __str__(self):
        return f"<PhreeqPython.{self.__class__.__name__} number {self.number}>"
