import requests
import re
from bs4 import BeautifulSoup
import array as arr
import ast
from operator import eq, add, sub
import sqlite3 
from threading import Thread
import threading
import time
import json
from multiprocessing import Process, Value
from concurrent.futures import ThreadPoolExecutor
import os.path

global_stock_dict = {}

class macrotrends_generic:

    def __init__(self,stock_symbol, company_name, operation):
        #Private methods and members
        self.__symbol = stock_symbol
        self.__company_name = company_name
        self.__operation = operation
        self.__stock_path = stock_symbol +'/' + company_name + '/' + operation
        self.__macrotrends_list = []


    def run(self):
        self.__soup = self.__get_html_profile_data(self.__stock_path)
        self.__fill_macrotrends_list(self.__soup)
        self.fill_global_stock_dict()

    def __get_html_profile_data(self, stock_path):
        URL = 'https://www.macrotrends.net/stocks/charts/'+stock_path
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        return soup


    def __fill_macrotrends_list(self,soup):
        results = soup.findAll("th")
        j = 0
        for res in results:
            if ( j == 1):
                for i in range(24):
                    res = res.find_next('td')
                    if (( i % 2 ) == 1):
                        self.__macrotrends_list.insert(0,res.text)
            j = j + 1



    def get_list_func(self):
        return self.__macrotrends_list

    def fill_global_stock_dict(self):
        global global_stock_dict

        if (self.__operation == 'eps-earnings-per-share-diluted'):
            global_stock_dict[self.__symbol][0] = self.__macrotrends_list
        elif (self.__operation == 'net-income'):
            global_stock_dict[self.__symbol][1] = self.__macrotrends_list
        else:
            global_stock_dict[self.__symbol][2] = self.__macrotrends_list



def read_stock_file(file_path):
    stock_map = {}
    f = open(file_path, "r")
    for stock in f:
        stock_array = stock.split()
        if (len(stock_array) > 1) :
            # clean the stock name
            if ((stock_array[1][-1] == '-') or (stock_array[1][-1] == '.')):
                stock_array[1] = stock_array[1][:-1]
            # build hash map 
            stock_map[stock_array[0]] = stock_array[1]

    return stock_map
    
    
def write_db():
    db_file = 'stock_db.txt'

    if os.path.exists(db_file):
        with open(db_file, 'r+') as f:
            f.truncate(0)  # need '0' when using r+

    for key in global_stock_dict:

        eps_array = global_stock_dict[key][0]
        net_income_array = global_stock_dict[key][1]
        sales_array = global_stock_dict[key][2]

        # open output file for writing
        with open('stock_db.txt', 'a') as filehandle:
            filehandle.write(key +' net_income ')
            json.dump(net_income_array, filehandle)
            filehandle.write(' eps ')
            json.dump(eps_array, filehandle)
            filehandle.write(' sales ')
            json.dump(sales_array, filehandle)
            filehandle.write('\n')



    
def iteatre_over_stock_map(stock_map):

    i = 1
    start = time.time()
    pool = ThreadPoolExecutor(max_workers=100)
    for stock_symbol in stock_map:
        try:
            global global_stock_dict
            print(stock_symbol)
            global_stock_dict[stock_symbol] = ['','','']
            sem = threading.Semaphore(4)

            obj1 = macrotrends_generic(stock_symbol,stock_map[stock_symbol], 'net-income')
            obj2 = macrotrends_generic(stock_symbol,stock_map[stock_symbol],'eps-earnings-per-share-diluted')
            obj3 = macrotrends_generic(stock_symbol,stock_map[stock_symbol],'revenue')

            t1 =  pool.submit(obj1.run) 
            t2 =  pool.submit(obj2.run)
            t3 =  pool.submit(obj3.run)

            time.sleep(0.02)
            if (i % 20 == 0):
                time.sleep(0.05)
            i = i + 1


        except:
            print ('didnt work for'+ stock_symbol)
            pass
    end = time.time()
    print(end - start)
    pool.shutdown(wait=True)
            
def main():

    stock_map = read_stock_file("all_stocks.txt")
    iteatre_over_stock_map(stock_map)
    write_db()
    
    
if __name__== "__main__":
    main()