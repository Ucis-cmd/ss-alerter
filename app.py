import requests
from bs4 import BeautifulSoup
import threading
import tkinter as tk
from email.message import EmailMessage
import smtplib

# should return all the listings that are above the last newest listing, instead of only the most newest.

SEARCH_INTERVAL = (
    300  # inbox allows only 15 msgs/hour, so every five minutes should be fine
)
GAP = 5
TO_EMAIL = "jkunsooo@gmail.com"
FROM_EMAIL = "drillis@inbox.lv"
FROM_EMAIL_PASSWORD = "5BN5iyT3oE"
newest_item = None


def init_newest_item(link):
    global newest_item
    newest_item = get_first_item(link)


def get_first_item(link):
    r = requests.get(link)
    soup = BeautifulSoup(r.content, "html.parser")

    # Locate the first item in the list
    filter_element = soup.find("div", class_="filter_second_line_dv")
    table = filter_element.find_next_sibling("table")
    header_row = table.find("tr", id="head_line")
    first_item = header_row.find_next_sibling("tr")

    return first_item


def get_data_from_item(item):
    children = item.find_all("td")
    description = children[2].text
    other_data = [item.text for item in children[3:]]
    return description, other_data


def send_email(content):
    msg = EmailMessage()
    msg.set_content(content)
    msg["Subject"] = f"Auto"
    msg["From"] = FROM_EMAIL
    msg["To"] = TO_EMAIL
    try:
        with smtplib.SMTP(
            "mail.inbox.lv", 587
        ) as s:  # make the smtp server changeable, or add to the top of file
            s.starttls()  # Upgrade the connection to secure
            s.login(FROM_EMAIL, FROM_EMAIL_PASSWORD)
            s.send_message(msg)
            print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


def get_items_since_last_newest(link):
    # get the first item, then the next, then the next, etc., until get to last next
    first_item = get_first_item(link)

    if first_item == newest_item:
        print("nope")
        return

    next_item = first_item.find_next_sibling("tr")
    item_curr = first_item
    items_since_newest = [item_curr]

    while next_item.get("id") != newest_item.get("id"):
        item_curr = next_item
        print(item_curr.get("id"))
        items_since_newest.append(item_curr)
        next_item = item_curr.find_next_sibling("tr")
    print(f"Items since newest ({newest_item.get('id')}):", items_since_newest)


def convert_to_email_text(description, data):
    separator = ", "
    text_of_data = separator.join(item for item in data)
    text = f"Description: {description}, data: {text_of_data}"
    return text


def get_newest_item(link):
    global newest_item
    first_item = get_first_item(link)

    # Check if the newest item has changed
    if newest_item != first_item:
        newest_item = first_item
        description, other_data = get_data_from_item(first_item)
        send_email(convert_to_email_text(description, other_data))
        print(f"New item: {newest_item}")


def loop_function(get_newest_item, get_items_since_last_newest, link, f_stop, interval):
    if not f_stop.is_set():
        get_items_since_last_newest(link)
        get_newest_item(link)
        # Start the looping of function
        threading.Timer(
            interval,
            loop_function,
            [get_newest_item, get_items_since_last_newest, link, f_stop, interval],
        ).start()


def start_loop():
    global f_stop
    link = link_entry.get()
    init_newest_item(link)
    if not f_stop.is_set():
        f_stop.clear()
        loop_function(
            get_newest_item,
            get_items_since_last_newest,
            link,
            f_stop,
            interval=SEARCH_INTERVAL,
        )
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

inner_frame = tk.Frame(root)
inner_frame.pack(fill="both", expand=True, padx=20, pady=20)

f_stop = threading.Event()

link_label = tk.Label(inner_frame, text="Link:")
link_label.grid(row=0, column=0, sticky="W", pady=2)

link_entry = tk.Entry(inner_frame, width=50)
link_entry.grid(row=0, column=1, columnspan=2, ipadx=20, ipady=10, pady=GAP)

start_button = tk.Button(inner_frame, text="Start", command=start_loop)
start_button.grid(row=1, column=1, columnspan=3, ipadx=10, ipady=5, pady=GAP)

stop_button = tk.Button(inner_frame, text="Stop", command=stop_loop, state=tk.DISABLED)
stop_button.grid(row=2, column=1, columnspan=3, ipadx=10, ipady=5, pady=GAP)

root.mainloop()
