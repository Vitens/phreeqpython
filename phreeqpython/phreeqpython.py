""" Phreeqpython module """

import re
import os
from viphreeqc import VIPhreeqc

class PhreeqPython(object):
    """ PhreeqPython Class to interact with the VIPHREEQC module """

    def __init__(self, database=None):
        # Create VIPhreeqc Instance
        self.ip = VIPhreeqc()
        # Load Vitens.dat database. The VIPhreeqc module is unable to handle relative paths
        if not database:
            database_path = os.path.dirname(__file__) + "/database/vitens.dat"
        else:
            database_path = database

        self.ip.load_database(database_path)
        # set solution counter to 0
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

    def change_solution_temperature(self, solution_number, temperature):
        """ change temperature """
        inputstr = "USE SOLUTION " + str(solution_number) + "\n"
        inputstr += "REACTION_TEMPERATURE 1 \n"
        inputstr += str(temperature) + "\n"
        inputstr += "SAVE SOLUTION "+str(self.solution_counter) + "\n"

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

    def remove_solutions(self, solution_number_list):
        """ Remove solutions from VIPhreeqc memory """
        inputstr = "DELETE \n"
        inputstr += "-solution " + ' '.join(map(str, solution_number_list))
        self.ip.run_string(inputstr)
