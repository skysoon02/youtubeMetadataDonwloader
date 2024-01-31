import pymysql
from sqlalchemy import create_engine
from sshtunnel import SSHTunnelForwarder

'''
References
https://github.com/yt-dlp/yt-dlp#embedding-yt-dlp
https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/YoutubeDL.py
https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/downloader/common.py
'''

startDate = '20240123'          #값 변경 뒤에는 path_videoList 폴더를 삭제
periodDownloadComments = 3

number_of_process = 16
chunk_size = 100

## DB Setting
DB_ENV = {
    'SSH_HOST': '143.248.249.232',
    'SSH_PORT': 3221,
    'SSH_USER': 'youtube',
    'SSH_PASSWORD': 'youtube',
    'HOST': 'localhost',
    'PORT': 3306,
    'USER': 'root',
    'PASSWORD': '',
    'DATABASE': 'YOUTUBE_2024'
}