import threading
from concurrent.futures.thread import ThreadPoolExecutor

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
from functools import partial


def send_whatsapp_message(group_name, message_to_send):
    print('here')
    options = Options()
    options.add_argument('--profile-directory=Default')
    options.add_argument('--user-data-dir=C:/Temp/ChromeProfile')
    driver = webdriver.Chrome(chrome_options=options)

    driver.get("https://web.whatsapp.com/")
    wait = WebDriverWait(driver, 600)

    x_arg = '//span[contains(@title,' + group_name + ')]'
    group_title = wait.until(EC.presence_of_element_located((
        By.XPATH, x_arg)))
    print(group_title)
    print("Wait for few seconds")
    group_title.click()
    message = driver.find_elements_by_xpath('//*[@id="main"]/footer/div[1]/div[2]/div/div[2]')[0]

    message.send_keys(message_to_send)
    sendbutton = driver.find_elements_by_xpath('//*[@id="main"]/footer/div[1]/div[3]/button')[0]
    sendbutton.click()
    driver.close()





class backround_breakout_thread_class(object):

    def __init__(self):

        self.stocks_map = self.__get_map_of_stocks()
        self.breakout_stocks = set()

        try:
            thread = threading.Thread(target=self.run)
            thread.daemon = True
            thread.start()
            while thread.isAlive():
                thread.join(1)
        except (KeyboardInterrupt, SystemExit):
            print('program closed by user')

    def run(self):

        timer_of_breakout_checking = 60 * 15
        timer_between_whatsapp_writing = 20
        pool = ThreadPoolExecutor(max_workers = 10)

        while True:

            for stock in self.stocks_map:
                t1 =  pool.submit(self.__run_yahoo_stock, stock, self.stocks_map[stock])
                time.sleep(timer_between_whatsapp_writing)

            time.sleep(timer_of_breakout_checking)

    def __run_yahoo_stock(self, stock, pivot):

        if (stock in self.breakout_stocks):
            return

        yahoo_stock = YahooFinancials(stock)
        if self.__detect_breakout(yahoo_stock, 1.4, 0.03, pivot,stock) :
            self.breakout_stocks.add(stock)
            msg = 'Buy alert for ' + stock
            send_whatsapp_message('"Stocks alerts"', msg)



    def __get_relative_time_percentage(self, nyc_datetime):

        time_of_nasdaq_open_in_minutes = 390
        hour_difference = nyc_datetime.hour - 9
        hour_difference_in_minutes = hour_difference * 60
        minutes_difference = nyc_datetime.minute - 30
        sum_of_min_difference = minutes_difference + hour_difference_in_minutes
        return sum_of_min_difference / time_of_nasdaq_open_in_minutes

    def __is_market_open(self, nyc_datetime):

        if (nyc_datetime.isoweekday() == 6) or (nyc_datetime.isoweekday() == 7):
            return False

        if (nyc_datetime.hour < 9) or (nyc_datetime.hour > 16):
            return False

        if (nyc_datetime.hour == 9) and (nyc_datetime.minute < 30):
            return False

        if (nyc_datetime.hour == 16) and (nyc_datetime.minute > 0):
            return False

        return True


    def __detect_breakout(self, stock, volume_threshold, percent_threshold, pivot_point, stock_symbol):

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
        stock_current_price = stock.get_current_price()

        if (stock_current_volume >= stock_3m_avg_relative_volume * volume_threshold) and (stock_current_percent_change >= percent_threshold) and (float(pivot_point) <= stock_current_price ):
            print('is_breakout')
            is_breakout = True
        else:
            print ('no breakout so far for :')
        return is_breakout

    def __get_map_of_stocks(self):

        stocks_map = {}
        file = 'technically_valid_stocks.txt'
        try:
            with open(file, 'r+') as f:
                for line in f:
                    stock_symbol = line.split(',')[0]
                    pivot_point = line.split(' ')[2].rstrip()
                    stocks_map[stock_symbol] = pivot_point
        except:
            print('Failed to read file')

        return stocks_map


def main():

    backround_onj = backround_breakout_thread_class()
    a = 1
if __name__ == "__main__":


    main()