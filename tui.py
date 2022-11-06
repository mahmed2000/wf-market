import curses
import curses.textpad
import curses.ascii

from api import Session

class GUI():
    def __init__(self, root, h, w, y, x):
        self.root = root
        self.window = root.subwin(h, w, y, x)

    def create_gui(self):
        self.create_search_bar()
        self.create_item_search_results()
    
    def create_search_bar(self):
        self.search_box = self.window.subwin(3, self.window.getmaxyx()[1], 0, 0)
        self.search_box.border()
        self.search_bar = self.window.subwin(1, self.window.getmaxyx()[1] - 2, 1, 1)
        self.search_in = curses.textpad.Textbox(self.search_bar)

    def create_item_search_results(self):
        self.results_box = self.window.subwin(self.window.getmaxyx()[0] - 3, self.window.getmaxyx()[1] // 3, 3, 0)
        self.results_box.border()


class App():
    def __init__(self, root):
        self.root = root
        self.gui = GUI(self.root, *self.root.getmaxyx(), 0, 0)
        self.client = Session()

    def show_gui(self):
        self.root.clear()
        self.gui.create_gui()

    def update_item_search_results(self):
        search_str = self.gui.search_in.gather()
        items = self.client.api_request(url = '/items').get('payload').get('items')
        items = [item for item in items if search_str.strip().lower() in item.get('item_name').lower()][:self.gui.results_box.getmaxyx()[0] - 2]
        self.gui.results_box.clear()
        self.gui.results_box.border()
        for i in range(len(items)):
            try:
                self.gui.results_box.addstr(i + 1, 1, items[i]['item_name'][:self.gui.results_box.getmaxyx()[1] - 2])
            except:
                pass
        self.gui.results_box.refresh()



def main(w):
    app = App(w)
    app.show_gui()
    w.refresh()
    app.gui.search_in.edit()
    app.update_item_search_results()
    w.getch()

curses.wrapper(main)
