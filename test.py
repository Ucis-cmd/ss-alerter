import requests
from bs4 import BeautifulSoup
import threading
import tkinter as tk
from email.message import EmailMessage
import smtplib

newest_item = ''' 
<tr id="tr_55754084"><td class="msga2 pp0"><input id="c55754084" name="mid[]" type="checkbox" value="55754084_2383_0"/></td><td class="msga2"><a href="/msg/lv/transport/cars/bmw/318/bockn.html" id="im55754084"><img alt="" class="isfoto foto_list" src="https://i.ss.com/gallery/7/1300/324893/64978590.th2.jpg"/></a></td><td class="msg2"><div class="d1"><a class="am" data="eSU5QiU5NCVBNCVBNSU4RiVCRiU5QyU5OSU5RSVBRSU5MnQlOUUlOTMlQTElQUUlOEIlN0IlOUYlOTIlOUMlQTUlOEFz|CkbkuZ" href="/msg/lv/transport/cars/bmw/318/bockn.html" id="dm_55754084">BMW 318d-E91/ 2.0d/ 105kW(143zs)
Facelift modelis
</a></div></td><td c="1" class="msga2-o pp6" nowrap="">318</td><td c="1" class="msga2-o pp6" nowrap="">2012</td><td c="1" class="msga2-o pp6" nowrap="">2.0D</td><td c="1" class="msga2-r pp6" nowrap="">252 tūkst.</td><td c="1" class="msga2-o pp6" nowrap="">5,790  €</td></tr>
'''

def get_items_after_newest(link):
    #get the first item, then the next, then the next, etc., until get to last next
    r = requests.get(link)
    soup = BeautifulSoup(r.content, "html.parser")

    # Locate the first item in the list
    filter_element = soup.find("div", class_="filter_second_line_dv")
    table = filter_element.find_next_sibling("table")
    header_row = table.find("tr", id="head_line")
    first_item = header_row.find_next_sibling("tr")
    
    next_item = first_item.find_next_sibling("tr")
    item_curr = first_item
    items_since_newest = [item_curr]
    while next_item.get("id") != "tr_56092797":
        item_curr = next_item
        print(item_curr.get("id"))
        items_since_newest.append(item_curr)
        next_item = item_curr.find_next_sibling("tr")
    print(items_since_newest)

get_items_after_newest("https://www.ss.com/lv/transport/cars/bmw/")