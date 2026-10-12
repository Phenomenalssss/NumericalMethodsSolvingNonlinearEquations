from rich import box
from rich.align import Align
from rich.console import Console, Group
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

MAUVE = "#cba6f7"
BLUE = "#89b4fa"
SKY = "#89dceb"
GREEN = "#a6e3a1"
YELLOW = "#f9e2af"
PEACH = "#fab387"
RED = "#f38ba8"
TEXT = "#cdd6f4"
SUBTEXT = "#a6adc8"
MUTED = "#7f849c"

console = Console()


def prompt(message):
    return f"[bold {MAUVE}]›[/bold {MAUVE}] [{TEXT}]{message}[/{TEXT}] "


def info_grid(rows):
    grid = Table.grid(padding=(0, 1))
    grid.add_column(justify="right")
    grid.add_column(justify="left")
    for label, value in rows:
        grid.add_row(label, value)
    return grid


def show_error(message):
    console.print(Panel.fit(
        f"[{TEXT}]{escape(str(message))}[/{TEXT}]",
        title=f"[bold {RED}] Ошибка [/bold {RED}]",
        border_style=RED,
        box=box.ROUNDED,
        padding=(0, 2),
    ))
    console.print()


def show_start(x0, fx0):
    rows = [
        (f"[{BLUE}]x0[/{BLUE}] =", f"[bold {TEXT}]{x0}[/bold {TEXT}]"),
        (f"[{SUBTEXT}]F(x0)[/{SUBTEXT}] =", f"[bold {TEXT}]{fx0}[/bold {TEXT}]"),
    ]
    console.print()
    console.print(Panel(
        Align.center(info_grid(rows)),
        title=f"[bold {MAUVE}] Начальное приближение [/bold {MAUVE}]",
        border_style=MAUVE,
        box=box.ROUNDED,
        expand=False,
        padding=(0, 2),
    ))


def show_iteration(iteration, x, delta_x, eps, fx):
    converged = delta_x <= eps
    rows = [
        (f"[{BLUE}]x{iteration}[/{BLUE}] =", f"[bold {TEXT}]{x}[/bold {TEXT}]"),
        (f"[{BLUE}]Δx{iteration}[/{BLUE}] =", f"[bold {TEXT}]{delta_x}[/bold {TEXT}]"),
    ]
    if converged:
        color = GREEN
        border = GREEN
        verdict = f"[bold {GREEN}]Δx{iteration} ≤ ε ✓[/bold {GREEN}]"
    else:
        color = BLUE
        border = MUTED
        rows.append((f"[{SUBTEXT}]F(x{iteration})[/{SUBTEXT}] =", f"[bold {TEXT}]{fx}[/bold {TEXT}]"))
        verdict = f"[{MUTED}]Δx{iteration} > ε[/{MUTED}]"
    console.print()
    console.print(Panel(
        Group(
            Align.center(info_grid(rows)),
            Text.from_markup(verdict, justify="center"),
        ),
        title=f"[bold {color}] Итерация {iteration} [/bold {color}]",
        border_style=border,
        box=box.ROUNDED,
        expand=False,
        padding=(0, 2),
    ))


def show_result(method_name, function, a, b, eps, root):
    rows = [
        (f"[{SUBTEXT}]Функция[/{SUBTEXT}]", f"[{TEXT}]f(x) = {escape(str(function))}[/{TEXT}]"),
        (f"[{SUBTEXT}]Отрезок[/{SUBTEXT}]", f"[{TEXT}]{escape(f'[{a}; {b}]')}[/{TEXT}]"),
        (f"[{SUBTEXT}]Точность[/{SUBTEXT}]", f"[{TEXT}]ε = {eps}[/{TEXT}]"),
        (f"[{SUBTEXT}]Корень[/{SUBTEXT}]", f"[bold {GREEN}]r = {root}[/bold {GREEN}] [{SUBTEXT}]±[/{SUBTEXT}] [{TEXT}]{eps}[/{TEXT}]"),
    ]
    grid = Table.grid(padding=(0, 2))
    grid.add_column(justify="right")
    grid.add_column(justify="left")
    for label, value in rows:
        grid.add_row(label, value)
    console.print()
    console.print(Panel.fit(
        Align.center(grid),
        title=f"[bold {GREEN}] {method_name} [/bold {GREEN}]",
        border_style=GREEN,
        box=box.ROUNDED,
        padding=(1, 3),
    ))
    console.print()