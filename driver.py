import smtplib
import ssl
import sys
from collections import defaultdict
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
from bs4 import BeautifulSoup

import dump

oos_strings = {"not available", "check stores", "sold out", "see all buying options"}
header = {'User-Agent': 'Chrome/57.0.2987.110 '}
headerbb = {'User-Agent':   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                            'AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/76.0.3809.132 Safari/537.36'}
headergs = {'User-Agent':   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) '
                            'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.4 '
                            'Safari/605.1.15'}
stock_informer = ["https://www.stockinformer.com/checker-nintendo-switch-console"]
retailer_list = []
product_list = []
status_list = []
found = defaultdict(list)

# Email stuff
port = 465  # For SSL
password = input("Type your password and press enter: ")
conf_password = input("Confirm password: ")
if password != conf_password:
    print("Passwords not equal, ending program...")
    sys.exit()


def get_status(address, tag, attr, value, headers=False):
    # Clear out global lists
    retailer_list.clear()
    product_list.clear()
    status_list.clear()
    found.clear()

    if headers:
        # use specific header for bestbuy
        if "bestbuy" in address:
            get_request = requests.get(address, headers=headerbb).text
        elif "gamestop" in address:
            get_request = requests.get(address, headers=dump.headergs).text
        else:
            get_request = requests.get(address, headers=header).text
    else:
        get_request = requests.get(address).text
    doc = BeautifulSoup(get_request, 'html.parser')
    # print(doc.prettify())
    rows_temp = doc.find(tag, {attr: value})
    rows = rows_temp.find_all('tr', limit=10)
    for row in rows:
        retailer = row.find('img').attrs['alt']
        retailer_list.append(retailer)
        status = row.find('span').contents[4].getText()
        status_list.append(status)
        product_line = row.find('span').contents[7].strip()
        product = product_line[0:product_line.rfind('-')].strip()
        product_list.append(product)
    # print(product_list)
    # print(status_list)
    # print(retailer_list)
    check_last_stock()
    # print(found)


def check_last_stock():
    # Product List goes from (0 -> max), (newest -> oldest)
    # as long as first instance of unique product is in stock for given retailer, product is in stock
    for i in range(0, len(product_list)-1):
        product = product_list[i]
        status = status_list[i]
        retailer = retailer_list[i]
        # if product not found in dictionary -> first instance of
        if not found[retailer].__contains__(product):
            print("Last '" + product + "' status at " + retailer + " is: " + status)
            if "in" in status.lower():
                send_email(product, status, retailer)
            found[retailer].append(product)


def send_email(product, status, retailer):
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=ssl.create_default_context()) as server:
        server.login("jswaggy789@gmail.com", password=password)
        sender_email = "jswaggy789@gmail.com"
        receiver_email = "ibanezguy998@gmail.com"
        message = MIMEMultipart("alternative")
        message["Subject"] = "Nintendo Switch In Stock - Randy Python Code"
        message["From"] = sender_email
        message["To"] = receiver_email
        body = "Last '" + product + "' status at " + retailer + " is: " + status + "\nCheck here for details: " + \
               stock_informer[0]
        message.attach(MIMEText(body, "plain"))
        server.sendmail(sender_email, receiver_email, message.as_string())

for url in stock_informer:
    get_status(url, "table", "id", "TblFeed", headers=True)
