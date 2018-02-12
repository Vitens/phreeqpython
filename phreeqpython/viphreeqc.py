# -*- coding: utf-8 -*-*

"""Access PHREEQC-DLL via ctypes.

This is exchangeable with the COM interface.
"""

import ctypes
import os
import sys

if sys.version_info[0] == 2:
    #pylint: disable-msg=W0622
    def bytes(str_, encoding): #pylint: disable-msg=W0613
        """Compatibilty function for Python 3.
        """
        return str_
    range = xrange #pylint: disable-msg=C0103
    #pylint: enable-msg=W0622


class VIPhreeqc(object):
    """Wrapper for the VIPhreeqc DLL.
    """
    # All methods in `method_mapping` are added dynamically.
    # Therefore, pylint complains.
    #pylint: disable-msg=E1101
    def __init__(self, dll_path=None):
        """Connect to DLL and create IPhreeqc.

        The optional `dll_path` takes a path to the IPhreeqc shared library.
        If not provided it tries to select an appropriate library.
        Make sure you have the right library for your operating system.
        You may download one from here:
        ftp://brrftp.cr.usgs.gov/pub/charlton/iphreeqc/

        See the PhreeqPy documentation for help on compiling a IPhreeqc shared
        library.
        """
        if not dll_path:
            if sys.platform == 'win32':
                dll_name = './lib/VIPhreeqc.dll'
            elif 'linux' in sys.platform:
                dll_name = './lib/viphreeqc.so'
            elif sys.platform == 'darwin':
                dll_name = './lib/viphreeqc.dylib'
            else:
                msg = 'Platform %s is not supported.' % sys.platform
                raise NotImplementedError(msg)
            dll_path = os.path.join(os.path.dirname(__file__), dll_name)
        phreeqc = ctypes.cdll.LoadLibrary(dll_path)
        self.debug = False
        self.dll = phreeqc
        c_int = ctypes.c_int
        method_mapping = [('_accumulate_line', phreeqc.AccumulateLine,
                           [c_int, ctypes.c_char_p], c_int),
                          ('_add_error', phreeqc.AddError,
                           [c_int, ctypes.c_char_p], c_int),
                          ('_add_error', phreeqc.AddWarning,
                           [c_int, ctypes.c_char_p], c_int),
                          ('_clear_accumlated_lines',
                           phreeqc.ClearAccumulatedLines, [c_int], c_int),
                          ('_create_iphreeqc', phreeqc.CreateIPhreeqc,
                           [ctypes.c_void_p], c_int),
                          ('_destroy_iphreeqc', phreeqc.DestroyIPhreeqc,
                           [c_int], c_int),
                          ('_get_component', phreeqc.GetComponent,
                           [c_int, c_int], ctypes.c_char_p),
                          ('_get_component_count', phreeqc.GetComponentCount,
                           [c_int], c_int),
                          ('_get_dump_string', phreeqc.GetDumpString,
                           [c_int], ctypes.c_char_p),
                          ('_set_dump_string_on', phreeqc.SetDumpStringOn,
                           [c_int], c_int),
                          ('_get_error_string', phreeqc.GetErrorString,
                           [c_int], ctypes.c_char_p),
                          ('_get_selected_output_column_count',
                           phreeqc.GetSelectedOutputColumnCount, [c_int],
                           c_int),
                          ('_get_selected_output_row_count',
                           phreeqc.GetSelectedOutputRowCount, [c_int], c_int),
                          ('_get_value', phreeqc.GetSelectedOutputValue,
                           [c_int, c_int, c_int, ctypes.POINTER(VAR)], c_int),
                          ('_load_database', phreeqc.LoadDatabase,
                           [c_int, ctypes.c_char_p], c_int),
                          ('_load_database_string', phreeqc.LoadDatabaseString,
                           [c_int, ctypes.c_char_p], c_int),
                          ('_run_string', phreeqc.RunString,
                           [c_int, ctypes.c_char_p], c_int),
                          ('_set_selected_output_file_on',
                           phreeqc.SetSelectedOutputFileOn, [c_int, c_int],
                           c_int),
                          # VIPHREEQC Additions:
                          # gas
                          ('_get_gas_volume', phreeqc.GetGasVolume,
                           [c_int, c_int], ctypes.c_double),
                          ('_get_gas_pressure', phreeqc.GetGasPressure,
                           [c_int, c_int], ctypes.c_double),
                          ('_get_gas_total_moles', phreeqc.GetGasTotalMoles,
                           [c_int, c_int], ctypes.c_double),
                          ('_get_gas_components', phreeqc.GetGasComponents,
                           [c_int, c_int], ctypes.c_char_p),
                          ('_get_gas_component_moles', phreeqc.GetGasComponentMoles,
                           [c_int, c_int, ctypes.c_char_p], ctypes.c_double),
                          # solution
                          ('_get_ph', phreeqc.GetPH,
                           [c_int, c_int], ctypes.c_double),
                          ('_get_pe', phreeqc.GetPe,
                           [c_int, c_int], ctypes.c_double),
                          ('_get_sc', phreeqc.GetSC,
                           [c_int, c_int], ctypes.c_double),
                          ('_get_mu', phreeqc.GetMu,
                           [c_int, c_int], ctypes.c_double),
                          ('_get_temperature', phreeqc.GetTemperature,
                           [c_int, c_int], ctypes.c_double),
                          ('_get_mass', phreeqc.GetMass,
                           [c_int, c_int], ctypes.c_double),
                          ('_get_total', phreeqc.GetTotal,
                           [c_int, c_int, ctypes.c_char_p], ctypes.c_double),
                          ('_get_total_element', phreeqc.GetTotalElement,
                           [c_int, c_int, ctypes.c_char_p], ctypes.c_double),
                          ('_get_moles', phreeqc.GetMoles,
                           [c_int, c_int, ctypes.c_char_p], ctypes.c_double),
                          ('_get_activity', phreeqc.GetActivity,
                           [c_int, c_int, ctypes.c_char_p], ctypes.c_double),
                          ('_get_molality', phreeqc.GetMolality,
                           [c_int, c_int, ctypes.c_char_p], ctypes.c_double),
                          ('_get_species', phreeqc.GetSpecies,
                           [c_int, c_int], ctypes.c_char_p),
                          ('_get_species_masters', phreeqc.GetSpeciesMasters,
                           [c_int, c_int], ctypes.c_char_p),
                          ('_get_phases', phreeqc.GetPhases,
                           [c_int, c_int], ctypes.c_char_p),
                          ('_get_elements', phreeqc.GetElements,
                           [c_int, c_int], ctypes.c_char_p),
                          ('_get_si', phreeqc.GetSI,
                           [c_int, c_int, ctypes.c_char_p], ctypes.c_double),
                          ('_get_solution_list', phreeqc.GetSolutionList,
                           [c_int], ctypes.c_char_p)
                         ]
        for name, com_obj, argtypes, restype in method_mapping:
            com_obj.argtypes = argtypes
            com_obj.restype = restype
            setattr(self, name, com_obj)
        self.var = VAR()
        self.phc_error_count = 0
        self.phc_warning_count = 0
        self.phc_database_error_count = 0
        self.id_ = self.create_iphreeqc()

    @staticmethod
    def raise_ipq_error(error_code):
        """There was an error, raise an exception.
        """
        error_types = {0: 'ok', -1: 'out of memory', -2: 'bad value',
                       -3: 'invalid argument type', -4: 'invalid row',
                       -5: 'invalid_column', -6: 'invalid instance id'}
        error_type = error_types[error_code]
        if error_type:
            raise PhreeqcException(error_type)

    def raise_string_error(self, errors):
        """Raise an exception with message from IPhreeqc error.
        """
        if errors > 1:
            msg = '%s errors occured.\n' % errors
        elif errors == 1:
            msg = 'An error occured.\n'
        else:
            msg = 'Wrong error number.'
        raise Exception(msg + self.get_error_string())

    def accumulate_line(self, line):
        """Put line in input buffer.
        """
        errors = self._accumulate_line(self.id_, bytes(line, 'utf-8'))
        if errors != 0:
            self.raise_string_error(errors)

    def add_error(self, phc_error_msg):
        """Add an error message to Phreeqc.
        """
        errors = self._add_error(self.id_, bytes(phc_error_msg, 'utf-8'))
        if errors < 0:
            self.raise_string_error(errors)
        else:
            self.phc_error_count = errors

    def add_warning(self, phc_warn_msg):
        """Add an warning message to Phreeqc.
        """
        errors = self._add_warning(self.id_, bytes(phc_warn_msg, 'utf-8'))
        if errors < 0:
            self.raise_string_error(errors)
        else:
            self.phc_warning_count = errors

    def clear_accumlated_lines(self):
        """Clear the input buffer.
        """
        errors = self._clear_accumlated_lines(self.id_)
        if errors != 0:
            self.raise_string_error(errors)

    @property
    def column_count(self):
        """Get number of columns in selected output.
        """
        return self._get_selected_output_column_count(self.id_)

    def create_iphreeqc(self):
        """Create a IPhreeqc object.
        """
        error_code = self._create_iphreeqc(ctypes.c_void_p())
        if error_code < 0:
            self.raise_ipq_error(error_code)
        id_ = error_code
        return id_

    def destroy_iphreeqc(self):
        """Delete the current instance of IPhreeqc.
        """
        error_code = self._destroy_iphreeqc(self.id_)
        if error_code < 0:
            self.raise_ipq_error(error_code)

    def get_component(self, index):
        """Get one component.
        """
        component = self._get_component(self.id_, index).decode('utf-8')
        if not component:
            raise IndexError('No component for index %s' % index)
        return component

    @property
    def component_count(self):
        """Return the number of components.
        """
        return self._get_component_count(self.id_)

    def get_component_list(self):
        """Return all component names.
        """
        get_component = self.get_component
        return [get_component(index) for index in range(self.component_count)]

    def get_error_string(self):
        """Retrieves the error messages.
        """
        return self._get_error_string(self.id_).decode('utf-8')

    # Vitens VIPHREEQC Extensions

    # gas
    def get_gas_volume(self, gas):
        return self._get_gas_volume(self.id_, gas)
    # gas
    def get_gas_pressure(self, gas):
        return self._get_gas_pressure(self.id_, gas)
    # gas
    def get_gas_total_moles(self, gas):
        return self._get_gas_total_moles(self.id_, gas)
    def get_gas_components(self, gas):
        return self._get_gas_components(self.id_, gas).decode('utf-8').split(",")
    def get_gas_component_moles(self, gas, component):
        return self._get_gas_component_moles(self.id_, gas, bytes(component, 'utf-8'))

    def get_gas_components_moles(self, gas):
        component_list = self.get_gas_components(gas)
        component_moles = {}
        for component in component_list:
            component_moles[component] = self.get_gas_component_moles(gas, component)

        return component_moles

    def get_gas_components_fractions(self, gas):
        total_moles = self.get_gas_total_moles(gas)

        return {name: value/total_moles for (name, value) in self.get_gas_components_moles(gas).items()}

    def get_gas_components_pressures(self, gas):
        total_moles = self.get_gas_total_moles(gas)
        total_pressure = self.get_gas_pressure(gas)

        return {name: value/total_moles * total_pressure for (name, value) in self.get_gas_components_moles(gas).items()}




    # solution
    def get_ph(self, solution):
        return self._get_ph(self.id_, solution)
    def get_pe(self, solution):
        return self._get_pe(self.id_, solution)
    def get_sc(self, solution):
        return self._get_sc(self.id_, solution)
    def get_mu(self, solution):
        return self._get_mu(self.id_, solution)
    def get_temperature(self, solution):
        return self._get_temperature(self.id_, solution)
    def get_mass(self, solution):
        return self._get_mass(self.id_, solution)
    def get_total(self, solution, element):
        return self._get_total(self.id_, solution, bytes(element, 'utf-8'))
    def get_total_element(self, solution, element):
        return self._get_total_element(self.id_, solution, bytes(element, 'utf-8'))
    def get_moles(self, solution, species):
        return self._get_moles(self.id_, solution, bytes(species, 'utf-8'))
    def get_activity(self, solution, species):
        return self._get_activity(self.id_, solution, bytes(species, 'utf-8'))
    def get_molality(self, solution, species):
        return(self._get_molality(self.id_, solution, bytes(species, 'utf-8')))
    def get_species_moles(self, solution):
        """ Returns a list of species and their molarity """
        species_list = self.get_species(solution)
        species_moles = {}
        for species in species_list:
            species_moles[species] = self.get_moles(solution, species)
        return species_moles
    def get_species_molalities(self, solution):
        """ Returns a list of species and their molality """
        species_list = self.get_species(solution)
        species_moles = {}
        for species in species_list:
            species_moles[species] = self.get_molality(solution, species)
        return species_moles
    def get_species_activities(self, solution):
        """ Returns a list of species and their molality """
        species_list = self.get_species(solution)
        species_moles = {}
        for species in species_list:
            species_moles[species] = self.get_activity(solution, species)
        return species_moles

    def get_species_masters(self, solution):
        """ Returns a dict of species and their masters """
        species_list = self._get_species_masters(self.id_, solution).decode('utf-8').split(";")
        species_dict = {}
        for specie in species_list:
            species_dict[specie.split(":")[0]] = specie.split(":")[1].split(",")[:-1]
        return species_dict

    def get_masters_species(self, solution):
        masters_list = {}
        species_dict = self.get_species_masters(solution)

        for specie, masters in species_dict.items():
            for master in masters:
                masters_list.setdefault(master,[]).append(specie)
            
        return masters_list

    def get_solution_list(self):
        solution_list = self._get_solution_list(self.id_).decode('utf-8').split(",")
        return list(map(int, solution_list))
    def get_species(self, solution):
        return self._get_species(self.id_, solution).decode('utf-8').split(",")
    def get_si(self, solution, phase):
        return self._get_si(self.id_, solution, bytes(phase, 'utf-8'))
    def get_phases(self, solution):
        # no idea why this is necessary.. it won't work otherwise
        return self.dll.GetPhases(self.id_, solution).decode('utf-8').split(",")
    def get_phases_si(self, solution):
        """ Returns a list of phases and their solubility index """
        phases = self.get_phases(solution)
        phases_si = {}
        for phase in phases:
            phases_si[phase] = self.get_si(solution, phase)
        return phases_si
    def get_elements(self, solution):
        return self._get_elements(self.id_, solution).decode('utf-8').split(",")

    def get_elements_totals(self, solution):
        """ Returns a list of elements and their totals """
        elements = self.get_elements(solution)
        element_total = {}
        for element in elements:
            element_total[element] = self.get_total(solution, element)
        return element_total

    def set_dump_string_on(self):
        return self._set_dump_string_on(self.id_,1)
    def set_dump_string_off(self):
        return self._set_dump_string_on(self.id_,0)

    def get_dump_string(self):
        return self._get_dump_string(self.id_)
    # END Vitens extensions

    def get_selected_output_value(self, row, col):
        """Get one value from selected output at given row and column.
        """
        error_code = self._get_value(self.id_, row, col, self.var)
        if error_code != 0:
            self.raise_ipq_error(error_code)
        type_ = self.var.type
        value = self.var.value
        if type_ == 3:
            val = value.double_value
        elif type_ == 2:
            val = value.long_value
        elif type_ == 4:
            val = value.string_value.decode('utf-8')
        elif type_ == 0:
            val = None
        if type_ == 1:
            self.raise_error(value.error_code)
        return val

    def get_selected_output_array(self):
        """Get all values from selected output.
        """
        nrows = self.row_count
        ncols = self.column_count
        results = []
        for row in range(nrows):
            result_row = []
            for col in range(ncols):
                result_row.append(self.get_selected_output_value(row, col))
            results.append(result_row)
        return results

    def get_selected_output_row(self, row):
        """Get all values for one from selected output.
        """
        if row < 0:
            row = self.row_count + row
        ncols = self.column_count
        results = []
        for col in range(ncols):
            results.append(self.get_selected_output_value(row, col))
        return results

    def get_selected_output_column(self, col):
        """Get all values for one column from selected output.
        """
        if col < 0:
            col = self.column_count + col
        nrows = self.row_count
        results = []
        for row in range(nrows):
            results.append(self.get_selected_output_value(row, col))
        return results

    def set_selected_output_file_off(self):
        """Turn on writing to selected output file.
        """
        self._set_selected_output_file_on(self.id_, 0)

    def set_selected_output_file_on(self):
        """Turn on writing to selected output file.
        """
        self._set_selected_output_file_on(self.id_, 1)

    def load_database(self, database_name):
        """Load a database with given file_name.
        """
        self.phc_database_error_count = self._load_database(
            self.id_, bytes(database_name, 'utf-8'))

    def load_database_string(self, input_string):
        """Load a datbase from a string.
        """
        self.phc_database_error_count = self._load_database_string(
            self.id_, ctypes.c_char_p(bytes(input_string, 'utf-8')))

    @property
    def row_count(self):
        """Get number of rows in selected output.
        """
        return self._get_selected_output_row_count(self.id_)

    def run_string(self, cmd_string):
        """Run PHREEQC input from string.
        """
        #print(cmd_string)
        if self.debug:
            print(cmd_string)

        errors = self._run_string(self.id_,
                                  ctypes.c_char_p(bytes(cmd_string, 'utf-8')))
        if errors != 0:
            self.raise_string_error(errors)


class VARUNION(ctypes.Union):
    # pylint: disable-msg=R0903
    # no methods
    """Union with types.

    See Var.h in PHREEQC source.
    """
    _fields_ = [('long_value', ctypes.c_long),
                ('double_value', ctypes.c_double),
                ('string_value', ctypes.c_char_p),
                ('error_code', ctypes.c_int)]


class VAR(ctypes.Structure):
    # pylint: disable-msg=R0903
    # no methods
    """Struct with data type and data values.

    See Var.h in PHREEQC source.
    """
    _fields_ = [('type', ctypes.c_int),
                ('value', VARUNION)]

class PhreeqcException(Exception):
    """Error in Phreeqc call.
    """
    pass
