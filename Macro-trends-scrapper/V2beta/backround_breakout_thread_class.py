import threading
from selenium.webdriver.chrome.options import Options  
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import sys
from yahoofinancials import YahooFinancials
from heapq import heappush, heappop
import datetime
import pytz
import concurrent.futures
import os
 
 
def send_whatsapp_message(group_name , message_to_send):
 
    options = Options()
    options.add_argument('--profile-directory=Default')
    options.add_argument('--user-data-dir=C:/Temp/ChromeProfile') 
    driver = webdriver.Chrome(chrome_options=options)   

    driver.get("https://web.whatsapp.com/")
    wait = WebDriverWait(driver, 600)

    x_arg = '//span[contains(@title,' + group_name + ')]'
    group_title = wait.until(EC.presence_of_element_located((
    By.XPATH, x_arg)))
    print (group_title)
    print ("Wait for few seconds")
    group_title.click()
    message = driver.find_elements_by_xpath('//*[@id="main"]/footer/div[1]/div[2]/div/div[2]')[0]

    message.send_keys(message_to_send)
    sendbutton = driver.find_elements_by_xpath('//*[@id="main"]/footer/div[1]/div[3]/button')[0]
    sendbutton.click()
    driver.close()

class backround_breakout_thread_class(object):


    def __init__(self):

        self.stocks_set = self.__get_set_of_stocks()
        thread = threading.Thread(target=self.run)
        thread.daemon = True  
        thread.start()
        thread.join()

    def run(self):
        
        sleep_time = 600
        while True:
            # Do something
            for stock_symbol in self.stocks_set:
                yahoo_stock = YahooFinancials(stock_symbol)
                print(stock_symbol)
                if (self.__detect_breakout(yahoo_stock, 1.2, 0.02) == True) :
                    msg = 'Buy alert for' + stock_symbol + ' as volume increase by :' + string(yaho.get_current_volume())
                    send_whatsapp_message('"Stocks alerts"', msg )
                else :
                    send_whatsapp_message('"Stocks alerts"', 'bo breakout'+stock_symbol )    

            time.sleep(sleep_time)

    def __is_market_open(self, nyc_datetime):
     
        if (nyc_datetime.hour < 9) or (nyc_datetime.hour > 16):
            return False

        if (nyc_datetime.hour == 9) and (nyc_datetime.minute < 30):
            return False

        if (nyc_datetime.hour == 16) and (nyc_datetime.minute > 0):
            return False

        return True            

    def __get_relative_time_percentage(self, nyc_datetime):
       
        time_of_nasdaq_open_in_minutes = 390
        hour_difference = nyc_datetime.hour - 9
        hour_difference_in_minutes = hour_difference * 60
        minutes_difference = nyc_datetime.minute - 30
        sum_of_min_difference = minutes_difference + hour_difference_in_minutes
        return sum_of_min_difference / time_of_nasdaq_open_in_minutes


    def __detect_breakout(self, stock, volume_threshold, percent_threshold):
       
        is_breakout = False
        nyc_datetime = datetime.datetime.now(pytz.timezone('US/Eastern'))
        market_open_flag = self.__is_market_open(nyc_datetime)

        if not market_open_flag:
            return False

        stock_current_volume = stock.get_current_volume()
        stock_3m_avg_volume = stock.get_three_month_avg_daily_volume()
        relative_time_percentage = self.__get_relative_time_percentage(nyc_datetime)
        stock_3m_avg_relative_volume = relative_time_percentage * stock_3m_avg_volume
        stock_current_percent_change = stock.get_current_percent_change()

        if (stock_current_volume >= stock_3m_avg_relative_volume * volume_threshold) and (stock_current_percent_change >= percent_threshold):
            is_breakout = True

        return is_breakout
        
    def __get_set_of_stocks(self):
        
        stocks_set = set()
        file = 'technically_valid_stocks.txt'
        try:
            with open(file, 'r+') as f:
                for line in f:
                    stock_symbol = line.split(',')[0]
                    stocks_set.add(stock_symbol)
        except:
            print('Failed to read file')
        
        return stocks_set
    

def main():
    backround_onj = backround_breakout_thread_class()

if __name__ == "__main__":
    main()