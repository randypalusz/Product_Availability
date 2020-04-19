import smtplib
import ssl
import argparse
import time
from collections import defaultdict
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
from bs4 import BeautifulSoup

ap = argparse.ArgumentParser()
ap.add_argument("-s", "--sender", required=True,
                help="Email sender")
ap.add_argument("-r", "--receiver", required=True,
                help="Email sent to")
ap.add_argument("-p", "--password", required=True,
                help="Sender")
args = vars(ap.parse_args())

oos_strings = {"not available", "check stores", "sold out", "see all buying options"}
header = {'User-Agent': 'Chrome/57.0.2987.110 '}
stock_informer = ["https://www.stockinformer.com/checker-nintendo-switch-console"]
retailer_list = []
website_list = []
product_list = []
status_list = []
price_list = []

# product, retailer, status, price, website
in_stock_list = []

found = defaultdict(list)

# Email stuff
port = 465  # For SSL
sender_email = args["sender"]
receiver_email = args["receiver"]
password = args["password"]


def get_status(address, tag, attr, value, headers=False):
    # Clear out global lists
    clear_lists()
    if headers:
        get_request = requests.get(address, headers=header).text
    else:
        get_request = requests.get(address).text
    doc = BeautifulSoup(get_request, 'html.parser')
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
        price = product_line[product_line.rfind('-')+1:].strip()
        price_list.append(price)
        website = "https://stockinformer.com/" + row.find('a').attrs['href']
        website_list.append(website)
    check_last_stock()
    if in_stock_list:
        send_email()
        return True


def check_last_stock():
    # Product List goes from (0 -> max), (newest -> oldest)
    # as long as first instance of unique product is in stock for given retailer, product is in stock
    for i in range(0, len(product_list) - 1):
        product = product_list[i]
        status = status_list[i]
        retailer = retailer_list[i]
        price = price_list[i]
        website = website_list[i]
        # if product not found in dictionary -> first instance of
        if not found[retailer].__contains__(product):
            print("Most recent status of '" + product + "' at " + retailer + " is: " + status + " - " + price)
            if "in" in status.lower():
                in_stock_list.append([product, retailer, status, price, website])
            found[retailer].append(product)


def send_email():
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=ssl.create_default_context()) as server:
        server.login(sender_email, password=password)
        message = MIMEMultipart("alternative")
        message["Subject"] = "Nintendo Switch In Stock - Python Code"
        message["From"] = sender_email
        message["To"] = receiver_email
        body = ""
        for i in range(0, len(in_stock_list)):
            body += "Most recent status of  '" + in_stock_list[i][0] + \
                    "' at " + in_stock_list[i][1] + \
                    " is: " + in_stock_list[i][2] + \
                    " - " + in_stock_list[i][3] + \
                    "\nCheck here for details: " + in_stock_list[i][4] + \
                    "\n\n"
        message.attach(MIMEText(body, "plain"))
        server.sendmail(sender_email, receiver_email, message.as_string())


def clear_lists():
    retailer_list.clear()
    website_list.clear()
    product_list.clear()
    status_list.clear()
    price_list.clear()
    found.clear()


for url in stock_informer:
    while(True):
        print("Checking stock...")
        time.sleep(10)
        if(get_status(url, "table", "id", "TblFeed", headers=True)):
            sys.exit()
