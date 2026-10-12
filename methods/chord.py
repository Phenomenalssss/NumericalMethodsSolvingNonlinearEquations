import sympy
from theme import show_error, show_iteration


def chord(function, a, b, eps):
    x = sympy.symbols('x')
    f = sympy.lambdify(x, function, "math")
    if f(a) * f(b) >= 0:
        show_error("На заданном отрезке не обнаружена смена знака функции.")
        return
    first_df = sympy.lambdify(x, sympy.diff(function, x), "math")
    second_df = sympy.lambdify(x, sympy.diff(function, x, 2), "math")
    iteration = 1
    if first_df(a) * second_df(a) > 0:
        x0 = a
        while True:
            if f(b) - f(x0) == 0:
                show_error(f"Деление на ноль на итерации {iteration}: F(b) = F(x{iteration - 1}).")
                return
            x1 = x0 - (f(x0) * (b - x0)) / (f(b) - f(x0))
            delta_x = abs(x1 - x0)
            show_iteration(iteration, x1, delta_x, eps, f(x1))
            if delta_x <= eps:
                return x1
            x0 = x1
            iteration += 1
    else:
        x0 = b
        while True:
            if f(x0) - f(a) == 0:
                show_error(f"Деление на ноль на итерации {iteration}: F(x{iteration - 1}) = F(a).")
                return
            x1 = x0 - (f(x0) * (x0 - a)) / (f(x0) - f(a))
            delta_x = abs(x1 - x0)
            show_iteration(iteration, x1, delta_x, eps, f(x1))
            if delta_x <= eps:
                return x1
            x0 = x1
            iteration += 1