import sympy
from theme import show_error, show_start, show_iteration


def bisection(function, a, b, eps):
    x = sympy.symbols('x')
    f = sympy.lambdify(x, function, "math")
    if f(a) * f(b) >= 0:
        show_error("На заданном отрезке не обнаружена смена знака функции.")
        return
    fa = f(a)
    fb = f(b)
    x_previous = (a + b) / 2
    fx_previous = f(x_previous)
    show_start(x_previous, fx_previous)
    if fx_previous == 0:
        return x_previous
    if fa * fx_previous < 0:
        right = x_previous
        left = a
    elif fx_previous * fb < 0:
        left = x_previous
        right = b
    iteration = 1
    while True:
        x = (left + right) / 2
        fx = f(x)
        delta_x = abs(x - x_previous)
        show_iteration(iteration, x, delta_x, eps, fx)
        if delta_x <= eps:
            return x
        if fx == 0:
            return x
        if f(left) * fx < 0:
            right = x
        else:
            left = x
        x_previous = x
        iteration += 1