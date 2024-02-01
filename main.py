from config import *
from VideoListDownloader import VideoListDownloader
from VideoDownloader import VideoDownloader

import os
import jsonlines
from multiprocessing import Process, Pool, Queue
from datetime import datetime, timedelta


def init():
    if not os.path.isdir(path_data):
        os.makedirs(path_data)
    if not os.path.isdir(path_videoList):
        os.makedirs(path_videoList)
    if not os.path.isdir(path_followerCount):
        os.makedirs(path_followerCount)
    if not os.path.isdir(path_metadata):
        os.makedirs(path_metadata)
    if not os.path.isdir(path_detail):
        os.makedirs(path_detail)
    if not os.path.isdir(path_thumbnail):
        os.makedirs(path_thumbnail)
    if not os.path.isdir(path_comment):
        os.makedirs(path_comment)

def worker_VideoListDownloader(channel):
    videoListDownloader = VideoListDownloader(channel)
    videoListDownloader.download()
    videoListDownloader.followerCountDownload()
    print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
    print('Successfully downloaded video URLs: {0}'.format(channel['name']))


def debug():
    pass


def main():
    init()
    lastDownloadTime = None

    while True:
        ### (1) Download new video URLs of channels
        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
        print('Start downloading video URLs\n')
        
        with Pool(number_of_process) as pool:
            pool.map(worker_VideoListDownloader, channels)
            
        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
        print('Successfully downloaded all video URLs\n')

        ### (2) Download videos' metadatas and thumbnails
        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
        print('Start downloading video metadatas\n')

        que = Queue()
        toDownloadVideoURLs = []    #여러 *.txt 파일의 URL 전부 읽기
        for channel in channels:
            path = path_videoList + '/videoList_' + channel['name'] + '.jsonl'
            with jsonlines.open(path, 'r') as f:
                for data in f.iter():
                    toDownloadVideoURLs.append(data['webpage_url'])
        
        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
        print('The number of entire URLs: {0}'.format(len(toDownloadVideoURLs)))
        
        if lastDownloadTime == None or lastDownloadTime + timedelta(hours=periodDownloadComments) < datetime.now():
            getCommentsOpt = True
            lastDownloadTime = datetime.now()
        else:
            getCommentsOpt = False

        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
        print('This time we will download comments too' if getCommentsOpt else 'This time we will not download comments')
                
        que = Queue()
        for url in toDownloadVideoURLs:
            que.put(url)
        
        processes=[]
        for i in range(number_of_process):
            videoDownloader = VideoDownloader(getCommentsOpt)            
            process = Process(target=videoDownloader.download, args=(que, ))
            processes.append(process)
            process.start()

        for process in processes:
            process.join()
        
        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
        print('Successfully donwloaded all video metadatas\n')


if __name__ == '__main__':
    #debug()
    main()