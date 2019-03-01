""" Phreeqpython module """

import os
import gzip
from .viphreeqc import VIPhreeqc
from .solution import Solution
from .gas import Gas
import warnings

class PhreeqPython(object):
    """ PhreeqPython Class to interact with the VIPHREEQC module """

    def __init__(self, database=None, from_file=None, debug=False):
        # Create VIPhreeqc Instance
        self.ip = VIPhreeqc()
        self.ip.debug = debug
        # Load Vitens.dat database. The VIPhreeqc module is unable to handle relative paths
        if not database:
            database_path = os.path.dirname(__file__) + "/database/vitens.dat"
        else:
            database_path = os.path.dirname(__file__) + "/database/"+database

        if not os.path.isfile(database_path):
            raise FileNotFoundError("Database file not found")

        self.ip.load_database(database_path)


        if from_file:
            dump = gzip.open(from_file,"rb")
            try:
                inputstr = dump.read().decode('utf-8') + "END"
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
            self.buffer = False
            self.solution_counter = 0
            self.gas_counter = 0

    def add_gas(self, components=None, pressure=1.0, volume=1.0, fixed_pressure=True, fixed_volume=False, equilibrate_with=False):
        """ add a gas phase to the VIPhreeqc stack """

        if fixed_pressure and fixed_volume:
            raise ValueError("Cannot create a gas with a fixed pressure and a fixed volume!")

        if equilibrate_with is not False and not fixed_volume:
            raise ValueError("Only gas phases with a fixed_volume can be created in equilibrium with a solution")

        self.gas_counter += 1


        inputstr = "GAS_PHASE {}\n".format(self.gas_counter)
        if fixed_pressure:
            inputstr += "-fixed_pressure \n"
        if fixed_volume:
            inputstr += "-fixed_volume \n"

        inputstr += "-volume {}\n".format(volume)
        inputstr += "-pressure {}\n".format(pressure)

        for gas, pressure in components.items():
            inputstr += "{} {} \n".format(gas, pressure)

        if equilibrate_with:
            if isinstance(equilibrate_with, Solution):
                inputstr += "-equilibrate {}\n".format(equilibrate_with.number)
            else:
                inputstr += "-equilibrate {}\n".format(equilibrate_with)


        inputstr += "SAVE GAS_PHASE "+str(self.gas_counter) + "\n"
        inputstr += "END \n"

        self.ip.run_string(inputstr)

        return Gas(self, self.gas_counter)

    def add_solution_raw(self, composition=None):
        warnings.warn("add_solution_raw is deprecated, use add_solution and add_solution_simple instead", DeprecationWarning)
        return self.add_solution(composition)

    def add_solution(self, composition=None):
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

    def add_solution_simple(self, composition=None, temperature=25):
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

    def add_master_species(self, element, master_species, alkalinity=0, gfw=1, egfw=""):
        """ add a master species to the VIPhreeqc Instance """
        inputstr = "SOLUTION_MASTER_SPECIES; {} {} {} {} {} \n".format(element, master_species, alkalinity, gfw, egfw)
        self.buffer = inputstr

    def add_species(self, reaction, log_k=0, delta_h=0, egfw=None):
        """ add a solution species to the VIPhreeqc Instance """
        inputstr = self.buffer if self.buffer else ""
        self.buffer = False
        inputstr +=  "SOLUTION_SPECIES \n {} \n".format(reaction)
        inputstr += "log_k {}".format(log_k)

        self.ip.run_string(inputstr)

    def change_solution(self, solution_number, elements, create_new=False):
        """ change solution composition by adding/removing elements """

        inputstr = "USE SOLUTION "+str(solution_number)+"\n"
        inputstr += "REACTION 1 \n"
        for element, change in elements.items():
            inputstr += element + " " + str(change) + "\n"
        inputstr += "1 mol \n"
        if create_new:
            self.solution_counter += 1
            solution_number = self.solution_counter

        inputstr += "SAVE SOLUTION "+str(solution_number) + "\n"
        inputstr += "END"

        self.ip.run_string(inputstr)
        return Solution(self, solution_number)

    def equalize_solution(self, solution_number, phases, to_si, in_phase=[10], with_element=[None]):
        """ saturate or desaturate (equalize) a solution with one or more phases """

        if not isinstance(phases, list):
            phases = [phases]
        if not isinstance(to_si, list):
            to_si = [to_si]
        if not isinstance(in_phase, list):
            in_phase = [in_phase]
        if not isinstance(with_element, list):
            with_element = [with_element]

        else:
            # fix default inputs
            if len(to_si) < len(phases):
                to_si.extend([0 for i in range(len(phases)-len(to_si))])

            if len(in_phase) < len(phases):
                in_phase.extend([10 for i in range(len(phases)-len(in_phase))])

            if len(with_element) < len(phases):
                with_element.extend([None for i in range(len(phases)-len(with_element))])

        inputstr = "USE SOLUTION "+str(solution_number)+"\n"
        inputstr += "EQUILIBRIUM PHASES 1 \n"

        for num in range(len(phases)):

            if with_element[num]:
                inputstr += phases[num] + " " + str(to_si[num]) + " " + with_element[num] + " " + str(in_phase[num]) + "\n"
            else:
                inputstr += phases[num] + " " + str(to_si[num]) + " " + str(in_phase[num]) + "\n"

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
        # set of phreeqpython IDs
        pp_ids = set()
        for solution, fraction in solutions.items():
            if isinstance(solution, Solution):
                pp_ids.add(solution.pp.ip.id_)
                inputstr += str(solution.number) + " " + str(fraction) + "\n"
            else:
                inputstr += str(solution) + " " + str(fraction) + "\n"

        inputstr += "SAVE SOLUTION "+str(self.solution_counter) + "\n"
        inputstr += "END \n"

        if len(pp_ids) > 1:
            raise ValueError('Cannot Mix solutions belonging to seperate PhreeqPython instances!')

        self.ip.run_string(inputstr)

        return Solution(self, self.solution_counter)

    def interact_solution_gas(self, solution_number, gas_number):
        """ Interact solution with gas phase """
        inputstr = "USE SOLUTION " + str(solution_number) + "\n"
        inputstr += "USE GAS_PHASE " + str(gas_number) + "\n"
        inputstr += "SAVE GAS_PHASE " + str(gas_number) + "\n"
        inputstr += "SAVE SOLUTION " + str(solution_number) + "\n"
        inputstr += "END"
        self.ip.run_string(inputstr)


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

    def copy_gas(self, gas_number):
        """ Copy a solution to create a new one """
        # add a solution to the VIPhreeqc Stack
        self.gas_counter += 1
        # mix two or more solutions to obtain a new solution
        inputstr = "COPY GAS_PHASE " + str(gas_number) + " " + str(self.gas_counter) + "\n"
        inputstr += "END\n"

        self.ip.run_string(inputstr)

        return Gas(self, self.gas_counter)

    def empty_solution(self):
        return self.add_solution({})

    def remove_solutions(self, solution_number_list):
        """ Remove solutions from VIPhreeqc memory """
        inputstr = "DELETE \n"
        inputstr += "-solution " + ' '.join(map(str, solution_number_list))
        self.ip.run_string(inputstr)

    def remove_gases(self, gas_number_list):
        """ Remove solutions from VIPhreeqc memory """
        inputstr = "DELETE \n"
        inputstr += "-gas_phase " + ' '.join(map(str, gas_number_list))
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

    def get_solution_list(self):
        return self.ip.get_solution_list()

