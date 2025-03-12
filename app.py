import requests
from bs4 import BeautifulSoup
import threading
import tkinter as tk
from email.message import EmailMessage
import smtplib

# add links to listings

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


def get_header_row(link):
    r = requests.get(link)
    soup = BeautifulSoup(r.content, "html.parser")

    # Locate the first item in the list
    filter_element = soup.find("div", class_="filter_second_line_dv")
    table = filter_element.find_next_sibling("table")
    header_row = table.find("tr", id="head_line")
    return header_row


def get_first_item(link):
    header_row = get_header_row(link)
    first_item = header_row.find_next_sibling("tr")

    return first_item


def get_data_from_item(item):
    children = item.find_all("td")
    description = children[2].text
    other_data = [item.text for item in children[3:]]
    return {"description": description, "other_data": other_data}


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
    header_row = get_header_row(link)
    items = header_row.find_next_siblings("tr")
    if items[0] == newest_item:
        print("No new items found")
        return
    try:
        newest_item_index = [item.get("id") for item in items].index(
            newest_item.get("id")
        )
    except ValueError:
        # If newest_item is not found, return all items
        newest_item_index = len(items)

    # Return all items since the newest_item
    items_since_newest = items[:newest_item_index]
    items_since_newest_data = [get_data_from_item(item) for item in items_since_newest]
    send_email(convert_to_email_text(items_since_newest_data))

    print(
        f"Items since newest ({newest_item.get('id')}):",
        convert_to_email_text(items_since_newest_data),
    )


def convert_to_email_text(list_of_dicts):
    separator = ", "
    email_body = ""
    if not isinstance(list_of_dicts, list):
        list_of_dicts = [list_of_dicts]
    for dict in list_of_dicts:
        text_of_data = separator.join(item for item in dict["other_data"])
        email_body += f"Description: {dict['description']}, data: {text_of_data} \n\n"
    return email_body


def get_newest_item(link):
    global newest_item
    first_item = get_first_item(link)

    # Check if the newest item has changed
    if newest_item != first_item:
        newest_item = first_item
        # send_email(convert_to_email_text(get_data_from_item(first_item)))
        print(f"New item: {get_data_from_item(newest_item)}")


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
