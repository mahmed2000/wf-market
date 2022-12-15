import requests

import curses, curses.textpad
import subprocess, sys, json


class Session():
    def __init__(self):
        self.client = requests.Session()

    def api_request(self, url='/', method='get', **kwargs):
        return json.loads(getattr(self.client, method)('https://api.warframe.market/v1' + url, **kwargs).text)



class GUI():
    def __init__(self, root, h, w, y, x):
        self.root = root
        self.window = root.subwin(h, w, y, x)

    def create_gui(self):
        self.create_search_bar()
        self.create_item_search_results()
        self.create_order_search_results()
        self.root.refresh()
    
    def create_search_bar(self):
        self.search_box = self.window.subwin(3, self.window.getmaxyx()[1], 0, 0)
        self.search_box.border()
        self.search_bar = self.window.subwin(1, self.window.getmaxyx()[1] - 2, 1, 1)
        self.search_in = curses.textpad.Textbox(self.search_bar)

    def create_item_search_results(self):
        self.results_box = self.window.subwin(self.window.getmaxyx()[0] - 3, self.window.getmaxyx()[1] // 3, 3, 0)
        self.results_box.border()

    def create_order_search_results(self):
        self.orders_box = self.window.subwin(self.window.getmaxyx()[0] - 3, self.window.getmaxyx()[1] * 2 // 3, 3, self.window.getmaxyx()[1] // 3)
        self.orders_box.border()


class App():
    def __init__(self, root):
        self.root = root
        self.gui = GUI(self.root, *self.root.getmaxyx(), 0, 0)
        self.client = Session()
        self.item_list = self.client.api_request(url = '/items').get('payload').get('items')

    def show_gui(self):
        self.root.clear()
        self.gui.create_gui()

    def update_item_search_results(self):
        search_str = self.gui.search_in.gather()
        items = [item for item in self.item_list if search_str.strip().lower() in item.get('item_name').lower()][:self.gui.results_box.getmaxyx()[0] - 2]
        self.gui.results_box.clear()
        self.gui.results_box.border()
        for i in range(len(items)):
            try:
                self.gui.results_box.addstr(i + 1, 1, items[i]['item_name'][:self.gui.results_box.getmaxyx()[1] - 2])
            except:
                break
        self.gui.results_box.refresh()
        self.items = items

    def update_orders_results(self):
        orders = sorted(self.client.api_request(url = f'/items/{self.selected_item["url_name"]}/orders').get('payload').get('orders'), key=lambda x: x['platinum'])
        self.buy_orders = [order for order in orders if order['order_type'] == 'buy' and order['user']['status'] == 'ingame'][:self.gui.orders_box.getmaxyx()[0] - 2]
        self.buy_orders.reverse()
        self.sell_orders = [order for order in orders if order['order_type'] == 'sell' and order['user']['status'] == 'ingame'][:self.gui.orders_box.getmaxyx()[0] - 2]

        self.gui.orders_box.clear()
        self.gui.orders_box.border()
        for i in range(len(self.sell_orders)):
            try:
                self.gui.orders_box.addstr(i + 1, 1, '{:20.20} {: >3}p x{: <3} {: <10}'.format(self.sell_orders[i]['user']['ingame_name'], self.sell_orders[i]['platinum'], self.sell_orders[i]['quantity'], self.sell_orders[i].get('mod_rank', '')))
            except:
                break
        for i in range(len(self.buy_orders)):
            try:
                self.gui.orders_box.addstr(i + 1, self.gui.orders_box.getmaxyx()[1] // 2, '{:20.20} {: >3}p x{: <3} {: <10}'.format(self.buy_orders[i]['user']['ingame_name'], self.buy_orders[i]['platinum'], self.buy_orders[i]['quantity'], self.buy_orders[i].get('mod_rank', '')))
            except:
                break
        self.gui.orders_box.refresh()

    def decide_state(self):
        if self.state == 0:
            return self.search
        elif self.state == 1:
            return self.select_item
        elif self.state == 2:
            return self.select_order

    def run(self):
        self.show_gui()
        self.state = 0
        while True:
            self.decide_state()()


    def search(self):
        self.gui.search_in.edit()
        self.update_item_search_results()
        self.state = 1

    def select_item(self):
        self.gui.results_box.move(1, 1)
        self.gui.results_box.refresh()
        x = self.root.getch()
        while x != 10 and x != 115:
            if x == curses.KEY_UP:
                self.gui.results_box.move((self.gui.results_box.getyx()[0] - 1 - 1) % len(self.items) + 1, 1)
            elif x == curses.KEY_DOWN:
                self.gui.results_box.move((self.gui.results_box.getyx()[0] - 1 + 1) % len(self.items) + 1, 1)
            self.gui.results_box.refresh()
            x = self.root.getch()

        if x == 10:
            subprocess.run(f'echo \'{self.gui.results_box.getyx()}\' | xclip -sel c', shell = True)
            self.selected_item = self.items[self.gui.results_box.getyx()[0] - 1]
            self.update_orders_results()
            self.state = 2
        else:
            self.state = 0

    def select_order(self):
        self.gui.orders_box.move(1, 1)
        self.gui.orders_box.refresh()
        x = self.root.getch()
        col = 0
        while x != 10 and x != 115 and x != 105:
            if x == curses.KEY_UP:
                self.gui.orders_box.move((self.gui.orders_box.getyx()[0] - 1 - 1) % len(self.sell_orders if col == 0 else self.buy_orders) + 1, 1 if col == 0 else self.gui.orders_box.getmaxyx()[1] // 2)
            elif x == curses.KEY_DOWN:
                self.gui.orders_box.move((self.gui.orders_box.getyx()[0] - 1 + 1) % len(self.sell_orders if col == 0 else self.buy_orders) + 1, 1 if col == 0 else self.gui.orders_box.getmaxyx()[1] // 2)
            elif x == curses.KEY_LEFT or x == curses.KEY_RIGHT:
                col = int(not col)
                self.gui.orders_box.move(min(self.gui.orders_box.getyx()[0], len(self.buy_orders if col else self.sell_orders)), 1 if col == 0 else self.gui.orders_box.getmaxyx()[1] // 2)
            self.gui.orders_box.refresh()
            x = self.root.getch()

        if x == 10:
            self.selected_order = (self.buy_orders if col else self.sell_orders)[self.gui.orders_box.getyx()[0] - 1]
            self.copy_whisper()
        elif x == 115:
            self.state = 0
        else:
            self.state = 1

    def copy_whisper(self):
        whisper = f'\\w {self.selected_order["user"]["ingame_name"]} {"WTS" if self.selected_order["order_type"] == "buy" else "WTB"} {self.selected_item["item_name"]} listed for {self.selected_order["platinum"]}p on warframe.market'
        subprocess.run(f'echo \'{whisper}\' | xclip -sel c', shell = True)



def main(w):
    app = App(w)
    app.run()

try:
    curses.wrapper(main)
except KeyboardInterrupt:
    print('Exiting')
except requests.exceptions.ConnectionError:
    print("No Internet")
    sys.exit(1)
