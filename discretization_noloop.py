"""Solver for steady-state 2D confined aquifer
Assumption: 2D Discretization
            3 Neumann & 1 Dirichlet BC

Scheme is cell center
"""
import time

import matplotlib.pyplot as plt
import numpy as np
import xlwt

time1 = time.time()

# # Setting
l_x = 600  # length
l_y = 400  # width
std_error = 0.001
n_x_max = 10  # grid in x-axis
n_y_max = 10  # grid in y-axis
dx = l_x / n_x_max
dy = l_y / n_y_max
T = 2000  # [m2/day]
d_a = 50  # depth average
area_x = dy  # area of x-axis wall of a cell
area_y = dx  # area of y-axis wall of a cell
omega = 0.8
error = 1000
# coefficients
a_known_w = T * area_x / dx  # for west cell
a_known_e = T * area_x / dx  # for east cell
a_known_n = T * area_y / dy  # for north cell
a_known_s = T * area_y / dy  # for south cell
iteration = 0
total_iteration = 200

# # Mesh Generation
x = np.zeros([n_x_max, n_y_max])
y = np.copy(x)
x[1:] = np.cumsum(x[:-1] + dx, axis=0)
y[:][1:] = np.cumsum(y[:][:-1] + dy, axis=1)  # not true

# # Initial Condition
h_old = np.reshape([float(d_a) for i in np.zeros(n_y_max * n_x_max)], [n_y_max, n_x_max])  # convert to matrix 10*10
h_new = np.reshape(np.zeros(n_y_max * n_x_max), [n_y_max, n_x_max])  # convert to matrix 10*10

"""Boundary Condition"""
"top boundary"
h_old[0] = 100  # Dirichlet boundary
h_new[0] = 100  # Dirichlet boundary

"left boundary"
q = 0.1  # newmann boundary [m/day]


"""Governing Equation (Water Head Distribution)"""
def whd(a_p=(2 * a_known_e + 2 * a_known_n), side_coefficient_w=a_known_w, side_coefficient_e=a_known_e,
        side_coefficient_n=a_known_n, side_coefficient_s=a_known_s, source=0.):
    h_p = ((1 / a_p) * (side_coefficient_w * h_old[i][j - 1] + side_coefficient_e * h_old[i][j + 1] +
                        side_coefficient_n * h_old[i - 1][j] + side_coefficient_s * h_old[i + 1][j] + source))
    return h_p


"""Processing"""
# while error > std_error:
while iteration < total_iteration:
    iteration += 1

    # top boundary
    h_old[0] = 100

    "left_boundary (constant_flow)"
    h_old[-1][0] = (1 / (a_known_e + a_known_n + a_known_s)) * ((2 * a_known_e) * h_old[-1][1] +
                                                                a_known_n * h_old[-2][0] + q * area_x)
    h_old[1:-1, 0] = (1 / (a_known_e + a_known_n + a_known_s)) * ((2 * a_known_e) * h_old[1:-1, 1] +
                                                                  a_known_n * h_old[:-2, 0] + a_known_s *
                                                                  h_old[2:, 0] + q * area_x)

    "left boundary (no flow)"
    h_new[1:-1, 0] = (1 / (a_known_e + a_known_n + a_known_s)) * (a_known_e * h_old[1:-1, 1] +
                                                                  a_known_n * h_old[:-2, 0] + a_known_s *
                                                                  h_old[2:, 0])

    # j = 0
    # for i in range(1, n_y_max - 1):
    #     h_new[i][j] = (1 / (a_known_e + a_known_n + a_known_s)) * (a_known_e * h_old[i][j + 1] +
    #                                                                a_known_n * h_old[i - 1][j] + a_known_s *
    #                                                                h_old[i + 1][j])
    "right boundary (no flow)"
    h_old[1:-1, -1] = (1 / (a_known_w + a_known_n + a_known_s)) * (a_known_w * h_old[1:-1, -2] +
                                                                   a_known_n * h_old[:-2, -1] + a_known_s *
                                                                   h_old[2:, -1])
    print('LHS= ', h_old[1:-1, -1])
    print('RHS= ', (1 / (a_known_w + a_known_n + a_known_s)) * (a_known_w * h_old[1:-1, -2] +
                                                                   a_known_n * h_old[:-2, -1] + a_known_s *
                                                                   h_old[2:, -1]))

    # j = n_x_max - 1
    # for i in range(1, n_y_max - 1):
    #     h_old[i][j] = (1 / (a_known_w + a_known_n + a_known_s)) * (a_known_w * h_old[i][j - 1] +
    #                                                                a_known_n * h_old[i - 1][j] + a_known_s *
    #                                                                h_old[i + 1][j])

    "bottom boundary (no flow)"
    i = n_y_max - 1
    for j in range(1, n_x_max):
        if j == n_x_max - 1:
            h_old[i][j] = (1 / (a_known_n + a_known_w + a_known_e)) * (a_known_w * h_old[i][j - 1] +
                                                                       a_known_n * h_old[i - 1][j])
        else:
            h_old[i][j] = (1 / (a_known_n + a_known_w + a_known_e)) * (a_known_w * h_old[i][j - 1] +
                                                                       a_known_n * h_old[i - 1][j] + a_known_e *
                                                                       h_old[i][j + 1])

    """main domain"""
    for j in range(1, n_x_max - 1):
        for i in range(1, n_y_max - 1):
            h_new[i][j] = whd()

    # error = np.linalg.norm((h_new - h_old), 2)
    # print('\nL2Norm = %0.5f' % error)

    print('iteration = ', iteration)

    # print('L2Norm = ', L2Norm)

#     plt.contourf(h_new)
#     plt.gca().invert_yaxis()
#     plt.axis('off')
#     plt.grid()
#     plt.colorbar().ax.set_ylabel('[m]', rotation=270)
#     plt.pause(0.001)
#     plt.show(block=False)
#     plt.clf()
#
#     h_old = h_new
#
# print('L2Norm = ', np.linalg.norm(h_new))
# print('iteration = ', iteration)
#
# plt.contourf(h_new)
# plt.gca().invert_yaxis()
# plt.colorbar().ax.set_ylabel('[m]', rotation=270)
# plt.savefig('Final_Result.png')
# plt.show()

time2 = time.time()

print('\nTotal time = ', time2 - time1)

# # write in Excel
# result = xlwt.Workbook('Discretization')
# ws = result.add_sheet('Sheet1')
#
# ws.write(0, 0, 'Water Head Distribution')
#
# for i, row in enumerate(h_new):
#     for j, col in enumerate(h_new[i]):
#         ws.write(i + 1, j, float('%0.2f' % h_new[i][j]))
# result.save('Discretization.xls')
