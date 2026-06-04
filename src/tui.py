import curses
import os
from src.scrubber import Scrubber

class ManualGateTUI:
    def __init__(self, case_id, file_path):
        self.case_id = case_id
        self.file_path = file_path
        self.raw_dir = os.path.join("data", "raw", case_id)
        self.config_path = os.path.join(self.raw_dir, "proprietary_terms.txt")
        self.proprietary_terms = self._load_terms()
        self.scrubber = Scrubber()
        self.content = self._load_content()
        self.scrubbed_lines = []
        self.cursor_y = 0
        self.cursor_x = 0
        self.top_line = 0
        self.selection_start = None

    def _load_terms(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                return [line.strip() for line in f if line.strip()]
        return []

    def _save_terms(self):
        os.makedirs(self.raw_dir, exist_ok=True)
        with open(self.config_path, "w") as f:
            for term in sorted(set(self.proprietary_terms)):
                f.write(f"{term}\n")

    def _load_content(self):
        try:
            with open(self.file_path, "r", errors='replace') as f:
                return f.readlines()
        except Exception as e:
            return [f"Error loading file: {e}"]

    def _update_scrubbed_lines(self):
        self.scrubbed_lines = [self.scrubber.scrub(line, self.proprietary_terms) for line in self.content]

    def run(self, stdscr):
        curses.curs_set(1) # Show cursor for selection
        stdscr.nodelay(False)
        stdscr.use_default_colors()

        while True:
            self._update_scrubbed_lines()
            self._draw(stdscr)

            key = stdscr.getch()

            if key == ord('q'):
                break
            # Navigation
            elif key == ord('j') or key == curses.KEY_DOWN:
                if self.cursor_y < len(self.scrubbed_lines) - 1:
                    self.cursor_y += 1
            elif key == ord('k') or key == curses.KEY_UP:
                if self.cursor_y > 0:
                    self.cursor_y -= 1
            elif key == ord('h') or key == curses.KEY_LEFT:
                if self.cursor_x > 0:
                    self.cursor_x -= 1
            elif key == ord('l') or key == curses.KEY_RIGHT:
                line_len = len(self.scrubbed_lines[self.cursor_y].rstrip())
                if self.cursor_x < line_len:
                    self.cursor_x += 1

            # Selection
            elif key == ord('v'): # Start/stop selection
                if self.selection_start is None:
                    self.selection_start = self.cursor_x
                else:
                    self.selection_start = None

            elif key == ord('y'): # "Yank" selection as proprietary term
                if self.selection_start is not None:
                    start = min(self.selection_start, self.cursor_x)
                    end = max(self.selection_start, self.cursor_x) + 1
                    # Note: We need to be careful because we are selecting from the SCRUBBED line
                    # but maybe we should select from the ORIGINAL line?
                    # Usually, proprietary terms are NOT yet scrubbed, so they are visible.
                    # Let's assume the user selects from the scrubbed view.
                    line = self.scrubbed_lines[self.cursor_y]
                    term = line[start:end].strip()
                    if term:
                        self.proprietary_terms.append(term)
                        self._save_terms()
                        self.selection_start = None

            elif key == ord('a'):
                term = self._get_input(stdscr, "Add proprietary term: ")
                if term:
                    self.proprietary_terms.append(term)
                    self._save_terms()

            # Adjust view window
            height, width = stdscr.getmaxyx()
            if self.cursor_y < self.top_line:
                self.top_line = self.cursor_y
            elif self.cursor_y >= self.top_line + height - 2:
                self.top_line = self.cursor_y - (height - 3)

    def _draw(self, stdscr):
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # Header
        header = f" Case: {self.case_id} | File: {os.path.basename(self.file_path)} | terms: {len(self.proprietary_terms)} "
        stdscr.addstr(0, 0, header[:width], curses.A_REVERSE)

        # Content
        for i in range(height - 2):
            line_idx = self.top_line + i
            if line_idx < len(self.scrubbed_lines):
                line = self.scrubbed_lines[line_idx].rstrip()

                if line_idx == self.cursor_y:
                    # Draw line with potential selection
                    for x, char in enumerate(line[:width-1]):
                        attr = curses.A_NORMAL
                        if self.selection_start is not None:
                            start = min(self.selection_start, self.cursor_x)
                            end = max(self.selection_start, self.cursor_x)
                            if start <= x <= end:
                                attr = curses.A_REVERSE
                        elif x == self.cursor_x:
                            # Highlight cursor position if no selection
                            attr = curses.A_UNDERLINE

                        try:
                            stdscr.addch(i + 1, x, char, attr)
                        except curses.error:
                            pass
                else:
                    try:
                        stdscr.addstr(i + 1, 0, line[:width-1], curses.A_NORMAL)
                    except curses.error:
                        pass

        # Footer
        footer = " [h/j/k/l] Move | [v] Select | [y] Yank Term | [a] Add | [q] Quit "
        stdscr.addstr(height - 1, 0, footer[:width], curses.A_REVERSE)

        # Move actual cursor to cursor_x, cursor_y (relative to screen)
        try:
            stdscr.move(self.cursor_y - self.top_line + 1, self.cursor_x)
        except curses.error:
            pass

        stdscr.refresh()

    def _get_input(self, stdscr, prompt):
        height, width = stdscr.getmaxyx()
        stdscr.addstr(height - 1, 0, " " * (width - 1))
        stdscr.addstr(height - 1, 0, prompt)
        curses.echo()
        input_str = stdscr.getstr(height - 1, len(prompt), 60).decode('utf-8')
        curses.noecho()
        return input_str.strip()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        tui = ManualGateTUI("test_case", sys.argv[1])
        curses.wrapper(tui.run)
    else:
        print("Usage: python3 src/tui.py <file_path>")
