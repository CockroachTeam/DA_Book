# DA Book
### 데이터 분석 기반 독서 관리 서비스

## Requirement  
Selenium을 작동시키기 위해서는 자신의 브라우저에 맞는 WebDriver가 필요하다. 해당 시스템에는 ChromeDriver에서 테스트 하였다.  
[Chrome Driver 다운로드](https://chromedriver.chromium.org/downloads)  (브라우저에 맞는 버전 필요)


## Usage
 terminal에서 아래 코드를 순차적으로 실행한다.
```
>> pip install -r requirements.txt
>> cd crawling
>> python crawler.py
```
iteration이 돌때마다 __crawling/data__ 에 __BookInfo.csv__ 와 __BookIntro.csv__ 에 저장됨
