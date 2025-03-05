import requests
from bs4 import BeautifulSoup
import threading
import tkinter as tk

SEARCH_INTERVAL = 2
newest_item = None


def get_newest_item():
    global newest_item
    r = requests.get("https://www.ss.com/lv/transport/cars/audi/")
    soup = BeautifulSoup(r.content, "html.parser")

    # Locate the first item in the list
    filter_element = soup.find("div", class_="filter_second_line_dv")
    table = filter_element.find_next_sibling("table")
    header_row = table.find("tr", id="head_line")
    first_item = header_row.find_next_sibling("tr")

    # Check if the newest item has changed
    if newest_item != first_item:
        newest_item = first_item
        print(f"New item: {newest_item}")


def loop_function(get_newest_item, f_stop, interval):
    if not f_stop.is_set():
        get_newest_item()
        # Start the looping of function
        threading.Timer(
            interval, loop_function, [get_newest_item, f_stop, interval]
        ).start()


def start_loop():
    global f_stop
    if not f_stop.is_set():
        f_stop.clear()
        loop_function(get_newest_item, f_stop, interval=SEARCH_INTERVAL)
        start_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.NORMAL)


def stop_loop():
    global f_stop
    f_stop.set()
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)


# Tkinter UI setup
root = tk.Tk()
root.title("Start/Stop Loop")

f_stop = threading.Event()

start_button = tk.Button(root, text="Start", command=start_loop)
start_button.pack(pady=10)

stop_button = tk.Button(root, text="Stop", command=stop_loop, state=tk.DISABLED)
stop_button.pack(pady=10)

root.mainloop()
