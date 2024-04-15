class EquilibriumPhase(object):
    """ PhreeqPy Solution Class """
    def __init__(self, phreeqpython, number):
        self.pp = phreeqpython
        self.number = number

    @property
    def components(self):
        return self.pp.ip.get_equilibrium_phase_components_moles(self.number) 