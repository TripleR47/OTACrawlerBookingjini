from re import findall
from lxml import html
from time import sleep
from selenium import webdriver
#from pprint import pprint
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import pandas as pd
#import os
#from urllib.request import Request, urlopen
#from xvfbwrapper import Xvfb
'''
def check_ping(hostname):
    response = os.system("ping " + hostname)
    # and then check the response...
    if response == 0:
        return True
    else:
        return False
'''
def parse(url, proxy, driver, inputs):
    searchKey = inputs[0] # Change this to your city 
    checkInDate = inputs[1] #Format %d/%m/%Y
    checkOutDate = inputs[2] #Format %d/%m/%Y
    if driver == 1:
        PROXY = proxy # IP:PORT 
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--proxy-server=%s' % PROXY)
        response = webdriver.Chrome(executable_path = r'C:\Users\TripleR\Downloads\chromedriver_win32\chromedriver.exe')
    if driver == 2:
        firefox_capabilities = DesiredCapabilities.FIREFOX
        firefox_capabilities['marionette'] = True
        firefox_capabilities['binary'] = '/usr/bin/firefox'
        profile = webdriver.FirefoxProfile()
        profile.set_preference("network.proxy.type", 1)
        profile.set_preference("network.proxy.http", proxy['ip'])
        profile.set_preference("network.proxy.http_port", proxy['port'])
        response = webdriver.Firefox(firefox_profile=profile, capabilities = firefox_capabilities, executable_path=r'C:\Users\TripleR\Downloads\geckodriver-v0.26.0-win64\geckodriver.exe')
    try:
        response.get(url) 
        searchKeyElement = response.find_elements_by_xpath('//input[contains(@id,"destination")]')
        checkInElement = response.find_elements_by_xpath('//input[contains(@class,"check-in")]')
        checkOutElement = response.find_elements_by_xpath('//input[contains(@class,"check-out")]')
        submitButton = response.find_elements_by_xpath('//button[@type="submit"]')
        if searchKeyElement and checkInElement and checkOutElement:
            searchKeyElement[0].send_keys(searchKey)
            sleep(5)
            searchKeyElement[0].send_keys(Keys.TAB)
            sleep(5)
            checkInElement[0].clear()
            checkInElement[0].send_keys(checkInDate)
            checkOutElement[0].clear()
            checkOutElement[0].send_keys(checkOutDate)
            randomClick = response.find_elements_by_xpath('//h1')
            if randomClick:
                randomClick[0].click()
            sleep(3)
            submitButton[0].click()
            sleep(5)
            
        hotelNames = []
        prices = []
        
        current_scroll_position, new_height,speed= 0, 1, 8
        while current_scroll_position <= new_height:
            current_scroll_position += speed
            response.execute_script("window.scrollTo(0, {});".format(current_scroll_position))
            new_height = response.execute_script("return document.body.scrollHeight")
        sleep(5)
        #response.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        parser = html.fromstring(response.page_source,response.current_url)
        hotels = parser.xpath('//section[@class="hotel-wrap"]')
        for hotel in hotels[:]: #Replace 5 with 1 to just get the cheapest hotel
            hotelName = hotel.xpath('.//h3/a')
            hotelName = hotelName[0].text_content() if hotelName else None
            price = hotel.xpath('.//div[@class="price"]/a//ins')
            price = price[0].text_content().replace(",","").strip() if price else None
            if price==None:
                price = hotel.xpath('.//div[@class="price"]/a')
                price = price[0].text_content().replace(",","").strip() if price else None
            
            price = findall('([\d\.]+)',price) if price else None
            price = price[0] if price else None
            hotelNames.append(str(hotelName))
            prices.append(str(price))
        
        response.close()
        item = {
                "hotelName":hotelNames,
                inputs[1]:prices
        }
        df = pd.DataFrame(item)
        df = pd.DataFrame.drop_duplicates(df)
        df.reset_index(drop = True, inplace = True)
        return df
    except:
        response.close()