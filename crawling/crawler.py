'''
 추가할 기능

 1. crawler multiprocessing: https://conservative-vector.tistory.com/entry/%EC%85%80%EB%A0%88%EB%8B%88%EC%9B%80%EC%9D%84-%EC%93%B0%EB%8A%94%EB%8D%B0-%EB%A9%80%ED%8B%B0%ED%94%84%EB%A1%9C%EC%84%B8%EC%8B%B1%EC%9D%B4-%EC%95%88-%EB%8F%BC%EC%9A%94
 2. 업데이트 범위 검사하는 방법론 찾기
'''
import pandas as pd

import sys
import os
import re
from datetime import datetime 
# import time
# import json
# import argparse

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchWindowException, TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities 
caps = DesiredCapabilities().CHROME 
caps["pageLoadStrategy"] = "none"


def printProgress (iteration, total, name, page, end_num, prefix = '', suffix = '', decimals = 1, barLength = 100):
    # python progress bar
    # reference: https://tjjourney7.tistory.com/14
    # 약간 변형하여 사용

    now_page = end_num - page +1

    formatStr = "{0:." + str(decimals) + "f}"
    percent = formatStr.format(100 * (iteration / float(total)))
    filledLength = int(round(barLength * iteration / float(total)))
    bar = '#' * filledLength + '-' * (barLength - filledLength)
    sys.stdout.write('\r  [%s: (%d/%d)] %s |%s| (%s/%s) %s%s %s' % (name, now_page, end_num, prefix, bar, iteration+1, total, percent, '%', suffix)),
    if iteration == total:
        
        sys.stdout.write('\n')
    sys.stdout.flush()

class BookDBUpdater:

    def __init__(self):
        
        
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'
        self.chrome_options = webdriver.ChromeOptions()
        # 속도 향상을 위해 사용 (출처: https://pcmc.tistory.com/entry/190125-performance-in-selenium-%EC%85%80%EB%A0%88%EB%8B%88%EC%9B%80%EC%97%90%EC%84%9C-%EC%84%B1%EB%8A%A5-%ED%96%A5%EC%83%81%EA%B3%BC-%EA%B4%80%EB%A0%A8%ED%95%98%EC%97%AC)
        prefs = {'profile.default_content_setting_values': {'cookies' : 2, 'images': 2, 'plugins' : 2, 
                                                            'popups': 2, 'geolocation': 2, 'notifications' : 2, 
                                                            'auto_select_certificate': 2, 'fullscreen' : 2, 
                                                            'mouselock' : 2, 'mixed_script': 2, 'media_stream' : 2, 
                                                            'media_stream_mic' : 2, 'media_stream_camera': 2, 
                                                            'protocol_handlers' : 2, 'ppapi_broker' : 2, 
                                                            'automatic_downloads': 2, 'midi_sysex' : 2, 'push_messaging' : 2, 
                                                            'ssl_cert_decisions': 2, 'metro_switch_to_desktop' : 2, 
                                                            'protected_media_identifier': 2, 'app_banner': 2, 'site_engagement' : 2, 
                                                            'javascript': 2, 'durable_storage' : 2}} 
        self.chrome_options.add_experimental_option('prefs', prefs) 
        self.chrome_options.add_argument("start-maximized") 
        self.chrome_options.add_argument("disable-infobars") 
        self.chrome_options.add_argument("--disable-extensions")

        self.chrome_options.add_argument('--headless') #selenium 작동시 웹 페이지를 작동하지 않음
        self.chrome_options.add_argument("--log-level=3") #log를 남가지 않음 
        
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.chrome_options.add_argument('user-agent=' + user_agent)
        self.chrome_options.add_argument("disable-gpu") 
        self.driver = webdriver.Chrome(os.path.join(os.getcwd(), 'chromedriver'), chrome_options=self.chrome_options)


    def makeDiffMonth(self, target_year, target_month):
        # update시 code의 updateDate 정보를 받아 page_nation의 범위를 제한함.
        now_year = datetime.now().year 
        now_month = datetime.now().month
        diff = (now_month-target_month) + (now_year-target_year) * 12
        return diff

    def getCategoryCode(self):
        # 알라딘 사이트의 도서 분야 코드를 수집

        codes = pd.DataFrame(columns=['code', 'name'])
        self.driver = webdriver.Chrome(os.path.join(os.getcwd(), 'chromedriver.exe'), chrome_options=self.chrome_options)
        self.driver.get("https://www.aladin.co.kr/home/wbookmain.aspx")
        html = self.driver.page_source
        

        soup = BeautifulSoup(html, 'html.parser')
        browse_sub_list = soup.select('li.browse_sub > a')

        #extract href and text
        for li in browse_sub_list:
            codes = codes.append({'code':li.attrs['href'].split('=')[1], 'name': li.text}, ignore_index=True)
        
        #save to csv
        codes.to_csv('data/rest.csv', encoding='utf-8', index=False)
        self.driver.quit()

    def getBookData(self): 

        if not os.path.exists('data/bookInfo.csv') and not os.path.exists('data/bookIntro.csv'): # 파일이 없으면
            booksinfo = pd.DataFrame(columns=['date', 'isbn13', 'title', 'sub_title', 'categories', 'author', 'translator', 'publisher', 'keywords', 'origin_title', 'page', 'aladin_url'])
            booksintro = pd.DataFrame(columns=['isbn13', 'title', 'introduction'])
            
            booksinfo.to_csv()
            booksintro.to_csv()

        df = pd.read_csv('data/codes.csv')
        codes=df['code']
        names=df['name']

        for code, name in zip(codes, names):
            # category code를 순회하며 데이터를 수집함

            # print(f"Now=> {name} : {code}")ㄴ
            
            # 책 발행 연도를 제한하기 위한 코드. 현재부터 제한연도까지 차이만큼 월수를 구함
            # with open('config/config.json', 'r') as file:
            #     config = json.load(file)
            # try:
            #     #code : updateDate가 있으면 그 날짜를 기준으로
            #     date = config[code].split('.')
            #     target_year = int(date[0])
            #     target_month = int(date[1])
            #     diff = self.makeDiffMonth(target_year, target_month)
            # except KeyError:
            #     #없으면 2010년이 기준
            #     diff = self.makeDiffMonth(2010, 1)
            
            diff = self.makeDiffMonth(2020, 1)

            self.driver.get(f'https://www.aladin.co.kr/shop/wbrowse.aspx?BrowseTarget=List&ViewRowsCount=50&ViewType=Detail&PublishMonth={diff}&SortOrder=5&page=1&Stockstatus=1&CID={code}&SearchOption=&CustReviewRankStart=&CustReviewRankEnd=&CustReviewCountStart=&CustReviewCountEnd=&PriceFilterMin=&PriceFilterMax=')
            
            # page_nation의 끝 번호를 구한다.
            end_num = self.driver.find_elements(by=By.XPATH, value='//div[@class="numbox_last"]/a')
            if end_num:
                end_num = end_num[0]
                end_num.get_attribute('href')
                end_num = int(re.sub('[^0-9]', '', end_num.get_attribute('href'))) 
            else:
                end_num = 1

            for page in range(end_num,0, -1): #오래된 책 데이터부터 수집한다.
                
                booksinfo = pd.DataFrame()
                booksintro = pd.DataFrame()

                page_url = f'https://www.aladin.co.kr/shop/wbrowse.aspx?BrowseTarget=List&ViewRowsCount=50&ViewType=Detail&PublishMonth={diff}&SortOrder=5&page={page}&Stockstatus=1&CID={code}&SearchOption=&CustReviewRankStart=&CustReviewRankEnd=&CustReviewCountStart=&CustReviewCountEnd=&PriceFilterMin=&PriceFilterMax='
                                
                self.driver.get(page_url)
                
                book_list = self.driver.find_elements(by=By.XPATH, value="//div[@class='cover_area']/a")
                book_urls = [list.get_attribute('href') for list in book_list]
                # book_dates = self.driver.find_elements(by=By.XPATH, value='//div[@class="ss_book_list"]/ul')
                if len(book_urls) >0 :
                    # for url, book_date in zip(book_list, book_dates): 
                    i = 0
                    for url in book_urls:
                        try:
                            # if self.driver.current_url != page_url:
                            #     self.driver.get(page_url)
                            
                            # book list를 돌면서 url을 수집한뒤 getBookInfo에 보냄
                            
                            # 현재 책의 출간 날짜를 구함.
                            # book_date = re.findall("[0-9]{4}년 [0-9]{1,2}월", book_date)[0]
                            # book_date = re.sub('년','.', book_date).rstrip('월')

                            #book_date와 config 날짜를 비교해서 더 과거면 continue
                            # if url in booksinfo['aladin_url']:
                            #     continue

                            info, intro = self.getBookInfo_aladin(url)

                            if info == None and intro == None:
                                continue

                            info["aladin_url"] = url

                            info = pd.DataFrame.from_dict([info])
                            intro = pd.DataFrame.from_dict([intro])

                            booksinfo = booksinfo.append(info)
                            booksintro = booksintro.append(intro)
                    
                            #진행 사항을 보여주는 progress bar
                            printProgress(i, len(book_urls)-1, name, page, end_num, 'Progress:', 'Complete', 1, 25)
                            i += 1
                            
                        except TimeoutException:
                            print("\nOps! TimeOut!")
                            continue

                        except NoSuchWindowException:
                            print("\nOps! NosuchWindow! So, restart!")
                            self.driver.quit()
                            self.driver = webdriver.Chrome(os.path.join(os.getcwd(), 'chromedriver.exe'), chrome_options=self.chrome_options)

                        except Exception as e:
                            # print('\n', e)
                            continue
                
                booksinfo.to_csv('data/bookInfo.csv', mode='a', encoding='utf-8', index=False, header=None, sep="\t")
                booksintro.to_csv('data/bookIntro.csv', mode='a', encoding='utf-8', index=False, header=None, sep="\t")    
                print('')
        
        self.driver.quit()

    def getBookInfo_aladin(self, url, update_date=None):
        # 이 함수는 알라딘에서 데이터를 수집한다. 수집한 데이터 중 isbn으로 kyobo web으로 접근한다.
        '''
        수집 데이터:
        title, sub_title, isbn, categories, date
        '''
        try:
            self.driver.get(url)
            dict = {}
            dict_intro = {}
            date = self.driver.find_element(by=By.XPATH, value='//li[@class="Ere_sub2_title"]').text
            date_pattern = r"\d{4}-\d{2}-\d{2}"
            # date_group = r"(\d{4})년\s(\d{1,2})월\s(\d{1,2})일"
            # to_change = r"\1.\2.\3"
            dict["date"] = re.findall(date_pattern, date)[0]
            # date = re.sub(date_group, to_change, date)
            
            # if update_date > date:
            #     #이 책의 출간일이 최종 Update 날짜보다 과거라면 함수 종료
            #     return None

            self.driver.get(url)

            #isbn 
            isbn = self.driver.find_elements(by=By.XPATH , value='//div[@class="conts_info_list1"]')
            isbn = isbn[-1].text.split(' : ')[-1]
            try:
                dict["isbn13"] = int(re.sub('[^0-9]{13}', '', isbn))
                dict_intro["isbn13"] = dict["isbn13"]
            except ValueError:
                return None, None
            #title
            dict["title"] = self.driver.find_element(by=By.XPATH, value='//a[@class="Ere_bo_title"]').text
            dict_intro["title"] = dict["title"]
            
            #sub_title                                             
            sub_title = self.driver.find_elements(by=By.XPATH, value='//span[@class="Ere_sub1_title"]')
            dict["sub_title"] = sub_title[0].text.lstrip('-') if sub_title else None
            
            

            #categories 
            # 카테고리 중 마지막만 사용한다.
            categories = self.driver.find_elements(by=By.XPATH, value='//ul[@class="ulCategory"]/li')
            categories = list(set([category.text.split(' > ')[-1] for category in categories]))
            if len(categories) > 1:
                dict["categories"] = '/'.join(categories)
            else:
                dict["categories"] = None

            dict_kyobo, introduction = self.getBookInfo_kyobo(isbn)
            dict.update(dict_kyobo)
            dict_intro.update(introduction)

            return dict, dict_intro

        except Exception as e:
            # print("\n",e)
            # print("Here is Aladin, => ",url)
            # print(dict)
            return None
    
    def getBookInfo_kyobo(self, isbn):

        
        # 아래 정보는 교보문고를 통해 수집
        '''
        수집 데이터
        author, translator, publisher, original_title, keyword, page, introduction
        '''
        try:
            dict = {}
            dict_intro = {}
            kyobo_url = f'http://www.kyobobook.co.kr/product/detailViewKor.laf?mallGb=KOR&ejkGb=KOR&barcode={isbn}'
            self.driver.get(kyobo_url)

            #get author+author_code, translator+translator_code, publisher, date
            names_elements = self.driver.find_elements(by=By.XPATH, value='//a[@class="detail_author"]')
            names = [name.text for name in names_elements]
            if len(names) > 1:
                dict["author"] = ','.joint(names)
            else:
                dict["author"] = names[0]

            # try:
            #     for author_number in names_elements:
            #         author_number = author_number.get_attribute("onclick").split(';')[0]
            #         author_number = author_number.split(',')[-1]
            #         author_number = re.sub('[^0-9]','', author_number)
            #     if len(author_number) > 1:
            #         dict["author_number"] = ','.join(author_number)
            #     elif len(author_number) == 1:
            #         dict["author_number"] = author_number[0]
            #     else:
            #         dict["author_number"] = None

            # except ValueError:
            #     dict["author_number"] = None

            translators = self.driver.find_elements(by=By.XPATH, value='//a[@class="detail_translator"]')
            translators = [translator.text for translator in translators if translator]
            if len(translators) > 1:
                dict["translator"] = ','.join(translators)
            elif len(translators) == 1:
                dict["translator"] = translators[0]
            else:
                dict["translator"] = None

            # try:
            #     for translator_number in translators:
            #         translator_number = translator_number.get_attribute("onclick").split(';')[0]
            #         translator_number = re.sub('[^0-9]','', translator_number.split(',')[-1])
            #         if len(translator_number) > 1:
            #             dict["translator_number"] = ','.join(translator_number)
            #         elif len(translator_number) == 1:
            #             dict["translator_number"] = translator_number[0]
            #         else:
            #             dict["translator_number"] = None

            # except ValueError:
            #     dict["translator_number"] = None

            dict["publisher"] = self.driver.find_element(by=By.XPATH, value='//span[@title="출판사"]').text
            
            keywords = self.driver.find_elements(by=By.XPATH, value='//div[@class="tag_list"]/a/span')
            if len(keywords) > 1:
                keywords = [keyword.text for keyword in keywords]
                dict["keywords"] = ''.join(keywords)
            elif len(keywords) ==1:
                dict["keywords"] = keywords[0].text
            else:
                dict["keywords"] = None
                
            origin_title = self.driver.find_elements(by=By.XPATH, value='//*[@id="container"]/div[5]/div[1]/div[2]/table/tbody/tr[4]/td/a')
            
            if len(origin_title) > 0 :
                origin_title = origin_title[0].text if origin_title else None
                origin_title = origin_title.split('/')[0] 
                dict["origin_title"] = origin_title
            else:
                dict["origin_title"] = None

            page = self.driver.find_element(by=By.XPATH, value='//div[@class="box_detail_content"]/table/tbody').text
            page_pattern = r"\d{1,4}쪽"
            page = re.findall(page_pattern, page)[0]
            dict["page"] = int(page.rstrip('쪽'))

            

            #introduction => 따로 저장, 책에 대한 텍스트 정보들을 모두 수집해야 함
            #이 데이터를 text 분석해서 유사도를 구하는 작업을 할 예정
            # 아래 데이터는 검증이 필요함. 
            introductions = self.driver.find_elements(by=By.XPATH, value='//div[@class="box_detail_article"]')
            introduction = introductions[0].text
            introduction = re.sub('\\t', ' ', introduction)
            introduction = re.sub('\n', ' ', introduction)

            dict_intro["introduction"] = introduction
            

            return dict, dict_intro
        except Exception as e:
            # print("\n",e)
            # print("Here is Kyobo, => ", isbn)
            return None

# class ReviewUpdator():
#     def __init__():
#         pass

#     def getReviews(self):
#         # kyobo 리뷰 점수
#         kyobo_review_point = self.driver.find_elements(by=By.XPATH, value='//div[@class="popup_load"]/em')
#         dict["kyobo_review_point"] = float(kyobo_review_point[0].text) if kyobo_review_point else 0.0

#         #kyobo review
#         # kyobo_review = 

#         #aladin_review_point
#         aladin_review_point = self.driver.find_elements(by=By.XPATH, value='//*[@id="wa_product_top1_wa_Top_Ranking_pnlRanking"]/div[2]/a[2]')
#         dict["aladin_review_point"] = float(aladin_review_point[0].text) if aladin_review_point else 0.0



if __name__ == "__main__":

    #argparse 셋팅하기

    getbook = BookDBUpdater()
    getbook.getBookData()