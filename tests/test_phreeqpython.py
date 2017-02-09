from phreeqpython import PhreeqPython, Solution
from nose.tools import assert_equal, assert_almost_equal, assert_raises

class TestPhreeqPython(object):

    pp = PhreeqPython()

    def test1_basiscs(self):
        sol = self.pp.add_solution({'CaCl2':1, 'Na2CO3':1})
        # test solution number
        assert_equal(sol.number, 1)
        # test solution ph, sc, pe and temperature
        assert_equal(round(sol.pH, 2), 10.41)
        assert_equal(round(sol.sc, 2), 435.35)
        assert_equal(round(sol.pe, 2), 7.4)
        assert_equal(round(sol.temperature, 2), 25)
        # test solution composition
        assert_equal(round(sol.total("Ca"), 4), 0.001)
        assert_equal(round(sol.total("Cl"), 4), 0.002)
        assert_equal(round(sol.total_element("C"), 4), 0.001)
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
        assert_equal(round(sol.activity('Ca+2'),5),0.00054)
        # test moles
        assert_equal(round(sol.moles('Ca+2'),5),0.00071)

        assert_equal(round(sol.molality('Ca+2'),5),0.00071)

        # test species_moles
        assert_equal(round(sol.species_moles['Ca+2'],5), 0.00071)
        assert_equal(round(sol.species_molalities['Ca+2'],5), 0.00071)
        assert_equal(round(sol.species_activities['Ca+2'],5), 0.00054)

    def test2_solution_functions(self):
        sol = self.pp.add_solution({'CaCl2':1})
        # add components
        sol.add('NaHCO3', 1)
        assert_equal(round(sol.total('Na'), 4), 0.001)
        # desaturate
        sol.desaturate('Calcite')
        assert_equal(sol.si('Calcite'), 0)

        # remove mmol
        sol.remove('Na',0.5)
        assert_equal(round(sol.total('Na'), 4), 0.0005)

        # remove fraction
        sol.remove_fraction('Na',0.5)
        assert_equal(round(sol.total('Na'), 5), 0.00025)

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
        sol1 = self.pp.add_solution({'NaCl':1})
        sol2 = self.pp.add_solution({})
        sol3 = self.pp.mix_solutions({sol1:0.5, sol2:0.5})
        assert_equal(round(sol3.total('Na'), 4), 0.0005)


    def test4_solution_listing(self):
        # test solution list
        sol_list = self.pp.ip.get_solution_list()
        assert_equal(len(sol_list), 7)
        # test forgetting solutions
        self.pp.remove_solutions([1, 2, 3])
        sol_list = self.pp.ip.get_solution_list()
        assert_equal(len(sol_list), 4)

    def test5_addition(self):
        sol1 = self.pp.add_solution({'NaCl':1})
        sol2 = self.pp.add_solution({'NaCl':2})
        sol3 = sol1 + sol2
        assert_equal(round(sol3.mass),2.0)

        sol4 = sol1/2 + sol2/2
        assert_equal(round(sol4.total('Na')*1000,1),1.5)

        sol5 = sol1*0.5 + sol2*0.5
        assert_equal(round(sol5.total('Na')*1000,1),1.5)

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
        sol1 = self.pp.add_solution({'NaCl':1})
        sol2 = sol1.copy()
        assert_equal(sol1.sc,sol2.sc)

        sol2.forget()
        assert_equal(sol2.pH,-999)

    def test7_dump_and_load(self):
        sol5a = self.pp.get_solution(5)
        self.pp.dump_solutions()
        pp2 = PhreeqPython('dump.gz')
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
        assert_almost_equal(sol8.total_element('Ca'), 1e-3, 5)
        assert_almost_equal(sol8.total_element('Cl'), 2e-3, 5)
