from config import *

import yt_dlp
import threading
import os
import json
import requests
from datetime import datetime
import multiprocessing

import codecs



class VideoDownloader():
    def __init__(self, getCommentsOpt=False):
        self.getCommentsOpt = getCommentsOpt
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
        
        
    def download(self, toDownloadVideoURLs):
        self.processName = multiprocessing.current_process().name
        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
        print('Start downloading video metadatas: ', self.processName)

        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download(toDownloadVideoURLs)

        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
        print('Successfully downloaded: ', self.processName)
        

    def postprocessor_hook(self, d):
        if d['status'] == 'started':    #비디오 다운로드를 시작하는 시점. 비디오를 다운로드 하지 않더라도 실행 됨
            thread_save = threading.Thread(target=self.save(d))
            thread_save.start()
    

    class Logger:
        def debug(self, msg):
            pass
            
        def info(self, msg):
            pass

        def warning(self, msg):
            print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
            print(msg)

        def error(self, msg):
            print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
            print(msg)
    
    
    def listToStr(self, list):
        string = ''
        for feature in list:
            string += feature + '\t'
        return string[:-1] + '\n'


    def save_CONTENT_METADATA(self, d):
        filePath = path_metadata + '/metadata_' + d['info_dict']['id'] + 'tsv'
        data = self.listToStr([str(d['info_dict']['id']), str(d['info_dict']['title']), 
                f"https://i.ytimg.com/vi/{d['info_dict']['id']}/hqdefault.jpg", str(d['info_dict']['duration']), str(d['info_dict']['duration_string']), 
                str(d['info_dict']['categories']), str(d['info_dict']['tags']), str(d['info_dict']['upload_date']), str(d['info_dict']['description'])])
        if not os.path.isfile(filePath):
            with codecs.open(filePath, 'w', encoding='UTF-8-sig') as f:
                f.write(data)
        else:
            with codecs.open(filePath, 'r', encoding='UTF-8-sig') as f:
                lines = f.readlines()
            if lines[-1] != data:
                with codecs.open(filePath, 'w', encoding='UTF-8-sig') as f:
                    f.write(data)


    def save_CONTENT_DETAIL(self, d):
        filePath = path_detail + '/detail_' + d['info_dict']['id'] + 'tsv'
        data = self.listToStr([str(d['info_dict']['view_count']), str(d['info_dict']['comment_count']), str(d['info_dict']['like_count'])])
        with codecs.open(filePath, 'a', encoding='UTF-8-sig') as f:
            f.write(data)


    def save_CONTENT_THUMBNAIL(self, thumbnailURL, videoName):
        try:
            response = requests.get(thumbnailURL, verify=False, timeout=10)   #썸네일 다운로드
        except:
            print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')  #debug
            print(self.PID, end=' ')
            print('Thumbnail request was time out: ' + videoName)           #debug
            return

        filePathLatest = path_thumbnail + '/' + videoName + '_latest.jpg'
        filePath = path_thumbnail + '/' + videoName + datetime.now().strftime('_%Y-%m-%d %H-%M-%S.jpg')
        if not os.path.isfile(filePathLatest):    #해당 비디오의 썸네일을 처음으로 다운로드하는 경우
            with open(filePathLatest, 'wb') as f:
                f.write(response.content)
            with open(filePath, 'wb') as f:
                f.write(response.content)
            return
        else:
            f_latest = open(filePathLatest, 'rb')
            if response.content != f_latest.read(): #저장되어있던 썸네일과 다운로드 받은 썸네일이 다른 경우, 즉 썸네일이 바뀐 경우
                f_latest.close()
                with open(filePathLatest, 'wb') as f:
                    f.write(response.content)
                with open(filePath, 'wb') as f:
                    f.write(response.content)
                print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')  #debug
                print('Thumbnail updated: ' + videoName)                        #debug
            else:
                f_latest.close()
            
                

    def save_COMMENT_TABLE(self, d):
        filePath = path_comment + '/comment_' + d['info_dict']['id'] + datetime.now().strftime('_%Y-%m-%d %H-%M-%S.json')
        with codecs.open(filePath, 'w', encoding='UTF-8-sig') as f:
            json.dump(d['info_dict']['comments'], f, indent=4, ensure_ascii=False)


    def save(self, d): 
        video_name = d['info_dict']['id']
        thumbnail_url = f'https://i.ytimg.com/vi/{video_name}/hqdefault.jpg'
        
        self.save_CONTENT_METADATA(d)
        self.save_CONTENT_DETAIL(d)
        self.save_CONTENT_THUMBNAIL(thumbnail_url, video_name)

        # 댓글을 다운로드 하는 경우
        if self.getCommentsOpt == True: 
            self.save_COMMENT_TABLE(d)
            