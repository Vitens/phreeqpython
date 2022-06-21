from phreeqpython import PhreeqPython, Solution
from pathlib import Path
from nose.tools import assert_equal, assert_almost_equal, assert_raises

class TestPhreeqPython(object):

    pp = PhreeqPython()

    def test1_basiscs(self):
        sol = self.pp.add_solution_simple({'CaCl2':1, 'Na2CO3':1})        
        # test solution number
        assert_equal(sol.number, 0)
        # test solution ph, sc, pe and temperature
        assert_equal(round(sol.pH, 2), 10.41)
        assert_equal(round(sol.sc, 2), 435.81)
        assert_equal(round(sol.pe, 2), 7.4)
        assert_equal(round(sol.temperature, 2), 25)
        # test solution composition
        assert_equal(round(sol.total("Ca", units='mol'), 4), 0.001)
        assert_equal(round(sol.total("Cl"), 4), 2)
        assert_equal(round(sol.total_element("C"), 4), 1)
        # test si
        assert_equal(round(sol.si("Calcite"), 2), 1.71)
        # test phases
        assert_equal(len(sol.phases), 10)
        assert_equal(len(sol.elements), 5)
        # test ionic strength
        assert_equal(round(sol.I,4), 0.0045)
        # test mass
        assert_equal(round(sol.mass,2), 1.0)
        # test activity
        assert_equal(round(sol.activity('Ca+2', units='mol'),5),0.00054)
        # test moles
        assert_equal(round(sol.moles('Ca+2', units='mol'),5),0.00071)

        assert_equal(round(sol.molality('Ca+2', units='mol'),5),0.00071)

        # test species_moles
        assert_equal(round(sol.species_moles['Ca+2'],5), 0.00071)
        assert_equal(round(sol.species_molalities['Ca+2'],5), 0.00071)
        assert_equal(round(sol.species_activities['Ca+2'],5), 0.00054)


        # test add_solution_simple as milligrams
        sol2 = self.pp.add_solution_simple({'Ca': 40.078, 'Na': 22.99, 'MgSO4': 120.37}, units='mg')
        # test conversion from mg to mmol
        assert_equal(round(sol2.total("Ca", 'mmol'), 4), 1)
        # test amount in mg
        assert_equal(round(sol2.total("Na", 'mg'), 4), 22.99)
        # test amount in mmol from molecule added in mg's
        assert_equal(round(sol2.total("Mg", 'mmol'), 4), 1)

    def test2_solution_functions(self):
        sol = self.pp.add_solution_simple({'CaCl2':1})
        # add components
        sol.add('NaHCO3', 1)
        assert_equal(round(sol.total('Na'), 4), 1)
        # change solution in mmols (add and subtract)
        sol.change({'MgCl2': 1, 'NaCl': -0.5})        
        assert_equal(round(sol.total('Cl'), 2), 3.5)
        assert_equal(round(sol.total('Mg'), 2), 1)
        # change solution in mgs (add and subtract)
        sol.change({'Na': 11.495, 'MgCl2': -95.211}, 'mg')        
        assert_equal(round(sol.total('Cl'), 2), 1.5)
        assert_equal(round(sol.total('Mg'), 2), 0)

        # desaturate
        sol.desaturate('Calcite')
        assert_equal(sol.si('Calcite'), 0)

        # remove mmol
        sol.remove('Na',0.5)
        assert_equal(round(sol.total('Na'), 4), 0.5)

        # remove fraction
        sol.remove_fraction('Na',0.5)
        assert_equal(round(sol.total('Na'), 5), 0.25)

        # change ph using base
        sol.change_ph(10)
        assert_equal(round(sol.pH, 2), 10)
        # change ph using acid
        sol.change_ph(5)
        assert_equal(round(sol.pH, 2), 5)
        # raise ph using custom chemical (NaOH)
        sol.change_ph(8, 'NaOH')
        assert_equal(round(sol.pH, 2), 8)

        sol.saturate('Calcite',1)
        assert_equal(sol.si('Calcite'), 1)

        sol.change_temperature(10)
        assert_equal(sol.temperature, 10)

    def test3_mixing(self):
        sol1 = self.pp.add_solution_simple({'NaCl':1})
        sol2 = self.pp.add_solution_simple({})
        sol3 = self.pp.mix_solutions({sol1:0.5, sol2:0.5})
        assert_equal(round(sol3.total('Na'),1), 0.5)


    def test4_solution_listing(self):
        # test solution list
        sol_list = self.pp.ip.get_solution_list()
        assert_equal(len(sol_list), 8)
        # test forgetting solutions
        self.pp.remove_solutions([1, 2, 3])
        sol_list = self.pp.ip.get_solution_list()
        assert_equal(len(sol_list), 5)

    def test5_addition(self):
        sol1 = self.pp.add_solution_simple({'NaCl':1})
        sol2 = self.pp.add_solution_simple({'NaCl':2})
        sol3 = sol1 + sol2
        assert_equal(round(sol3.mass),2.0)

        sol4 = sol1/2 + sol2/2
        assert_equal(round(sol4.total('Na'),1),1.5)

        sol5 = sol1*0.5 + sol2*0.5
        assert_equal(round(sol5.total('Na'),1),1.5)

        # test invalid mixtures
        def testadd(sol, other):
            return sol+other
        def testdiv(sol, other):
            return sol/other
        def testmul(sol, other):
            return sol*other

        assert_raises(TypeError, testadd, sol1, 1)
        assert_raises(TypeError, testdiv, sol1, sol2)
        assert_raises(TypeError, testmul, sol1, sol2)

    def test6_misc(self):
        sol1 = self.pp.add_solution_simple({'NaCl':1})
        sol2 = sol1.copy()
        assert_equal(sol1.sc,sol2.sc)

        sol2.forget()
        assert_equal(sol2.pH,-999)

    def test7_dump_and_load(self):
        sol5a = self.pp.get_solution(5)
        self.pp.dump_solutions()
        pp2 = PhreeqPython(from_file='dump.gz')
        sol5b = pp2.get_solution(5)

        assert_almost_equal(sol5a.sc, sol5b.sc, 2)
        assert_equal(self.pp.ip.get_solution_list(), pp2.ip.get_solution_list())

    def test8_raw_solutions(self):
        sol8 = self.pp.add_solution_raw({
            'pH': '8.0',
            'temp': '20',
            'units': 'mg/l',
            'Alkalinity': '200 as HCO3',
            'Ca':'40.1',
            'Cl':'71.0'
            })
        assert_equal(sol8.pH, 8.0)
        assert_almost_equal(sol8.total_element('Ca'), 1, 2)
        assert_almost_equal(sol8.total_element('Cl'), 2, 2)

    def test9_gas_phases(self):

        gas1 = self.pp.add_gas({
            'CH4(g)': 0.5,
            'Ntg(g)': 0.5
            },
            volume = 1,
            pressure = 1,
            fixed_pressure = False,
            fixed_volume = True
            )

        assert_equal(gas1.pressure, 1)
        assert_almost_equal(gas1.volume, 1, 2)
        assert_almost_equal(gas1.total_moles, 0.041, 2)
        assert_almost_equal(gas1.pressure, 1, 2)
        assert_almost_equal(gas1.partial_pressures['CH4(g)'], 0.5, 2)
        assert_almost_equal(gas1.partial_pressures['Ntg(g)'], 0.5, 2)

        sol9 = self.pp.add_solution({})

        sol9.interact(gas1)

        assert_almost_equal(gas1.pressure, 0.975, 3)
        assert_almost_equal(gas1.volume, 1, 2)
        assert_almost_equal(gas1.partial_pressures['CH4(g)'], 0.48, 2)
        assert_almost_equal(gas1.partial_pressures['Ntg(g)'], 0.49, 2)

    def test10_use_non_default_database_directory(self):
        pp_test10 = PhreeqPython(database_directory=Path(__file__).parent)
        sol = pp_test10.add_solution_simple({'CaCl2':1, 'Na2CO3':1})
        # test solution number
        assert_equal(sol.number, 0)
        # test solution ph, sc, pe and temperature
        assert_equal(round(sol.pH, 2), 10.41)
        assert_equal(round(sol.sc, 2), 435.81)
        assert_equal(round(sol.pe, 2), 7.4)
        assert_equal(round(sol.temperature, 2), 25)

    def test11_pitzer(self):
        pp_test11 = PhreeqPython(database='pitzer.dat')

        solution = pp_test11.add_solution({'units':'mmol/kgw', #set the units (moles per kg of water)
                                    'pH': '10 charge',
                                    'temp': 20, 
                                    'K':1000,
                                    'C': 500
                                   })

        assert_almost_equal(solution.pH, 11.789, 3)
        assert_almost_equal(solution.sc, 73290.5, 1)
