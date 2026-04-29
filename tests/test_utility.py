from phreeqpython.utility import convert_units

class TestUtility:

    def test_convert_units(self):
        # test unit conversions
        assert round(
            convert_units('NaOH', 1, from_units='mol', to_units='mmol'), 0
        ) == 1000.0
        assert round(
            convert_units('NaOH', 1, from_units='mol', to_units='mg'), 0
        ) == 39997.0
        assert round(
            convert_units('NaOH', 1, from_units='mol', to_units='ug'), 0
        ) == 39997110.0

        assert round(
            convert_units('NaOH', 1, from_units='mmol', to_units='mol'), 4
        ) == 0.001
        assert round(
            convert_units('NaOH', 1, from_units='mmol', to_units='mg'), 3
        ) == 39.997
        assert round(
            convert_units('NaOH', 1, from_units='mmol', to_units='ug'), 0
        ) == 39997.0

        assert round(
            convert_units('NaOH', 1, from_units='mg', to_units='mmol'), 4
        ) == 0.025
        assert round(
            convert_units('NaOH', 1, from_units='mg', to_units='mol'), 7
        ) == 2.5e-05
        assert round(
            convert_units('NaOH', 1, from_units='mg', to_units='ug'), 0
        ) == 1000.0

        assert round(
            convert_units('NaOH', 1, from_units='ug', to_units='mmol'), 7
        ) == 2.5e-05
        assert round(
            convert_units('NaOH', 1, from_units='ug', to_units='mol'), 10
        ) == 2.5e-08
        assert round(
            convert_units('NaOH', 1, from_units='ug', to_units='mg'), 4
        ) == 0.001
