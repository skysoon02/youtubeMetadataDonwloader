from config import *
from VideoListDownloader import VideoListDownloader
from VideoDownloader import VideoDownloader

import os
import argparse
from multiprocessing import Process, Queue
from datetime import datetime, timedelta

import pymysql
from sqlalchemy import create_engine
from sshtunnel import SSHTunnelForwarder

import pandas as pd


def get_DB(DB_NAME):
    with SSHTunnelForwarder(
        (DB_ENV['SSH_HOST'], DB_ENV['SSH_PORT']),
        ssh_username=DB_ENV['SSH_USER'],
        ssh_password=DB_ENV['SSH_PASSWORD'],
        remote_bind_address=(DB_ENV['HOST'], DB_ENV['PORT'])
    ) as tunnel:
        with pymysql.connect(
            host='127.0.0.1', # tunnel.local_bind_host,
            port=tunnel.local_bind_port,
            user=DB_ENV['USER'],
            password=DB_ENV['PASSWORD'],
            database=DB_ENV['DATABASE'],
            charset='utf8mb4'
        ) as conn:
            with conn.cursor() as cur:
                DB_TABLE = pd.read_sql(f'SELECT * FROM {DB_NAME};', conn)
                
    return DB_TABLE

def filter_channel_id(df, channel_id_column_name, channel_id_lst):
    return df[df[channel_id_column_name].isin(channel_id_lst)].reset_index(drop=True)

def main(args):    
    comment_flag = False
    lastDownloadTime = None
    
    c_id_lst = args.channel_id_lst
    ORI_CHANNEL_TABLE = get_DB('CHANNEL_TABLE')
    CHANNEL_TABLE = filter_channel_id(ORI_CHANNEL_TABLE, 'ID', c_id_lst)
    
    while True:
        CONTENT_TABLE = get_DB('CONTENT_TABLE')
        CONTENT_REVISED_TABLE = get_DB('CONTENT_REVISED_TABLE')
        CHANNEL_FOLLOWER_CNT_TABLE = get_DB('CHANNEL_FOLLOWER_CNT_TABLE')
        VIDEO_URL_TABLE = filter_channel_id(get_DB('VIDEO_URL_TABLE'), 'CHANNEL_TABLE_ID', c_id_lst)
        
        ### (1) Download new video URLs of channels
        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
        print('### Start downloading video URLs\n')
        
        processes = []
        for i, row in CHANNEL_TABLE.iterrows():
            videoListDownloader = VideoListDownloader({
                'flag': i == 0,  'id': row.ID, 'name': row.CHANNEL_NAME, 'URL': row.CHANNEL_URL, 
                'CHANNEL_TABLE': CHANNEL_TABLE, 'ORI_CHANNEL_TABLE': ORI_CHANNEL_TABLE, 
                'VIDEO_URL_TABLE': VIDEO_URL_TABLE, 'CHANNEL_FOLLOWER_CNT_TABLE': CHANNEL_FOLLOWER_CNT_TABLE
            })
            
            process = Process(target=videoListDownloader.download)
            process.start()
            processes.append(process)

        for process in processes:
            process.join()
            
        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
        print('### Done downloading video URLs\n')

        ### (2) Download videos' metadatas and thumbnails
        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
        print('### Start downloading video metadatas\n')
        
        toDownloadVideoURLs = list(VIDEO_URL_TABLE['YOUTUBE_URL'])
        
        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
        print('The number of entire URLs: {0}'.format(len(toDownloadVideoURLs)))

        que = Queue()   #URL들을 chunK_size로 나눠서 프로세스 큐에 넣기
        for i in range(number_of_process):            
            que.put(toDownloadVideoURLs[
                i*len(toDownloadVideoURLs)//number_of_process : 
                (i+1)*len(toDownloadVideoURLs)//number_of_process
            ])

        processes = []
        for i in range(number_of_process):
            videoDownloader = VideoDownloader({
                'CONTENT_TABLE': CONTENT_TABLE, 
                'CONTENT_REVISED_TABLE': CONTENT_REVISED_TABLE
            })
            
            process = Process(target=videoDownloader.download, args=(que, ))
            processes.append(process)
            process.start()

        for process in processes:
            process.join()
        que.close()
        
        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
        print('### Done downloading video metadatas\n')

        ### (3) Download videos' comments
        if comment_flag:
            ### FIXME: 바꿔주기
            # 댓글을 다운로드 받은 적이 있고, 마지막으로 댓글을 받은지 아직 일정 시간이 지나지 않았다면
            # if lastDownloadTime != None and lastDownloadTime + timedelta(days=periodDownloadComments) > datetime.now():
            if lastDownloadTime != None and lastDownloadTime + timedelta(hours=2) > datetime.now():
                continue

            lastDownloadTime = datetime.now()
            print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
            print('Start downloading video comments')

            que = Queue()   # URL들을 chunK_size로 나눠서 프로세스 큐에 넣기
            for i in range(number_of_process):
                que.put(toDownloadVideoURLs[
                    i*len(toDownloadVideoURLs)//number_of_process : 
                    (i+1)*len(toDownloadVideoURLs)//number_of_process
                ])

            processes = []
            for i in range(number_of_process):
                videoDownloader = VideoDownloader({
                    'CONTENT_TABLE': CONTENT_TABLE,
                    'CONTENT_REVISED_TABLE': CONTENT_REVISED_TABLE
                }, getCommentsOpt=True)
                process = Process(target=videoDownloader.download, args=(que, ))
                processes.append(process)
                process.start() 

            for process in processes:
                process.join()
            que.close()
            
            print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
            print('### Done downloading video comments\n')
            
        comment_flag = True


if __name__ == '__main__':
    ## Get 'YouTube channel name' using argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--channel_id_lst', 
        type=int,
        nargs='+', 
        default=list(range(1,27)),
        help="Input CHANNEL_TABLE 'ID' values with one space"
    )
    
    args = parser.parse_args(); print(f"args: {args}")
    
    main(args)