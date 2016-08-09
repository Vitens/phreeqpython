""" Phreeqpy module """

import re
import os
from viphreeqc import VIPhreeqc

class PhreeqPy(object):
    """ PhreeqPy Class to interact with the VIPHREEQC module """

    def __init__(self):
        # Create VIPhreeqc Instance
        self.ip = VIPhreeqc()
        # Load Vitens.dat database. The VIPhreeqc module is unable to handle relative paths
        database_path = os.path.dirname(__file__) + "/database/vitens.dat"
        self.ip.load_database(database_path)
        self.solution_counter = 0

    def add_solution(self, composition=None, temperature=25):
        """ add a solution to the VIPhreeqc Stack """
        self.solution_counter += 1

        inputstr = "SOLUTION "+str(self.solution_counter) + "\n"
        inputstr += "-temp "+str(temperature) + "\n"
        if len(composition) > 0:
            inputstr += "REACTION 1 \n"
            for species, moles in composition.iteritems():
                inputstr += species + " " + str(moles) + "\n"
            inputstr += "1 mmol \n"

        inputstr += "SAVE SOLUTION "+str(self.solution_counter) + "\n"
        inputstr += "END \n"

        self.ip.run_string(inputstr)

        return Solution(self, self.solution_counter)

    def change_solution(self, solution_number, elements, create_new=False):
        """ change solution composition by adding/removing elements """

        inputstr = "USE SOLUTION "+str(solution_number)+"\n"
        inputstr += "REACTION 1 \n"
        for element, change in elements.iteritems():
            inputstr += element + " " + str(change) + "\n"
        inputstr += "1 mmol \n"
        if create_new:
            self.solution_counter += 1
            solution_number = self.solution_counter

        inputstr += "SAVE SOLUTION "+str(solution_number) + "\n"
        inputstr += "END"

        self.ip.run_string(inputstr)
        return Solution(self, solution_number)

    def equalize_solution(self, solution_number, phase, to_si, in_phase=10, with_element=None):
        """ saturate or desaturate a solution """
        inputstr = "USE SOLUTION "+str(solution_number)+"\n"
        inputstr += "EQUILIBRIUM PHASES 1 \n"
        if with_element:
            inputstr += phase + " " + str(to_si) + " " + with_element + " " + str(in_phase) + "\n"
        else:
            inputstr += phase + " " + str(to_si) + " " + str(in_phase) + "\n"

        inputstr += "SAVE SOLUTION "+str(solution_number) + "\n"
        inputstr += "END"

        self.ip.run_string(inputstr)
        return Solution(self, solution_number)

    def mix_solutions(self, solutions):
        """ Create a mixture from two other solutions """
        # add a solution to the VIPhreeqc Stack
        self.solution_counter += 1
        # mix two or more solutions to obtain a new solution
        inputstr = "MIX 1 \n"
        for solution, fraction in solutions.iteritems():
            if isinstance(solution, Solution):
                inputstr += str(solution.number) + " " + str(fraction) + "\n"
            else:
                inputstr += str(solution) + " " + str(fraction) + "\n"

        inputstr += "SAVE SOLUTION "+str(self.solution_counter) + "\n"
        inputstr += "END \n"

        self.ip.run_string(inputstr)

        return Solution(self, self.solution_counter)

    def copy_solution(self, solution_number):
        """ Copy a solution to create a new one """
        # add a solution to the VIPhreeqc Stack
        self.solution_counter += 1
        # mix two or more solutions to obtain a new solution
        inputstr = "COPY SOLUTION " + str(solution_number) + " " + str(self.solution_counter) + "\n"
        inputstr += "END\n"

        self.ip.run_string(inputstr)

        return Solution(self, self.solution_counter)

class Solution(object):
    """ PhreeqPy Solution Class """

    def __init__(self, phreeqpy, number):
        self.pp = phreeqpy
        self.number = number

    def copy(self):
        """ Create a new copy, with unique solution number, from this solution """
        return self.pp.copy_solution(self.number)

    def add(self, element, mmol):
        self.pp.change_solution(self.number, {element:mmol})
    def remove(self, element, mmol):
        mmol = -mmol
        self.pp.change_solution(self.number, {element:mmol})
    def remove_fraction(self, species, fraction):
        current = self.pp.ip.get_moles(self.number, species)
        to_remove = 1000 * current * fraction
        self.remove(species, to_remove)

    # this function can precipitate and dissolve!
    def saturate(self, phase, to_si=0, partial_pressure = 10):
        self.pp.equalize_solution(self.number, phase, to_si, partial_pressure)

    # this function can only precipitate
    def desaturate(self, phase, to_si=0):
        self.pp.equalize_solution(self.number, phase, to_si, 0)

    # change the ph
    def change_ph(self, to_pH, with_chemical=None):
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

    # Accessor methods
    @property
    def pH(self):
        return self.pp.ip.get_ph(self.number)
    @property
    def sc(self):
        return self.pp.ip.get_sc(self.number)
    @property
    def temperature(self):
        return self.pp.ip.get_temperature(self.number)
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
        return self.pp.ip.get_species_molalities(self.number)

    def total(self, element):
        """ Returns to total of any given species or element (SLOW!) """
        total = 0
        regexp = "(^|[^A-Z])"+element
        for species, amount in self.species.iteritems():
            if re.search(regexp, species):
                total += amount
        return total

    def total_element(self, element):
        """ Returns to total any given element (FAST!) """
        return self.pp.ip.get_total_element(self.number, element)

    def si(self, phase):
        return self.pp.ip.get_si(self.number, phase)
