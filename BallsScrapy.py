import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

requests_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.88 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}
scrapy_url = "https://www.demo.com/?no=%s"

class ScrapyException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

def get_lottery_balls(lotteryNo:str):
    balls = {'blue': 0, 'red': [], 'lotteryNo': lotteryNo, 'lotteryDate': datetime.today()}
    r = requests.get(scrapy_url%lotteryNo, headers=requests_headers)
    r.encoding = r.apparent_encoding
    soup = BeautifulSoup(r.text, 'html.parser')
    kjqDom = soup.find('table', class_='kj_tablelist02') #中奖区域
    if kjqDom is None:
        raise ScrapyException("没有爬取到中奖区域")
    redBallSpans = kjqDom.find_all('li', class_='ball_red')
    for ball in redBallSpans:
        try:
            ballNo = ball.text
            balls['red'].append(int(ballNo))
        except:
            raise ScrapyException("爬取到一个非数字红球号:%s"%ballNo)
    blueBallSpan = kjqDom.find('li', class_='ball_blue')
    if blueBallSpan is not None:
        try:
            ballNo = blueBallSpan.text
            balls['blue'] = int(blueBallSpan.text)
        except:
            raise ScrapyException("爬取到一个非数字蓝球号:%s"%ballNo)
    if balls['blue'] == 0 or len(balls['red']) != 6:
        raise ScrapyException("爬取失败, 爬取结果非双色球规则:%s"%balls)
    tbodyDom = kjqDom.find('td', class_="td_title01")
    if tbodyDom:
        lotteryNoDom = tbodyDom.find('font', class_='cfont2').find('strong')
        if lotteryNoDom is not None:
            lotteryNo = lotteryNoDom.text
            balls['lotteryNo'] = "20" + lotteryNo if len(lotteryNo) == 5 else lotteryNo
        lotteryDateDom = tbodyDom.find('span', class_='span_right')
        dates = re.findall(r'(\d{4})年(\d{1,2})月(\d{1,2})日', lotteryDateDom.text)
        if dates is None:
            print("!!!!!!没有爬取到开奖日期, 开奖日期将设置为今天:%s"%balls['lotteryDate'])
        balls['lotteryDate'] = datetime(*list(map(int, dates[0])))
    else:
        print("!!!!无法爬取开奖期与开奖时间, 开奖期数将不会校准, 开奖日期将设置为今天:%s"%balls['lotteryDate'])
    return balls

if __name__ == '__main__':
    balls = get_lottery_balls('2024144')
    print(balls)