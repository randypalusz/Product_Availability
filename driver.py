import requests
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver

oos_strings = {"not available", "check stores", "sold out", "see all buying options"}
header = {'User-Agent':  'Chrome/57.0.2987.110 '}
headerbb = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}
target = ["https://www.target.com/p/nintendo-switch-with-neon-blue-and-neon-red-joy-con/-/A-77464001",
          "https://www.target.com/p/nintendo-switch-with-gray-joy-con/-/A-77464002"]
best_buy = ["https://www.bestbuy.com/site/nintendo-switch-32gb-console-gray-joy-con/6364253.p?skuId=6364253",
            "https://www.bestbuy.com/site/nintendo-switch-32gb-console-neon-red-neon-blue-joy-con/6364255.p?skuId=6364255"]
amazon = ["https://www.amazon.com/Nintendo-Switch-Neon-Blue-Joy%E2%80%91/dp/B07VGRJDFY/ref=sr_1_2",
          "https://www.amazon.com/Nintendo-Switch-Gray-Joy%E2%80%91-HAC-001/dp/B07VJRZ62R/ref=sr_1_2",
          "https://www.amazon.com/Nintendo-Switch-Animal-Crossing-New-Horizons/dp/B084DDDNRP/ref=sr_1_5"]


def get_status(address, tag, attr, value, headers=False):
    if headers:
        # use specific header for bestbuy
        if "bestbuy" in address:
            get_request = requests.get(address, headers=headerbb).text
        else:
            get_request = requests.get(address, headers=header).text
    else:
        get_request = requests.get(address).text
    doc = BeautifulSoup(get_request, 'html.parser')
    # print(doc.prettify())
    rows = doc.find_all(tag, {attr: value}, limit=1)
    for row in rows:
        stock = row.getText().strip().lower()
        # print(stock)
        if stock in oos_strings:
            print("Out of stock at: " + address)
        else:
            print("In stock at: " + address)


for url in target:
    get_status(url, "div", "data-test", "oosDeliveryOption", headers=False)

for url in best_buy:
    get_status(url, "div", "class", "fulfillment-add-to-cart-button", headers=True)

for url in amazon:
    get_status(url, "a", "class", "a-button-text", headers=True)



