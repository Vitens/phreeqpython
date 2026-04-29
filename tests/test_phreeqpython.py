from phreeqpython import PhreeqPython, utility
from pathlib import Path
import pytest

class TestPhreeqPython:

    pp = PhreeqPython()

    def test01_basiscs(self):
        sol = self.pp.add_solution_simple({'CaCl2':1, 'Na2CO3':1})        
        # test solution number
        assert sol.number == 0
        # test solution ph, sc, pe and temperature
        assert sol.pH == pytest.approx(10.41, abs=1e-2)
        assert sol.sc == pytest.approx(435.81, abs=1e-2)
        assert sol.pe == pytest.approx(7.4, abs=1e-2)
        assert sol.temperature == pytest.approx(25, abs=1e-2)
        # test solution composition
        assert sol.total("Ca", units='mol') == pytest.approx(0.001, abs=1e-4)
        assert sol.total("Cl") == pytest.approx(2, abs=1e-4)
        assert sol.total_element("C") == pytest.approx(1, abs=1e-4)
        # test si
        assert sol.si("Calcite") == pytest.approx(1.71, abs=1e-2)
        # test phases
        assert len(sol.phases) == 10
        assert len(sol.elements) == 5
        # test ionic strength
        assert sol.I == pytest.approx(0.0045, abs=1e-4)
        # test mass
        assert sol.mass == pytest.approx(1.0, abs=1e-2)
        # test activity
        assert sol.activity('Ca+2', units='mol') == pytest.approx(0.00054, abs=1e-5)
        # test moles
        assert sol.moles('Ca+2', units='mol') == pytest.approx(0.00071, abs=1e-5)
        assert sol.molality('Ca+2', units='mol') == pytest.approx(0.00071, abs=1e-5)
        # test species_moles
        assert sol.species_moles['Ca+2'] == pytest.approx(0.00071, abs=1e-5)
        assert sol.species_molalities['Ca+2'] == pytest.approx(0.00071, abs=1e-5)
        assert sol.species_activities['Ca+2'] == pytest.approx(0.00054, abs=1e-5)

        # test add_solution_simple as milligrams
        sol2 = self.pp.add_solution_simple({'Ca': 40.078, 'Na': 22.99, 'MgSO4': utility.convert_units('MgSO4', 1, 'mmol', 'mg')}, units='mg')
        # test conversion from mg to mmol
        assert sol2.total("Ca", 'mmol') == pytest.approx(1, abs=1e-4)
        # test amount in mg
        assert sol2.total("Na", 'mg') == pytest.approx(22.99, abs=1e-4)
        # test amount in mmol from molecule added in mg's
        assert sol2.total("Mg", 'mmol') == pytest.approx(1, abs=1e-4)

    def test02_solution_functions(self):
        sol = self.pp.add_solution_simple({'CaCl2':1})
        # add components
        sol.add('NaHCO3', 1)
        assert sol.total('Na') == pytest.approx(1, abs=1e-4)
        # change solution in mmols (add and subtract)
        sol.change({'MgCl2': 1, 'NaCl': -0.5})        
        assert sol.total('Cl') == pytest.approx(3.5, abs=1e-2)
        assert sol.total('Mg') == pytest.approx(1, abs=1e-2)
        # change solution in mgs (add and subtract)
        sol.change({'Na': 11.495, 'MgCl2': -utility.convert_units('MgCl2', 1, 'mmol', 'mg')}, 'mg')        
        assert sol.total('Cl') == pytest.approx(1.5, abs=1e-2)
        assert sol.total('Mg') == pytest.approx(0, abs=1e-2)

        # desaturate
        sol.desaturate('Calcite')
        assert sol.si('Calcite') == pytest.approx(0, abs=1e-9)

        # remove mmol
        sol.remove('Na', 0.5)
        assert sol.total('Na') == pytest.approx(0.5, abs=1e-4)

        # remove fraction
        sol.remove_fraction('Na', 0.5)
        assert sol.total('Na') == pytest.approx(0.25, abs=1e-5)

        # change ph using base
        sol.change_ph(10)
        assert sol.pH == pytest.approx(10, abs=1e-2)
        # change ph using acid
        sol.change_ph(5)
        assert sol.pH == pytest.approx(5, abs=1e-2)
        # raise ph using custom chemical (NaOH)
        sol.change_ph(8, 'NaOH')
        assert sol.pH == pytest.approx(8, abs=1e-2)

        sol.saturate('Calcite', 1)
        assert sol.si('Calcite') == pytest.approx(1, abs=1e-9)

        sol.change_temperature(10)
        assert sol.temperature == pytest.approx(10, abs=1e-9)

    def test03_mixing(self):
        sol1 = self.pp.add_solution_simple({'NaCl':1})
        sol2 = self.pp.add_solution_simple({})
        sol3 = self.pp.mix_solutions({sol1:0.5, sol2:0.5})
        assert sol3.total('Na') == pytest.approx(0.5, abs=1e-1)

    def test04_solution_listing(self):
        # test solution list
        sol_list = self.pp.ip.get_solution_list()
        assert len(sol_list) == 8
        # test forgetting solutions
        self.pp.remove_solutions([1, 2, 3])
        sol_list = self.pp.ip.get_solution_list()
        assert len(sol_list) == 5

    def test05_addition(self):
        sol1 = self.pp.add_solution_simple({'NaCl':1})
        sol2 = self.pp.add_solution_simple({'NaCl':2})
        sol3 = sol1 + sol2
        assert sol3.mass == pytest.approx(2.0, abs=0.5)

        sol4 = sol1 / 2 + sol2 / 2
        assert sol4.total('Na') == pytest.approx(1.5, abs=1e-1)

        sol5 = sol1 * 0.5 + sol2 * 0.5
        assert sol5.total('Na') == pytest.approx(1.5, abs=1e-1)

        # test invalid mixtures
        def testadd(sol, other):
            return sol + other
        def testdiv(sol, other):
            return sol / other
        def testmul(sol, other):
            return sol * other

        with pytest.raises(TypeError):
            testadd(sol1, 1)
        with pytest.raises(TypeError):
            testdiv(sol1, sol2)
        with pytest.raises(TypeError):
            testmul(sol1, sol2)

    def test06_misc(self):
        sol1 = self.pp.add_solution_simple({'NaCl':1})
        sol2 = sol1.copy()
        assert sol1.sc == pytest.approx(sol2.sc, abs=1e-9)

        sol2.forget()
        assert sol2.pH == pytest.approx(-999, abs=1e-9)

    def test07_dump_and_load(self):
        sol5a = self.pp.get_solution(5)
        self.pp.dump_solutions()
        return
        pp2 = PhreeqPython(from_file='dump.gz')
        sol5b = pp2.get_solution(5)

        assert pytest.approx(sol5a.sc, 2) == sol5b.sc
        assert self.pp.ip.get_solution_list() == pp2.ip.get_solution_list()

    def test08_raw_solutions(self):
        sol8 = self.pp.add_solution_raw({
            'pH': '8.0',
            'temp': '20',
            'units': 'mg/l',
            'Alkalinity': '200 as HCO3',
            'Ca':'40.1',
            'Cl':'71.0'
            })
        assert sol8.pH == pytest.approx(8.0, abs=1e-9)
        assert sol8.total_element('Ca') == pytest.approx(1, rel=0.01)
        assert sol8.total_element('Cl') == pytest.approx(2, rel=0.01)

    def test09_gas_phases(self):

        gas1 = self.pp.add_gas({
            'CH4(g)': 0.5,
            'Ntg(g)': 0.5
            },
            volume = 1,
            pressure = 1,
            fixed_pressure = False,
            fixed_volume = True
            )

        assert gas1.pressure == pytest.approx(1, abs=1e-9)
        assert gas1.volume == pytest.approx(1, rel=0.01)
        assert gas1.total_moles == pytest.approx(0.041, rel=0.01)
        assert gas1.pressure == pytest.approx(1, rel=0.01)
        assert gas1.partial_pressures['CH4(g)'] == pytest.approx(0.5, rel=0.01)
        assert gas1.partial_pressures['Ntg(g)'] == pytest.approx(0.5, rel=0.01)


        sol9 = self.pp.add_solution({})

        sol9.interact(gas1)

        assert gas1.pressure == pytest.approx(0.975, rel=0.01)  # Tolerance of 0.001
        assert gas1.volume == pytest.approx(1, rel=0.01)           # Tolerance of 2
        assert gas1.partial_pressures['CH4(g)'] == pytest.approx(0.48, rel=0.01)  # Tolerance of 2
        assert gas1.partial_pressures['Ntg(g)'] == pytest.approx(0.49, rel=0.01)  # Tolerance of 2


    def test10_use_non_default_database_directory(self):
        pp_test10 = PhreeqPython(database_directory=Path(__file__).parent)
        sol = pp_test10.add_solution_simple({'CaCl2':1, 'Na2CO3':1})
        # test solution number
        assert sol.number == 0
        # test solution ph, sc, pe and temperature
        assert sol.pH == pytest.approx(10.41, abs=1e-2)
        assert sol.sc == pytest.approx(435.81, abs=1e-2)
        assert sol.pe == pytest.approx(7.4, abs=1e-2)
        assert sol.temperature == pytest.approx(25, abs=1e-2)

    def test11_phases_si(self):

        sol = self.pp.add_solution({
                "units": "ppm",
                "Mg": 516, 
                "Mn(2)": 2.6, 
            }, 
        )
        assert sol.si('Hausmannite') == pytest.approx(-10.90, abs=1e-2)
        assert sol.si('Manganite') == pytest.approx(-4.96, abs=1e-2)
        assert sol.si('Pyrochroite') == pytest.approx(-5.82, abs=1e-2)
        assert sol.si('Pyrolusite') == pytest.approx(-10.00, abs=1e-2)

    def test12_equilibrium_phase(self):
        sol = self.pp.add_solution({
            'pH': 7,
            'temp': 25
        })
        eq = self.pp.add_equilibrium_phase(['CO2(g)', 'Calcite'], [-2, 0], [1, 1])

        sol.interact(eq)

        assert pytest.approx((eq.components['CO2(g)'] - 1) * 1e3, 3) == -1.991
        assert pytest.approx((eq.components['Calcite'] - 1) * 1e3, 3) == -1.655
        assert pytest.approx(sol.total('Ca'), 3) == 1.655

    def test13_extraneous_properties(self):
        sol = self.pp.add_solution({
            'pH': 7,
            'temp': 25
        }, {
            'A': 1,
            'B': 10,
            'C': 20,
            'D': {
                'E': 1,
                'F': 2
            }
        })
        
        assert sol.extraneous['A'] == 1
        assert sol.extraneous['B'] == 10
        assert sol.extraneous['C'] == 20

        sol2 = self.pp.add_solution({
            'pH': 7,
            'temp': 25
        }, {'B': 5, 'D': {'E': 2}})

        assert sol2.extraneous == {'B': 5, 'D': {'E': 2}}

        # test mixing
        sol3 = sol * 0.5 + sol2 * 0.5
        assert sol3.extraneous['A'] == 0.5
        assert sol3.extraneous['B'] == 7.5
        assert sol3.extraneous['D']['E'] == 1.5
        assert sol3.extraneous['D']['F'] == 1

        # test copying
        sol4 = sol3.copy()
        assert sol4.extraneous['A'] == 0.5
        assert sol4.extraneous['D']['E'] == 1.5
        assert sol4.extraneous['D']['F'] == 1
