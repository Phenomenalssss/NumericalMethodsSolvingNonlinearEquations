import math
import sympy
from rich import box
from rich.align import Align
from rich.console import Group
from rich.markup import escape
from rich.panel import Panel
from rich.prompt import Prompt, FloatPrompt, IntPrompt
from rich.table import Table
from rich.text import Text
from methods.bisection import bisection
from methods.chord import chord
from methods.tangent import tangent
from methods.compare import compare
from theme import (
    BLUE, GREEN, MAUVE, MUTED, PEACH, RED, SUBTEXT, TEXT, YELLOW,
    console, prompt, show_error, show_result,
)

Prompt.prompt_suffix = ""
FloatPrompt.prompt_suffix = ""
IntPrompt.prompt_suffix = ""
IntPrompt.validate_error_message = f"[bold {RED}]Ошибка:[/bold {RED}] [{TEXT}]введите целое число.[/{TEXT}]"
FloatPrompt.validate_error_message = f"[bold {RED}]Ошибка:[/bold {RED}] [{TEXT}]введите число (дробную часть отделяйте точкой).[/{TEXT}]"
x = sympy.symbols('x')


def build_menu():
    items = (
        ("1", "Метод бисекции", BLUE),
        ("2", "Метод хорд", BLUE),
        ("3", "Метод касательных", BLUE),
        ("4", "Сравнительный анализ методов", BLUE),
        (None, None, None),
        ("5", "Подсказка", YELLOW),
        ("6", "Выход", MUTED),
    )
    grid = Table.grid(padding=(0, 2))
    grid.add_column(justify="right")
    grid.add_column(justify="left")
    for number, name, color in items:
        if number is None:
            grid.add_row("", "")
        else:
            grid.add_row(f"[bold {color}]{number}[/bold {color}]", f"[bold {TEXT}]{name}[/bold {TEXT}]")
    return Panel.fit(
        Group(
            Text.from_markup(f"[{SUBTEXT}]Поиск корней нелинейных уравнений с заданной точностью[/{SUBTEXT}]", justify="center"),
            Text(""),
            Align.center(grid),
        ),
        title=f"[bold {MAUVE}] Численные методы [/bold {MAUVE}]",
        border_style=MAUVE,
        box=box.ROUNDED,
        padding=(1, 4),
    )


def build_help():
    interval = escape("[a, b]")
    text = (
        f"[bold {BLUE}]1. Формат функции f(x):[/bold {BLUE}]\n"
        f"   [{MUTED}]•[/{MUTED}] Переменная должна быть обозначена как [bold {TEXT}]x[/bold {TEXT}].\n"
        f"   [{MUTED}]•[/{MUTED}] Степень: [bold {TEXT}]x^2[/bold {TEXT}] или [bold {TEXT}]x**2[/bold {TEXT}]\n"
        f"   [{MUTED}]•[/{MUTED}] Умножение пишется строго через звездочку: [bold {TEXT}]2*x[/bold {TEXT}] (не [strike]2x[/strike]).\n"
        f"   [{MUTED}]•[/{MUTED}] Математические функции: [bold {TEXT}]sin(x)[/bold {TEXT}], [bold {TEXT}]cos(x)[/bold {TEXT}], [bold {TEXT}]exp(x)[/bold {TEXT}], [bold {TEXT}]log(x)[/bold {TEXT}], [bold {TEXT}]sqrt(x)[/bold {TEXT}] и так далее.\n"
        f"   [{MUTED}]•[/{MUTED}] Правильно написанная функция: [bold {GREEN}]x^2 / (x^2 - 1) - ln(x)[/bold {GREEN}]\n\n"
        f"[bold {BLUE}]2. Границы отрезка {interval}:[/bold {BLUE}]\n"
        f"   [{MUTED}]•[/{MUTED}] Вводите числа (целые или с плавающей точкой через точку, например: [bold {TEXT}]-1.5[/bold {TEXT}]).\n"
        f"   [{MUTED}]•[/{MUTED}] Функция должна менять знак на концах отрезка: [bold {TEXT}]f(a) * f(b) < 0[/bold {TEXT}].\n\n"
        f"[bold {BLUE}]3. Точность ε:[/bold {BLUE}]\n"
        f"   [{MUTED}]•[/{MUTED}] Положительное малое число, например: [bold {TEXT}]0.001[/bold {TEXT}] или [bold {TEXT}]1e-3[/bold {TEXT}]."
    )
    return Panel.fit(
        text,
        title=f"[bold {PEACH}] Как правильно вводить данные [/bold {PEACH}]",
        border_style=PEACH,
        box=box.ROUNDED,
        padding=(1, 3),
    )


def ask_method():
    while True:
        method = IntPrompt.ask(prompt(f"Выберите [bold {BLUE}]метод[/bold {BLUE}], [bold {YELLOW}]подсказку[/bold {YELLOW}] или [bold {MUTED}]выход[/bold {MUTED}], введя цифру ="))
        if 1 <= method <= 6:
            return method
        show_error("Неверный метод. Попробуйте снова.")


def ask_function():
    while True:
        text = Prompt.ask(prompt(f"Введите [bold {BLUE}]функцию f(x)[/bold {BLUE}] ="))
        try:
            function = sympy.sympify(text.replace("^", "**").lower())
        except Exception:
            show_error("Не удалось распознать функцию. Формат ввода описан в подсказке (пункт 5).")
            continue
        if not isinstance(function, sympy.Expr):
            show_error("Введите выражение, зависящее от x.")
            continue
        symbols = function.free_symbols
        if not symbols:
            show_error("Функция должна содержать переменную x.")
            continue
        if symbols != {x}:
            show_error("В функции допустима только переменная x.")
            continue
        return function


def ask_interval(function):
    f = sympy.lambdify(x, function, "math")
    while True:
        a = FloatPrompt.ask(prompt(f"Введите левую границу [bold {BLUE}]a[/bold {BLUE}] ="))
        while True:
            b = FloatPrompt.ask(prompt(f"Введите правую границу [bold {BLUE}]b[/bold {BLUE}] ="))
            if b > a:
                break
            show_error("Правая граница b должна быть больше левой границы a.")
        try:
            fa, fb = f(a), f(b)
            if not (math.isfinite(fa) and math.isfinite(fb)):
                raise ValueError
        except Exception:
            show_error("Функция не определена в одной из границ отрезка. Введите границы заново.")
            continue
        if fa * fb >= 0:
            show_error("На заданном отрезке не обнаружена смена знака функции. Введите границы заново.")
            continue
        return a, b


def ask_eps():
    while True:
        eps = FloatPrompt.ask(prompt(f"Введите точность [bold {BLUE}]ε[/bold {BLUE}] ="))
        if not (math.isfinite(eps) and eps > 0):
            show_error("Точность ε должна быть положительным числом.")
            continue
        return eps


def ask_repeats():
    while True:
        repeats = IntPrompt.ask(prompt(f"Введите [bold {BLUE}]количество повторов[/bold {BLUE}] для замера времени ="))
        if repeats >= 1:
            return repeats
        show_error("Количество повторов должно быть положительным.")


while True:
    console.print(build_menu())
    console.print()
    method = ask_method()
    if method == 5:
        console.print()
        console.print(build_help())
        console.print()
        continue
    if method == 6:
        console.print(f"[bold {MAUVE}]Программа завершена.[/bold {MAUVE}]")
        break
    function = ask_function()
    a, b = ask_interval(function)
    eps = ask_eps()
    if method == 4:
        repeats = ask_repeats()
    try:
        if method == 4:
            compare(function, a, b, eps, repeats)
            console.print()
            continue
        if method == 1:
            root = bisection(function, a, b, eps)
            text_method = "Метод бисекции"
        elif method == 2:
            root = chord(function, a, b, eps)
            text_method = "Метод хорд"
        else:
            root = tangent(function, a, b, eps)
            text_method = "Метод касательных"

        if root is not None:
            show_result(text_method, function, a, b, eps, root)
    except Exception as e:
        show_error(e)