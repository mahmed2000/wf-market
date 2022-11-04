import curses
import curses.textpad
import curses.ascii

class GUI():
    def __init__(self, root, h, w, y, x):
        self.root = root
        self.window = root.subwin(h, w, y, x)

    def create_gui(self):
        self.create_search_bar()
        self.create_search_results()
    
    def create_search_bar(self):
        self.search_box = self.window.subwin(3, self.root.getmaxyx()[1], 0, 0)
        self.search_box.border()
        self.search_bar = self.window.subwin(1, self.root.getmaxyx()[1] - 2, 1, 1)
        self.search_in = curses.textpad.Textbox(self.search_bar)

    def create_search_results(self):
        self.results_box = self.window.subwin(self.root.getmaxyx()[0] - 3, self.root.getmaxyx()[1] // 3, 3, 0)
        self.results_box.border()

        

class App():
    def __init__(self, root):
        self.root = root
        self.gui = GUI(self.root, *self.root.getmaxyx(), 0, 0)

    def show_gui(self):
        self.root.clear()
        self.gui.create_gui()

def main(w):
    app = App(w)
    app.show_gui()
    w.refresh()
    app.gui.search_in.edit()
    search_string = app.gui.search_in.gather()
    app.gui.results_box.addstr(1, 1, search_string)
    app.gui.results_box.refresh()
    w.getch()
    return search_string

print(curses.wrapper(main))
