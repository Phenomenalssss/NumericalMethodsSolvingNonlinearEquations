import sympy
from theme import show_error, show_iteration


def tangent(function, a, b, eps):
    x = sympy.symbols('x')
    f = sympy.lambdify(x, function, "math")
    if f(a) * f(b) >= 0:
        show_error("На заданном отрезке не обнаружена смена знака функции.")
        return
    first_df = sympy.lambdify(x, sympy.diff(function, x), "math")
    second_df = sympy.lambdify(x, sympy.diff(function, x, 2), "math")
    if first_df(a) * second_df(a) > 0:
        x0 = b
    else:
        x0 = a
    iteration = 1
    while True:
        if first_df(x0) == 0:
            show_error(f"Первая производная равна нулю в x{iteration - 1} = {x0}.")
            return
        x1 = x0 - f(x0) / first_df(x0)
        delta_x = abs(x1 - x0)
        show_iteration(iteration, x1, delta_x, eps, f(x1))
        if delta_x <= eps:
            return x1
        x0 = x1
        iteration += 1