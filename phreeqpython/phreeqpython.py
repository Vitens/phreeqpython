""" Phreeqpython module """

import os
import gzip
from .viphreeqc import VIPhreeqc
from .solution import Solution

class PhreeqPython(object):
    """ PhreeqPython Class to interact with the VIPHREEQC module """

    def __init__(self, from_file=None, database=None):
        # Create VIPhreeqc Instance
        self.ip = VIPhreeqc()
        # Load Vitens.dat database. The VIPhreeqc module is unable to handle relative paths
        if not database:
            database_path = os.path.dirname(__file__) + "/database/vitens.dat"
        else:
            database_path = database


        self.ip.load_database(database_path)

        if from_file:
            dump = gzip.open(from_file,"rb")
            try:
                inputstr = dump.read().decode('utf-8')  + "END"
                self.ip.run_string(inputstr)

                solutions = self.ip.get_solution_list()
                # force IPHREEQC to calculate all the solution properties
                for solution_number in solutions:
                    self.change_solution(solution_number,{'Na':0})

                self.solution_counter = solutions[-1]
                # precalculte all solutions
            finally:
                dump.close()
            

        else:
            # set solution counter to 0
            self.solution_counter = 0

    def add_solution_raw(self, composition=None):
        """ add a solution to the VIPhreeqc Stack, allowing more control over the
        created solution """

        self.solution_counter += 1
        inputstr = "SOLUTION "+str(self.solution_counter) + "\n"
        if len(composition) > 0:
            for key, value in composition.items():
                inputstr += "  "+key+" "+str(value) + "\n"

        inputstr += "SAVE SOLUTION "+str(self.solution_counter) + "\n"
        inputstr += "END \n"

        self.ip.run_string(inputstr)

        return Solution(self, self.solution_counter)

    def add_solution(self, composition=None, temperature=25):
        """ add a solution to the VIPhreeqc Stack and add all individual components 
        in a reaction step 
        """
        self.solution_counter += 1

        inputstr = "SOLUTION "+str(self.solution_counter) + "\n"
        inputstr += "-temp "+str(temperature) + "\n"
        if len(composition) > 0:
            inputstr += "REACTION 1 \n"
            for species, moles in composition.items():
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
        for element, change in elements.items():
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
        for solution, fraction in solutions.items():
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
        inputstr += "SAVE SOLUTION "+str(solution_number) + "\n"

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

    def get_solution(self, number):
        return Solution(self, number)

    def dump_solutions(self, solution_number_list = None, filename='dump.gz'):
        """ Dump solutions to raw file for transmission to another VIPhreeqc instance """
        if not solution_number_list:
            solution_number_list = []

        inputstr = "DUMP \n"
        inputstr += "-file "+filename + "\n"
        inputstr += "-solution " + ' '.join(map(str, solution_number_list)) + "\n"
        inputstr += "END"

        self.ip.set_dump_string_on()
        self.ip.run_string(inputstr)

        dump = self.ip.get_dump_string()

        # write to file
        dumpfile = gzip.open(filename,'w')
        dumpfile.write(dump)
        dumpfile.close()

        self.ip.set_dump_string_off()

