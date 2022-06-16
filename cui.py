import curses
import logging
from classnamespace import ClassNamespace

def _wrap_line(line, cols):
    return [line[i:i + cols] for i in range(0, len(line), cols)]

def wrap_str(paragraph, cols):
    lines = []
    for line in paragraph.splitlines():
        if not line:
            wrapped_lines = [""]
        else:
            wrapped_lines = _wrap_line(line, cols)
        lines.extend(wrapped_lines)
    if paragraph and paragraph[-1] == "\n":
        lines.append("")
    return lines

def wrap_str2(paragraph, cols):
    last_index = 0
    lines = []
    for i, char in enumerate(paragraph):
        str_len = i - last_index
        assert str_len <= cols
        if char == "\n" or str_len == cols:
            line = paragraph[last_index:i]
            lines.append(line)
            last_index = i
    #last_line = paragraph
    return lines

def run_app(stdscr):
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)

    entry = ""

    rows, cols = stdscr.getmaxyx()

    cursor_pos = ClassNamespace()
    cursor_pos.x = 0
    cursor_pos.y = 0

    while True:
        # Clear screen
        stdscr.clear()

        # This raises ZeroDivisionError when i == 10.
        for i in range(0, 10):
            stdscr.addstr(i, 0, f"10 divided by {i}")

        rows, cols = stdscr.getmaxyx()
        stdscr.addstr(15, 5, f"{rows} {cols}")

        blank_line = " " * cols
        # This is actually recommended by the docs since python-curses
        # is such a crusty piece of shit
        #try:
        #    stdscr.addstr(rows - 1, 0, blank_line, curses.color_pair(1))
        #except curses.error:
        #    pass

        lines = wrap_str(entry, cols)
        if not lines:
            lines = [""]
        n = len(lines)
        try:
            for i, line in enumerate(lines):
                y = rows - (n - i)
                # Pad it with spaces so entire line is colored
                line += " " * (cols - len(line))
                stdscr.addstr(y, 0, line, curses.color_pair(1))
        except curses.error:
            pass

        logging.info(f"cursor pos: ({cursor_pos.x}, {cursor_pos.y}), n: {n}")
        cursor_screen_y = rows - n + cursor_pos.y
        stdscr.move(cursor_screen_y, cursor_pos.x)
        stdscr.refresh()
        charcode = stdscr.getch()
        if charcode == curses.KEY_LEFT:
            if cursor_pos.x > 0:
                cursor_pos.x -= 1
        elif charcode == curses.KEY_RIGHT:
            if cursor_pos.x < cols - 1:
                cursor_pos.x += 1
        elif charcode == curses.KEY_UP:
            if cursor_pos.y > 0:
                cursor_pos.y -= 1
        elif charcode == curses.KEY_DOWN:
            if cursor_pos.y < n - 1:
                cursor_pos.y += 1
        elif charcode == curses.KEY_BACKSPACE:
            entry = delet_entry_char(entry, cursor_pos, cols, -1)
            if cursor_pos.x > 0:
                cursor_pos.x -= 1
            elif cursor_pos.y > 0:
                cursor_pos.x = len(lines[cursor_pos.y])
                cursor_pos.y -= 1
        elif charcode == curses.KEY_HOME:
            cursor_pos.x = 0
        elif charcode == curses.KEY_END:
            cursor_pos.x = len(lines[cursor_pos.y])
        elif charcode == curses.KEY_DC:
            entry = delet_entry_char(entry, cursor_pos, cols, 1)
        else:
            logging.info(f"current line: {lines[cursor_pos.y]}")
            char = chr(charcode)
            entry = edit_entry(entry, cursor_pos, cols, char)
            if charcode == ord("\n"):
                cursor_pos.y += 1
                cursor_pos.x = 0
            else:
                cursor_pos.x += 1

def main(stdscr):
    logging.basicConfig(filename="/tmp/foo.log",
                        filemode='a',
                        format='%(levelname)s %(message)s',
                        level=logging.DEBUG)
    try:
        run_app(stdscr)
    except KeyboardInterrupt:
        pass

# This function takes a multilined string and edits it
def edit_entry(entry, cursor, cols, char):
    lines = wrap_str(entry, cols)
    if not lines:
        return char
    # index within the multilined entry
    idx = 0
    for line_number, line in enumerate(lines):
        if line_number == cursor.y:
            add_text = ""
            x_idx = cursor.x
            if cursor.x > len(line):
                # add blank spaces
                add_text += " " * (cursor.x - len(line))
                x_idx = len(line)
            add_text += char
            idx += x_idx
            before, after = entry[:idx], entry[idx:]
            entry = before + add_text + after
            return entry

        # Advance idx to the next line in entry
        idx += len(line) + 1

# Delete single character from multilined entry string
def delet_entry_char(entry, cursor, cols, direction):
    lines = wrap_str(entry, cols)
    if not lines:
        return char
    # index within the multilined entry
    idx = 0
    for line_number, line in enumerate(lines):
        if line_number == cursor.y:
            add_text = ""
            if cursor.x > len(line):
                # do nothing
                return entry
            x_idx = cursor.x
            idx += x_idx
            if direction == -1:
                idx -= 1
            before, after = entry[:idx], entry[idx + 1:]
            entry = before + after
            return entry

        # Advance idx to the next line in entry
        idx += len(line) + 1

# Testing code
#entry = """foo
#"""
#cursor = ClassNamespace()
#cursor.x = 1
#cursor.y = 1
#print(edit_entry(entry, cursor, 80, "a"))

curses.wrapper(main)

