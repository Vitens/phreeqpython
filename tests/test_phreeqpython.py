from phreeqpython import PhreeqPython, Solution
from nose.tools import assert_equal

class TestPhreeqPython(object):

    pp = PhreeqPython()

    def test_basiscs(self):
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

    def test_solution_functions(self):
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

        sol.change_ph(10)
        assert_equal(round(sol.pH, 2), 10)

        sol.saturate('Calcite',1)
        assert_equal(sol.si('Calcite'), 1)

    def test_mixing(self):
        sol1 = self.pp.add_solution({'NaCl':1})
        sol2 = self.pp.add_solution({})
        sol3 = self.pp.mix_solutions({sol1:0.5, sol2:0.5})
        assert_equal(round(sol3.total('Na'), 4), 0.0005)

    def test_solution_listing(self):

        # test solution list
        sol_list = self.pp.ip.get_solution_list()
        assert_equal(len(sol_list), 7)
        # test forgetting solutions
        self.pp.remove_solutions([1, 2, 3])
        sol_list = self.pp.ip.get_solution_list()
        assert_equal(len(sol_list), 4)
