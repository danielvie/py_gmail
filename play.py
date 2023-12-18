from rich.console import Console
from pynput import keyboard
import os

class TerminalApp:
    def __init__(self):
        self.console = Console()
        self.highlighted_line = 2
        self.items = []
        self.init_items()
    
    def init_items(self):
        self.items.append([0, 'line 0'])
        self.items.append([0, 'line 1'])
        self.items.append([0, 'line 2'])
        self.items.append([0, 'line 3'])
        self.items.append([0, 'line 4'])
        self.items.append([0, 'line 5'])
        self.items.append([0, 'line 6'])
        self.items.append([0, 'line 7'])
        self.items.append([0, 'line 8'])
        self.items.append([0, 'line 9'])
        self.items.append([0, 'line 10'])
        self.items.append([0, 'line 11'])
        self.update_idx()
    
    def update_idx(self):
        for i,item in enumerate(self.items):
            item[0] = i

    def display_lines(self):
        self.console.clear()
        for i,v in self.items:
            if i == self.highlighted_line:
                self.console.print(f'[red]xxx[/red]', end=' ')
                self.console.print(v, style="bold red")
            else:
                self.console.print(v)

    def remove_item(self, idx):
        self.items.pop(idx)
        self.update_idx()
        if idx == len(self.items):
            self.highlighted_line -= 1

    def on_key_release(self, key):
        try:
            os.system('clear' if os.name == 'posix' else 'cls')  # Clear the terminal screen

            if key.char == "j":
                self.highlighted_line = min(self.highlighted_line + 1, len(self.items) - 1)
            elif key.char == "k":
                self.highlighted_line = max(self.highlighted_line - 1, 0)
            elif key.char == "x":
                self.remove_item(self.highlighted_line)
            elif key.char == "q":
                return False  # Stop the listener

            # Display lines after key press
            self.display_lines()
        except AttributeError:
            pass  # Handle non-character key events

    def run(self):
        # Display initial lines
        self.display_lines()

        with keyboard.Listener(on_release=self.on_key_release, suppress=True) as listener:
            listener.join()

if __name__ == "__main__":
    app = TerminalApp()
    app.run()
