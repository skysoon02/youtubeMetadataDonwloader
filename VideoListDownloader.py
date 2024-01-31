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
        self.flag = channel['flag']
        self.CHANNEL_TABLE = channel['CHANNEL_TABLE']
        self.ORI_CHANNEL_TABLE = channel['ORI_CHANNEL_TABLE']
        self.VIDEO_URL_TABLE = channel['VIDEO_URL_TABLE']
        self.CHANNEL_FOLLOWER_CNT_TABLE = channel['CHANNEL_FOLLOWER_CNT_TABLE']
        self.toUpdateVideoURLs = []
        
    def get_tunnel_engine(self):
        tunnel = SSHTunnelForwarder(
            (DB_ENV['SSH_HOST'], DB_ENV['SSH_PORT']),
            ssh_username=DB_ENV['SSH_USER'],
            ssh_password=DB_ENV['SSH_PASSWORD'],
            remote_bind_address=(DB_ENV['HOST'], DB_ENV['PORT'])
        ); tunnel.start()
        
        engine = create_engine(
            f"mysql+pymysql://{DB_ENV['USER']}:{DB_ENV['PASSWORD']}@{'127.0.0.1'}:{tunnel.local_bind_port}/{DB_ENV['DATABASE']}",
            pool_size=10, max_overflow=10
        )
        
        return engine, tunnel

    def save_CHANNEL_FOLLOWER_CNT_TABLE(self, engine):
        lastDownloadTime = None
        
        try:
            lastDownloadTime = self.CHANNEL_FOLLOWER_CNT_TABLE[
                self.CHANNEL_FOLLOWER_CNT_TABLE['CHANNEL_TABLE_ID'] == self.id
            ].sort_values('TIME_STAMP')['TIME_STAMP'].iloc[-1]
        except: pass
        
        if (lastDownloadTime == None) or lastDownloadTime + timedelta(hours=1) < datetime.now():
            try:
                for _, row in self.ORI_CHANNEL_TABLE.iterrows():
                    response = requests.get(row.CHANNEL_URL, verify=False, timeout=10)
                    startIdx = response.text.find('구독자')
                    endIdx = response.text.find('만명', startIdx)
                    try: follower_count = float(response.text[startIdx+4:endIdx])*10000
                    except: continue
                    
                    with engine.connect() as conn:
                        conn.execute(text(
                            f'''INSERT INTO CHANNEL_FOLLOWER_CNT_TABLE (CHANNEL_TABLE_ID, FOLLOWER_COUNT)
                                VALUES {row.ID, follower_count}'''
                        )); conn.commit()
                    
                    print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
                    print('Saving data to CHANNEL_FOLLOWER_CNT_TABLE DB')
                
            except:
                print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')  #debug
                print('Follower count request was time out: ' + self.id)        #debug
                return
                        
    def save_VIDEO_URL_TABLE(self, engine):
        with engine.connect() as conn:
            for url in self.toUpdateVideoURLs:
                conn.execute(text(
                    f'''INSERT INTO VIDEO_URL_TABLE (CHANNEL_TABLE_ID, YOUTUBE_URL)
                        VALUES {self.id, url[0]}'''
                ))
            conn.commit()
            
            print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
            print('Saving data to VIDEO_URL_TABLE DB')

    def download(self):
        engine, tunnel = self.get_tunnel_engine()
        
        if self.flag: # 한 번에 모든 채널의 정보를 받아오므로, 한 번만 실행하도록 셋팅
            self.save_CHANNEL_FOLLOWER_CNT_TABLE(engine)
        
        if self.id in self.VIDEO_URL_TABLE['CHANNEL_TABLE_ID'].unique(): # 기존 비디오 리스트 파일이 있어서 추가하면 되는 경우
            self.updatedVideoListDownload()
        else:                                                            # 비디오 리스트를 처음부터 만드는 경우
            self.dateAfterVideoListDownload()

        #다운로드 쓰레드 실행 및 대기
        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
        print('Start downloading video URLs of ' + self.name)
        thread = threading.Thread(target=yt_dlp.YoutubeDL(self.ydl_opts).download, args=([self.URL]))
        thread.start()
        thread.join()

        #파일에 저장
        self.toUpdateVideoURLs.reverse()
        self.save_VIDEO_URL_TABLE(engine)
        
        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
        print('{0} video URls were updated at '.format(len(self.toUpdateVideoURLs)))
        
        tunnel.stop()

    #기존 비디오 리스트 파일이 있는 경우의 옵션
    def updatedVideoListDownload(self):
        pivot_df = self.VIDEO_URL_TABLE[
            self.VIDEO_URL_TABLE['CHANNEL_TABLE_ID'] == self.id
        ].sort_values('TIME_STAMP')
        
        pivotURL = pivot_df['YOUTUBE_URL'].iloc[-1]

        class Logger:
            def debug(self, msg):
                if msg == '[youtube] Extracting URL: ' + pivotURL:
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