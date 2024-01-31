from config import *

import os
import yt_dlp
import threading
import requests
from datetime import datetime, timedelta

import pymysql
from sqlalchemy import create_engine, text
from sshtunnel import SSHTunnelForwarder

import pandas as pd


class VideoListDownloader():
    def __init__(self, channel):
        self.id = channel['id']
        self.name = channel['name']
        self.URL = channel['URL']
        self.videoListPath = path_videoList + '/videoList_' + channel['name'] + '.tsv'
        self.followerCountPath = path_followerCount + '/followerCount_' + channel['name'] + '.tsv'
        self.toUpdateVideoURLs = []

    def followerCountDownload(self):
        try:
            response = requests.get(self.URL, verify=False, timeout=10)
        except:
            print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
            print('Error: Follower count request was time out: ' + self.name)
            return
        try:
            startIdx = response.text.find('구독자')
            endIdx = response.text.find('만명', startIdx)
            follower_count = float(response.text[startIdx+4:endIdx])*10000
        except:
            print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
            print('Error: Failed to parse HTML: ' + self.name)
            return
        with open(self.followerCountPath, 'a') as f:
            f.write(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]') + '\t')
            f.write(str(follower_count) + '\n')


    def download(self):
        if os.path.isfile(self.videoListPath):           # 기존 비디오 리스트 파일이 있어서 추가하면 되는 경우
            self.updatedVideoListDownload()
        else:                                   # 비디오 리스트를 처음부터 만드는 경우
            self.dateAfterVideoListDownload()

        #다운로드 쓰레드 실행 및 대기
        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
        print('Start downloading video URLs of ' + self.name)
        thread = threading.Thread(target=yt_dlp.YoutubeDL(self.ydl_opts).download, args=([self.URL]))
        thread.start()
        thread.join()

        #파일에 저장
        with open(self.videoListPath, 'a') as f:
            self.toUpdateVideoURLs.reverse()
            for url in self.toUpdateVideoURLs:
                f.write(url[0]+'\t'+url[1]+'\t'+url[2]+'\n')
        
        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
        print('{0} video URLs were updated at: '.format(len(self.toUpdateVideoURLs)) + self.name)
        

    #기존 비디오 리스트 파일이 있는 경우의 옵션
    def updatedVideoListDownload(self):
        with open(self.videoListPath, 'r') as f:
            lines = f.readlines()
            pivotURL1 = lines[-1].split('\t')[0]
            pivotURL2 = lines[-2].split('\t')[0]
            pivotURL3 = lines[-3].split('\t')[0]

        class Logger:
            def debug(self, msg):
                if msg == '[youtube] Extracting URL: ' + pivotURL1 or \
                   msg == '[youtube] Extracting URL: ' + pivotURL2 or \
                   msg == '[youtube] Extracting URL: ' + pivotURL3:
                    exit()

            def warning(self, msg):
                print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
                print(msg)

            def error(self, msg):
                print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
                print(msg)
                    
        self.ydl_opts = {
            'lazy_playlist': True,
            'noplaylist': True, #need to check
            'skip_download': True,
            'quiet': True, # False = log
            'ignoreerrors': True,
            'postprocessor_hooks': [self.postprocessor_hook],
            'logger': Logger(),
        }

    #비디오 리스트 파일을 새로 만드는 경우의 옵션
    def dateAfterVideoListDownload(self):
        class Logger:
            def debug(self, msg):
                if msg.startswith('[download] ') and 'upload date is not in range' in msg:
                    print(msg)  #for debug
                    exit()
                    
            def warning(self, msg):
                print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
                print(msg)

            def error(self, msg):
                print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
                print(msg)

        self.ydl_opts = {
            'lazy_playlist': True,
            'noplaylist': True, #need to check
            'skip_download': True,
            'daterange': yt_dlp.utils.DateRange(startDate),
            'quiet': True, # False = log
            'ignoreerrors': True,
            'postprocessor_hooks': [self.postprocessor_hook],
            'logger': Logger(),
        }
    
    def postprocessor_hook(self, d):        
        if d['status'] == 'started':    #비디오 다운로드를 시작하는 시점. 비디오를 다운로드 하지 않더라도 실행 됨
            self.toUpdateVideoURLs.append([d['info_dict']['webpage_url'], d['info_dict']['upload_date'], datetime.now().strftime('%Y-%m-%d %H-%M-%S')])#