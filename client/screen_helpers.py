import curses
from curses.textpad import Textbox, rectangle


def print_to_pad(screen, msg):
    screen["screen"].addstr(f"{msg}\n")
    screen["screen"].refresh(
        0, 0, 0, 0, screen["rows"], screen["cols"],
    )


def print_to_screen(screen, msg):
    screen.addstr(f"{msg}\n")
    screen.refresh()


def setup_screen():
    curses.initscr()
    y_offset = int(curses.LINES * 0.9)
    y_input = curses.LINES - y_offset

    output_screen = curses.newpad(y_offset, curses.COLS)
    output_screen.scrollok(True)
    input_screen = curses.newwin(y_input, curses.COLS, y_offset, 0)

    screens = {
        "out": {
            "screen": output_screen,
            "rows": y_offset,
            "cols": curses.COLS,
            "printer": lambda s: print_to_pad(screens["out"], s),
        },
        "in": {
            "screen": input_screen,
            "rows": y_input,
            "cols": curses.COLS,
            "printer": lambda s: print_to_screen(input_screen, s),
        },
    }
    return screens


def gather_input(box):
    value = box["screen"].getstr().decode("utf-8")
    box["screen"].erase()
    return value


def refresh_all(screen):
    screen["out"]["screen"].refresh(
        0, 0, 0, 0, screen["out"]["rows"], screen["out"]["cols"]
    )
    screen["in"]["screen"].refresh()

def quit_screen():
    curses.endwin()
