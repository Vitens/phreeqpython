from phreeqpython import PhreeqPython
import re
import json
import matplotlib.pyplot as plt

pp = PhreeqPython()

sol = pp.add_solution({
            'pH': 13,
            'Na': 150,
            'N(5)': '100 charge'
            })

surf1 = pp.add_surface({
        'Hfo_w': "0.2e-3, 600, 88e-3",
        'Hfo_s': "0.5e-5"
        },
        equilibrate_with = sol
        )

sol.add('ZnNO3', 10e-6, 'mol')

sol.interact(surf1)
surf1.surface

# total = surf1.totals_Hfo_s + surf1.totals_Hfo_w

# print(surf1.totals_Hfo_s)
# print(surf1.totals_Hfo_w)
# print(surf1.charge_balance_Hfo)

# print(surf1.print_surface)


# x_axis = []
# y_axis = []
# start = 4
# for x in range(10):
#         x_axis.append(start)
#         start += 0.5
#         x_axis.append(start)
#         start += 0.5
#         y_axis.append(0)
#         y_axis.append(0)
# x_axis.append(14)
# y_axis.append(0)

# print(x_axis)

# plt.plot(x_axis, y_axis)
# plt.ylabel('% sorbed')
# plt.xlabel('pH')
# plt.show()