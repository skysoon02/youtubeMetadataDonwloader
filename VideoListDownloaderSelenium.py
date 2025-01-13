from config import *

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import jsonlines
import re
from datetime import datetime
import time




def download(channel):
    url = channel['URL']
    name = channel['name']
    file = jsonlines.open('./videoList/'+name+'.jsonl', 'a')

    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument('--headless')
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--max_old_space_size=16384")
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options) 
    driver.get(url)
    time.sleep(5)

    cnt = 0
    while True:
        #driver.find_element_by_tag_name('body').send_keys(Keys.END)
        driver.execute_script("window.scrollTo(0,document.documentElement.scrollHeight)")
        time.sleep(3)
        for i in range(cnt+1, cnt+31):
            #{"webpage_url": "https://www.youtube.com/watch?v=1J8BxgJjfEg", "title": "무안공항 여객기 참사...현재 상황은? / YTN", "upload_dated": "20241229", "mtime": "2024-12-30 18-51-43"}
            #print('/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-rich-grid-renderer/div[6]/ytd-rich-item-renderer[{0}]/div/ytd-rich-grid-media/div[1]/div[3]/div[2]/h3/a'.format(i))
            element = driver.find_element(By.XPATH, '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-rich-grid-renderer/div[6]/ytd-rich-item-renderer[{0}]/div/ytd-rich-grid-media/div[1]/div[3]/div[2]/h3/a'.format(i))
            matches = re.findall(r'회\s(\S+)', element.get_attribute('aria-label'))
            upload_dated = matches[-1]
            if upload_dated=='7개월':
                return

            videoInfo = {"webpage_url": element.get_attribute('href'), "title": element.get_attribute('title'), "upload_dated": upload_dated, "mtime": datetime.now().strftime("%Y-%m-%d %H-%M-%S")}
            file.write(videoInfo)
        cnt+=30
        
        driver.execute_script("""
            const elements = document.querySelectorAll('ytd-rich-item-renderer');
            elements.forEach(el => el.remove());
        """)
        driver.execute_script("window.localStorage.clear();")
        driver.execute_script("window.sessionStorage.clear();")
            
    #print(a.title)
#//*[@id="video-title-link"]
#//*[@id="video-title-link"]

#/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-rich-grid-renderer/div[6]/ytd-rich-item-renderer[2]/div/ytd-rich-grid-media/div[1]/div[3]/div[2]/h3/a

#/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-rich-grid-renderer/div[6]/ytd-rich-item-renderer[1]/div/ytd-rich-grid-media/div[1]/div[3]/div[2]/h3/a/yt-formatted-string
#/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-rich-grid-renderer/div[6]/ytd-rich-item-renderer[2]/div/ytd-rich-grid-media/div[1]/div[3]/div[2]/h3/a/yt-formatted-string
#/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-rich-grid-renderer/div[6]/ytd-rich-item-renderer[5]/div/ytd-rich-grid-media/div[1]/div[3]/div[2]/h3/a/yt-formatted-string
#/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-rich-grid-renderer/div[6]/ytd-rich-item-renderer[34]/div/ytd-rich-grid-media/div[1]/div[3]/div[2]/h3/a

#30개씩
for channel in channels:
    try:
        download(channel)
    except Exception as e:
        print(channel)
        print(e)