import pandas as pd

import sys
import os
import re
from datetime import datetime 
import time
import json

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchWindowException, TimeoutException


def printProgress (iteration, total, prefix = '', suffix = '', decimals = 1, barLength = 100):
    # python progress bar
    # reference: https://tjjourney7.tistory.com/14
    # 약간 변형하여 사용

    formatStr = "{0:." + str(decimals) + "f}"
    percent = formatStr.format(100 * (iteration / float(total)))
    filledLength = int(round(barLength * iteration / float(total)))
    bar = '#' * filledLength + '-' * (barLength - filledLength)
    sys.stdout.write('\r    %s |%s| (%s/%s) %s%s %s' % (prefix, bar, iteration+1, total,percent, '%', suffix)),
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()

class BookDBUpdater:

    def __init__(self):
        
        user_agent = "user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko"
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--headless') #selenium 작동시 웹 페이지를 작동하지 않음
        self.chrome_options.add_argument("--log-level=3") #log를 남가지 않음
        self.chrome_options.add_argument('user-agent=' + user_agent)
        self.driver = webdriver.Chrome(os.path.join(os.getcwd(), 'chromedriver'), chrome_options=self.chrome_options)
    

    def makeDiffMonth(target_year, target_month):
        # update시 code의 updateDate 정보를 받아 page_nation의 범위를 제한함.
        now_year = datetime.now().year 
        now_month = target_month
        diff = (now_month-target_month) + (now_year-target_year) * 12
        return diff

    def getCategoryCode(self):
        # 알라딘 사이트의 도서 분야 코드를 수집

        codes = pd.DataFrame(columns=['code', 'name'])
        self.driver = webdriver.Chrome(os.path.join(os.getcwd(), 'chromedriver.exe'), chrome_options=self.chrome_options)
        self.driver.get("https://www.aladin.co.kr/home/wbookmain.aspx")
        html = self.driver.page_source
        self.driver.quit()

        soup = BeautifulSoup(html, 'html.parser')
        browse_sub_list = soup.select('li.browse_sub > a')

        #extract href and text
        for li in browse_sub_list:
            codes = codes.append({'code':li.attrs['href'].split('=')[1], 'name': li.text}, ignore_index=True)
        
        #save to csv
        codes.to_csv('codes.csv', encoding='utf-8', index=False)

    def getBookURL(self): 

        if os.path.exists('bookInfo.csv'): # bookinfo.csv라는 파일이 있으면 그 파일을 읽어온다
            booksinfo = pd.read_csv('bookInfo.csv')
        else:
            booksinfo = pd.DataFrame(columns= ['isbn13', 'title', 'sub-title', 'authors', 'translator', 'publisher', 'date', 'original_title', 'price', 'pages', 'aladin_url','keywords'])

        df = pd.read_csv('codes.csv')
        codes=df['code']
        names=df['name']

        for code, name in zip(codes, names):
<<<<<<< HEAD

            print(f"Now=> {name} : {code}")
            url = f'https://www.aladin.co.kr/shop/wbrowse.aspx?BrowseTarget=List&ViewRowsCount=100&ViewType=Detail&PublishMonth={diff}&SortOrder=5&page=1&Stockstatus=1&CID={code}&SearchOption=&CustReviewRankStart=&CustReviewRankEnd=&CustReviewCountStart=&CustReviewCountEnd=&PriceFilterMin=&PriceFilterMax='
            driver.get(url)
            end_num = driver.find_element(by=By.XPATH, value='//*[@id="short"]/div[12]/a')
            end_num.get_attribute('href')
            end_num = int(re.sub('[^0-9]', '', end_num.get_attribute('href')))
=======
            # category code를 순회하며 데이터를 수집함
>>>>>>> ff4c5d91946137745d0a65fba8353be40f2c7413

            print(f"Now=> {name} : {code}")
            
            # 책 발행 연도를 제한하기 위한 코드. 현재부터 제한연도까지 차이만큼 월수를 구함
            with open('config.json', 'r') as file:
                config = json.load(file)
            try:
                #code : updateDate가 있으면 그 날짜를 기준으로
                date = config[code].split('.')
                target_year = int(date[0])
                target_month = int(date[1])
                diff = self.makeDiffMonth(target_year, target_month)
            except KeyError:
                #없으면 2010년이 기준
                diff = self.makeDiffMonth(2010, 1)

            self.driver.get(f'https://www.aladin.co.kr/shop/wbrowse.aspx?BrowseTarget=List&ViewRowsCount=200&ViewType=Detail&PublishMonth={diff}&SortOrder=5&page=1&Stockstatus=1&CID={code}&SearchOption=&CustReviewRankStart=&CustReviewRankEnd=&CustReviewCountStart=&CustReviewCountEnd=&PriceFilterMin=&PriceFilterMax=')
            
            # page_nation의 끝 번호를 구한다.
            end_num = self.driver.find_element(by=By.XPATH, value='//*[@id="short"]/div[12]/a')
            end_num.get_attribute('href')
            end_num = int(re.sub('[^0-9]', '', end_num.get_attribute('href'))) 

            for page in range(end_num,0, -1): #오래된 책 데이터부터 수집한다.
                try:
                    url = f'https://www.aladin.co.kr/shop/wbrowse.aspx?BrowseTarget=List&ViewRowsCount=200&ViewType=Detail&PublishMonth={diff}&SortOrder=5&page={page}&Stockstatus=1&CID={code}&SearchOption=&CustReviewRankStart=&CustReviewRankEnd=&CustReviewCountStart=&CustReviewCountEnd=&PriceFilterMin=&PriceFilterMax='
                    self.driver.get(url)
                    self.driver.implicitly_wait(2) #페이지가 열릴 때 까지 2초를 기다림.
                    book_list = self.driver.find_elements(by=By.XPATH, value="//div[@class='ss_book_box']/table/tbody/tr/td[2]/table/tbody/tr[1]/td/div/a")
                    book_dates = self.driver.find_elements(by=By.XPATH, value='//div[@class="ss_book_list"]/ul')

                    if len(book_list) >0 :
                        for url, book_date in zip(book_list, book_dates): 
                            # book list를 돌면서 url을 수집한뒤 getBookInfo에 보냄
                            url = url.get_attribute('href')
                            # 현재 책의 출간 날짜를 구함.
                            book_date = re.findall("[0-9]{4}년 [0-9]{1,2}월", book_date)[0]
                            book_date = re.sub('년','.', book_date).rstrip('월')

                            #book_date와 config 날짜를 비교해서 더 과거면 continue

                            info = self.getBookInfo(url)
                            booksinfo.loc[len(booksinfo)] = info
                            
                            config[code] = book_date

                    #진행 사항을 보여주는 progress bar
                    printProgress(page, end_num, 'Progress:', 'Complete', 1, 50)

                except TimeoutException:
                    print("\nOps! TimeOut!")
                    continue

                except NoSuchWindowException:
                    print("\nOps! NosuchWindow! So, restart!")
                    self.driver.quit()
                    self.driver = webdriver.Chrome(os.path.join(os.getcwd(), 'chromedriver.exe'), chrome_options=self.chrome_options)
        self.driver.quit()
        return booksinfo


    def getBookInfo(self, url):
        #

        self.driver.get(url)
        #title
        title = self.driver.find_element(by=By.XPATH, value='//*[@id="Ere_prod_allwrap"]/div[3]/div[2]/div[1]/div/ul/li[2]/div/a[1]').text
        #sub_title
        sub_title = self.driver.find_elements(by=By.XPATH, value='//*[@id="Ere_prod_allwrap"]/div[3]/div[2]/div[1]/div/ul/li[2]/div/span')
        sub_title = sub_title[0].text if sub_title else None
        #isbn 
        isbn = self.driver.find_elements(by=By.XPATH , value='//*[@id="Ere_prod_allwrap"]/div[9]/div[1]/div[3]/div[1]/ul/li')
        isbn = isbn[-1].text.split(' : ')[-1]            
        #categories
        categories = self.driver.find_elements(by=By.XPATH, value='//*[@id="ulCategory"]/li')
        categories = [category.text.split(' > ')[-1] for category in categories]
        #introduction
        
        # 아래 정보는 교보문고를 통해 수집
        #author, translator, publisher, date, original_title, keyword, page
        kyobo_url = f'http://www.kyobobook.co.kr/product/detailViewKor.laf?mallGb=KOR&ejkGb=KOR&barcode={isbn}'
        self.driver.get(kyobo_url)

        #get author+author_code, translator+translator_code, publisher, date
        # info = driver.find_elements(by=By.XPATH, value='//*[@id="container"]/div[2]/form/div[1]/div[@class="author"]')
        # info = info[0].text.split(' | ')

        return #list


class ReviewUpdator():
    def __init__():
        pass


if __name__ == "__main__":
    getbook = BookDBUpdater()
    getbook.getBookURL()