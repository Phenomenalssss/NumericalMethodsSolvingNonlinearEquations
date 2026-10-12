import gc
import statistics
from time import perf_counter_ns
from decimal import Decimal

import mpmath
import sympy
from rich import box
from rich.markup import escape
from rich.table import Table

from theme import BLUE, GREEN, MAUVE, PEACH, RED, TEXT, console, show_error


def bisection_core(f, df, d2f, fa, fb, a, b, eps):
    x_prev = (a + b) / 2
    fx_prev = f(x_prev)
    if fx_prev == 0:
        return x_prev, 0
    if fa * fx_prev < 0:
        left, right, f_left = a, x_prev, fa
    else:
        left, right, f_left = x_prev, b, fx_prev
    n = 1
    while True:
        x = (left + right) / 2
        if abs(x - x_prev) <= eps:
            return x, n
        fx = f(x)
        if fx == 0:
            return x, n
        if f_left * fx < 0:
            right = x
        else:
            left, f_left = x, fx
        x_prev = x
        n += 1


def chord_core(f, df, d2f, fa, fb, a, b, eps):
    if df(a) * d2f(a) > 0:
        x0, fx0 = a, fa
        fixed, f_fixed = b, fb
    else:
        x0, fx0 = b, fb
        fixed, f_fixed = a, fa
    n = 0
    while True:
        den = f_fixed - fx0
        if den == 0:
            return None, n
        x1 = x0 - fx0 * (fixed - x0) / den
        n += 1
        if abs(x1 - x0) <= eps:
            return x1, n
        x0, fx0 = x1, f(x1)


def tangent_core(f, df, d2f, fa, fb, a, b, eps):
    if df(a) * d2f(a) > 0:
        x0, fx0 = b, fb
    else:
        x0, fx0 = a, fa
    n = 0
    while True:
        d = df(x0)
        if d == 0:
            return None, n
        x1 = x0 - fx0 / d
        n += 1
        if abs(x1 - x0) <= eps:
            return x1, n
        x0, fx0 = x1, f(x1)


METHODS = {
    "Метод бисекции": bisection_core,
    "Метод хорд": chord_core,
    "Метод касательных": tangent_core,
}


def measure_time(core, args, repeats):
    for _ in range(min(200, repeats)):
        core(*args)
    times = []
    gc_was_enabled = gc.isenabled()
    gc.disable()
    try:
        for _ in range(repeats):
            start = perf_counter_ns()
            core(*args)
            times.append(perf_counter_ns() - start)
    finally:
        if gc_was_enabled:
            gc.enable()
    return statistics.median(times) / 1000


def true_root(function, a, b, digits=25):
    x = sympy.symbols('x')
    g = sympy.lambdify(x, function, "mpmath")
    with mpmath.workdps(digits + 10):
        lo, hi = mpmath.mpf(a), mpmath.mpf(b)
        g_lo = g(lo)
        for _ in range(int(digits * 3.4) + 10):
            mid = (lo + hi) / 2
            g_mid = g(mid)
            if g_mid == 0:
                return mpmath.nstr(mid, digits, min_fixed=-10**6, max_fixed=10**6)
            if g_lo * g_mid < 0:
                hi = mid
            else:
                lo, g_lo = mid, g_mid
        return mpmath.nstr((lo + hi) / 2, digits, min_fixed=-10**6, max_fixed=10**6)


def highlight(exact, root):
    shown = format(Decimal(repr(root)), "f")
    k = 0
    while k < len(exact) and k < len(shown) and exact[k] == shown[k]:
        k += 1
    if k == 0:
        return exact
    return f"[bold {GREEN}]{exact[:k]}[/bold {GREEN}]{exact[k:]}"


def compare(function, a, b, eps, repeats):
    x = sympy.symbols('x')
    f = sympy.lambdify(x, function, "math")
    df = sympy.lambdify(x, sympy.diff(function, x), "math")
    d2f = sympy.lambdify(x, sympy.diff(function, x, 2), "math")

    fa, fb = f(a), f(b)
    if fa * fb >= 0:
        show_error("На заданном отрезке не обнаружена смена знака функции.")
        return

    exact = true_root(function, a, b)

    table = Table(
        title=f"Сравнение методов, ε = {eps}, {escape(f'[{a}; {b}]')}",
        title_style=f"bold {MAUVE}",
        border_style=MAUVE,
        header_style=f"bold {BLUE}",
        box=box.ROUNDED,
        padding=(0, 2),
    )
    columns = (
        ("Название метода", f"bold {TEXT}"),
        ("Итераций", TEXT),
        ("Время, мкс", TEXT),
        ("Корень", TEXT),
        ("Истинный корень", f"bold {PEACH}"),
    )
    for title, style in columns:
        table.add_column(title, justify="center", style=style)

    for name, core in METHODS.items():
        args = (f, df, d2f, fa, fb, a, b, eps)
        root, n = core(*args)
        if root is None:
            table.add_row(name, str(n), "-", f"[bold {RED}]ошибка[/bold {RED}]", exact)
            continue
        t = measure_time(core, args, repeats)
        table.add_row(name, str(n), f"{t}", f"{root}", highlight(exact, root))
    console.print()
    console.print(table)