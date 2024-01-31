from config import *
from VideoListDownloader import VideoListDownloader
from VideoDownloader import VideoDownloader

import os
from multiprocessing import Pool
from datetime import datetime, timedelta


def init():
    if not os.path.isdir(path_data):
        os.makedirs(path_data)
    if not os.path.isdir(path_videoList):
        os.makedirs(path_videoList)
    if not os.path.isdir(path_followerCount):
        os.makedirs(path_followerCount)
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

        return
        ### (2) Download videos' metadatas and thumbnails
        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
        print('Start downloading video metadatas\n')

        toDownloadVideoURLs = []    #여러 *.txt 파일의 URL 전부 읽기
        for channel in channels:
            path = path_videoList + '/videoList_' + channel['name'] + '.tsv'
            f = open(path, 'r')
            lines = f.readlines()
            for line in lines:
                toDownloadVideoURLs.append(line.split('\t')[0])
        
        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
        print('The number of entire URLs: {0}'.format(len(toDownloadVideoURLs)))

        videoDownloader = VideoDownloader()
        with Pool(number_of_process) as pool:
            pool.map(videoDownloader.download, toDownloadVideoURLs)
        
        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
        print('Done downloading video metadatas\n')

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
    #debug()
    main()