from config import *

import yt_dlp
import threading
import os
import json
import requests
import base64
from PIL import Image
from io import BytesIO
from datetime import datetime
from urllib.request import urlopen
import multiprocessing

import pymysql
from sqlalchemy import create_engine, text
from sshtunnel import SSHTunnelForwarder

import pandas as pd
import numpy as np


class VideoDownloader():
    def __init__(self, data, getCommentsOpt=False):
        self.getCommentsOpt = getCommentsOpt
        self.CONTENT_TABLE = data['CONTENT_TABLE']
        self.CONTENT_REVISED_TABLE = data['CONTENT_REVISED_TABLE']

        self.ydl_opts = {
            'lazy_playlist': True,
            'noplaylist': True, #need to check
            'skip_download': True,
            'getcomments': getCommentsOpt,
            #'writethumbnail': True,
            #'paths': {'home': path_thumbnail + '/' + datetime.now().strftime('%Y-%m-%d %H-%M-%S')},
            #'writedescription': True,
            #'writeinfojson': True,
            #'writesubtitles': True,
            'ignoreerrors': True,
            'quiet': True, # False = log
            'postprocessor_hooks': [self.postprocessor_hook],
            'logger': self.Logger()
        }
        
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

    def download(self, que):     
        while not que.empty():
            toDownloadVideoURLs = que.get()                                 #debug
            self.processName = multiprocessing.current_process().name
            print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')  #debug
            print('Download start: ', self.processName)
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                ydl.download(toDownloadVideoURLs)
        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')      #debug
        print('Download finish: ', self.processName)                        #debug
        
    def postprocessor_hook(self, d):
        if d['status'] == 'started':    #비디오 다운로드를 시작하는 시점. 비디오를 다운로드 하지 않더라도 실행 됨
            thread_save = threading.Thread(target=self.save(d))
            thread_save.start()
    
    class Logger:
        # def __init__(self):
        #     self.log_file = 'yt_dlp_log.txt'  # 로그 파일 이름 정의

        def debug(self, msg):
            pass
            # with open(self.log_file, 'a') as file_handler:
            #     file_handler.write(datetime.now().strftime('[%Y-%m-%d %H:%M:%S] ') + msg + '\n')

        def info(self, msg):
            pass

        def warning(self, msg):
            print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
            print(msg)

        def error(self, msg):
            print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
            print(msg)

    def save_CONTENT_TABLE(self, engine, d):        
        # 동영상에서 바뀌지 않는 정보를 1번만 저장하도록, 기존 DB에 id 정보가 있으면 skip
        if d['info_dict']['id'] not in list(self.CONTENT_TABLE['C_ID']):
            with engine.connect() as conn:
                conn.execute(text(
                    f'''INSERT INTO CONTENT_TABLE (C_ID, C_TITLE, C_DESCRIPTION, C_THUMBNAIL_URL, C_DURATION, C_DURATION_STRING, C_CATEGORIES, C_TAGS, C_UPLOAD_DATE)
                        VALUES {
                            str(d['info_dict']['id']), str(d['info_dict']['title']), str(d['info_dict']['description'].encode('utf-8').decode('utf-8')), 
                            f"https://i.ytimg.com/vi/{d['info_dict']['id']}/hqdefault.jpg", str(d['info_dict']['duration']), str(d['info_dict']['duration_string']), 
                            str(d['info_dict']['categories']), str(d['info_dict']['tags']), str(d['info_dict']['upload_date'])
                        }
                    '''
                )); conn.commit()
                
                content_table_db = pd.read_sql('SELECT * FROM CONTENT_TABLE;', conn)
                ID = content_table_db[content_table_db['C_ID'] == d['info_dict']['id']]['ID'].values[0]
        
        else:
            ID = self.CONTENT_TABLE[self.CONTENT_TABLE['C_ID'] == d['info_dict']['id']]['ID'].values[0]
        
        return ID
    
    def save_CONTENT_REVISED_TABLE(self, engine, d):
        # CONTENT_TABLE에서 변동된 내용이 있다면, CONTENT_REVISED_TABLE에 Append
        pivot_df = self.CONTENT_REVISED_TABLE[
            self.CONTENT_REVISED_TABLE['C_ID'] == str(d['info_dict']['id'])
        ].sort_values('TIME_STAMP').tail(1).drop(columns=['ID', 'TIME_STAMP'])
        
        if pivot_df.shape[0] == 0:
            pivot_df = self.CONTENT_TABLE[
                self.CONTENT_TABLE['C_ID'] == str(d['info_dict']['id'])
            ].sort_values('TIME_STAMP').tail(1).drop(columns=['ID', 'TIME_STAMP'])
        
        current_df = pd.DataFrame({
            'C_ID': [str(d['info_dict']['id'])],
            'C_TITLE': [str(d['info_dict']['title'])],
            'C_DESCRIPTION': [str(d['info_dict']['description'].encode('utf-8').decode('utf-8'))],
            'C_THUMBNAIL_URL': [f"https://i.ytimg.com/vi/{d['info_dict']['id']}/hqdefault.jpg"],
            'C_DURATION': [str(d['info_dict']['duration'])],
            'C_DURATION_STRING': [str(d['info_dict']['duration_string'])],
            'C_CATEGORIES': [str(d['info_dict']['categories'])],
            'C_TAGS': [str(d['info_dict']['tags'])],
            'C_UPLOAD_DATE': [str(d['info_dict']['upload_date'])]
        })
        
        TF1 = list(pivot_df['C_ID']) == list(current_df['C_ID'])
        TF2 = list(pivot_df['C_TITLE']) == list(current_df['C_TITLE'])
        TF3 = list(pivot_df['C_DESCRIPTION']) == list(current_df['C_DESCRIPTION'])
        TF4 = list(pivot_df['C_THUMBNAIL_URL']) == list(current_df['C_THUMBNAIL_URL'])
        TF5 = list(pivot_df['C_DURATION']) == list(current_df['C_DURATION'])
        TF6 = list(pivot_df['C_DURATION_STRING']) == list(current_df['C_DURATION_STRING'])
        TF7 = list(pivot_df['C_CATEGORIES']) == list(current_df['C_CATEGORIES'])
        TF8 = list(pivot_df['C_TAGS']) == list(current_df['C_TAGS'])
        TF9 = list(pivot_df['C_UPLOAD_DATE']) == list(current_df['C_UPLOAD_DATE'])
        
        # 하나라도 변동 사항이 있다면, CONTENT_REVISED_TABLE에 추가
        if TF1 * TF2 * TF3 * TF4 * TF5 * TF6 * TF7 * TF8 * TF9 == 0: 
            current_df.to_sql('CONTENT_REVISED_TABLE', con=engine, if_exists='append', index=False)
            
            print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')  #debug
            print('Content updated: ' + d['info_dict']['id'])               #debug

    def save_CONTENT_DETAIL_TABLE(self, engine, d, CONTENT_TABLE_ID):
        # 동영상에서 지속적으로 append 해야 하는 데이터 (조회 수, 댓글 수 등등)
        with engine.connect() as conn:
            conn.execute(text(
                f'''INSERT INTO CONTENT_DETAIL_TABLE (CONTENT_TABLE_ID, C_VIEW_COUNT, C_COMMENT_COUNT, C_LIKE_COUNT)
                    VALUES {
                        CONTENT_TABLE_ID, str(d['info_dict']['view_count']), 
                        str(d['info_dict']['comment_count']), str(d['info_dict']['like_count'])
                    }
                '''
            )); conn.commit() 

    def save_CONTENT_THUMBNAIL_TABLE(self, engine, thumbnail_url, video_name, CONTENT_TABLE_ID):
        content_thumbnail_db = pd.read_sql('SELECT * FROM CONTENT_THUMBNAIL_TABLE;', engine).sort_values('TIME_STAMP')
        exist_flag = content_thumbnail_db['CONTENT_TABLE_ID'].isin([CONTENT_TABLE_ID]).sum()
        
        ## 해당 비디오의 Thumbnail을 처음으로 다운로드 하는 경우
        try:
            new_thumbnail_image = requests.get(thumbnail_url, verify=False, timeout=10).content
        except:
            print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')                      #debug
            print('Thumbnail request was time out: ' + video_name, ' at ', self.processName)    #debug
            return
        
        if not exist_flag:
            thumbnail_df = pd.DataFrame({'CONTENT_TABLE_ID': [CONTENT_TABLE_ID], 'C_THUMBNAIL_IMAGE': [new_thumbnail_image]})
            thumbnail_df.to_sql('CONTENT_THUMBNAIL_TABLE', con=engine, if_exists='append', index=False)
            return
        
        pivot_df = content_thumbnail_db[content_thumbnail_db['CONTENT_TABLE_ID'].isin([CONTENT_TABLE_ID])]
        origin_thumbnail_image = list(pivot_df['C_THUMBNAIL_IMAGE'])[-1]
                    
        ## 저장된 Thumbnail과 다운로드 받은 Thumbnail이 다른 경우, 즉 Thumbnail이 바뀐 경우
        if new_thumbnail_image != origin_thumbnail_image:                
            thumbnail_df = pd.DataFrame({'CONTENT_TABLE_ID': [CONTENT_TABLE_ID], 'C_THUMBNAIL_IMAGE': [new_thumbnail_image]})
            thumbnail_df.to_sql('CONTENT_THUMBNAIL_TABLE', con=engine, if_exists='append', index=False)
            
            print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')  #debug
            print('Thumbnail updated: ' + video_name)                       #debug
                
    def save_COMMENT_TABLE(self, engine, d, CONTENT_TABLE_ID):
        comment_df = pd.DataFrame(d['info_dict']['comments'])
        if comment_df.shape[0] >= 1: # 컨텐츠 내에 댓글이 포함된 경우
            comment_df['CONTENT_TABLE_ID'] = CONTENT_TABLE_ID
            comment_df = comment_df[['CONTENT_TABLE_ID', 'id', 'parent', 'author_id', 'author', 'text', 'like_count', '_time_text', 'timestamp']].reset_index(drop=True)
            comment_df.columns = ['CONTENT_TABLE_ID', 'COMMENT_ID', 'COMMENT_PARENT_ID', 'USER_ID', 'USER_NAME', 'COMMENT', 'LIKE_COUNT', 'TIME_TEXT', 'UNIX_TIMESTAMP']
            comment_df.to_sql('COMMENT_TABLE', con=engine, if_exists='append', index=False)
            
    def save(self, d): 
        video_name = d['info_dict']['id']
        thumbnail_url = f'https://i.ytimg.com/vi/{video_name}/hqdefault.jpg'
        
        engine, tunnel = self.get_tunnel_engine()
        
        CONTENT_TABLE_ID = self.save_CONTENT_TABLE(engine, d)
        self.save_CONTENT_REVISED_TABLE(engine, d)
        self.save_CONTENT_DETAIL_TABLE(engine, d, CONTENT_TABLE_ID)
        self.save_CONTENT_THUMBNAIL_TABLE(engine, thumbnail_url, video_name, CONTENT_TABLE_ID)

        # 댓글을 다운로드 하는 경우
        if self.getCommentsOpt == True: 
            self.save_COMMENT_TABLE(engine, d, CONTENT_TABLE_ID)
            
        tunnel.stop()