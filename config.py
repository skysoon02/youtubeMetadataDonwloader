'''
References
https://github.com/yt-dlp/yt-dlp#embedding-yt-dlp
https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/YoutubeDL.py
https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/downloader/common.py
'''

startDate = '20240201'          #값 변경 뒤에는 path_videoList 폴더를 삭제
periodDownloadComments = 3*24

number_of_process = 16

path_data = './data'

#pathes for channel
path_videoList = './data/videoList'
path_followerCount = './data/followerCount'

#pathes for video
path_metadata = './data/metadata'
path_detail = './data/detail'
path_thumbnail = './data/thumbnail'
path_comment = './data/comment'

channels = [
    {'id': 1, 'name': 'ytn', 'URL': 'https://www.youtube.com/@ytnnews24/videos'},
    {'id': 2, 'name': 'mbc', 'URL': 'https://www.youtube.com/@MBCNEWS11/videos'},
    {'id': 3, 'name': 'sbs', 'URL': 'https://www.youtube.com/@sbsnews8/videos'},
    {'id': 4, 'name': 'tvchosun', 'URL': 'https://www.youtube.com/@tvchosunnews/videos'},
    {'id': 5, 'name': 'kbs', 'URL': 'https://www.youtube.com/@newskbs/videos'},
    {'id': 6, 'name': 'jtbc', 'URL': 'https://www.youtube.com/@jtbc_news/videos'},
    {'id': 7, 'name': 'channela', 'URL': 'https://www.youtube.com/@channelA-news/videos'}
]
