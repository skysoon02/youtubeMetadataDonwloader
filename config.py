'''
References
https://github.com/yt-dlp/yt-dlp#embedding-yt-dlp
https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/YoutubeDL.py
https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/downloader/common.py
'''

startDate = '20241210'          #값 변경 뒤에는 path_data를 삭제
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
    {'id': 3, 'name': 'sbs', 'URL': 'https://www.youtube.com/sbs8news/videos'}, #{'id': 3, 'name': 'sbs', 'URL': 'https://www.youtube.com/@sbsnews8/videos'},
    {'id': 4, 'name': 'tvchosun', 'URL': 'https://www.youtube.com/@tvchosunnews/videos'},
    {'id': 5, 'name': 'kbs', 'URL': 'https://www.youtube.com/@newskbs/videos'},
    {'id': 6, 'name': 'jtbc', 'URL': 'https://www.youtube.com/@jtbc_news/videos'},
    {'id': 7, 'name': 'channela', 'URL': 'https://www.youtube.com/@channelA-news/videos'},
    {'id': 8, 'name': 'msnbc', 'URL': 'https://www.youtube.com/@msnbc/videos'},
    {'id': 9, 'name': 'ABCNews', 'URL': 'https://www.youtube.com/@ABCNews/videos'},
    {'id': 10, 'name': 'AssociatedPress', 'URL': 'https://www.youtube.com/@AssociatedPress/videos'},
    {'id': 11, 'name': 'CBSNews', 'URL': 'https://www.youtube.com/@CBSNews/videos'},
    {'id': 12, 'name': 'CNN', 'URL': 'https://www.youtube.com/@CNN/videos'},
    {'id': 13, 'name': 'guardiannews', 'URL': 'https://www.youtube.com/@guardiannews/videos'},
    {'id': 14, 'name': 'NBCNews', 'URL': 'https://www.youtube.com/@NBCNews/videos'},
    {'id': 15, 'name': 'BBCNews', 'URL': 'https://www.youtube.com/@BBCNews/videos'},
    {'id': 16, 'name': 'NewsNation', 'URL': 'https://www.youtube.com/@NewsNation/videos'},
    {'id': 17, 'name': 'Reuters', 'URL': 'https://www.youtube.com/@Reuters/videos'},
    {'id': 18, 'name': 'wsj', 'URL': 'https://www.youtube.com/@wsj/videos'},
    {'id': 19, 'name': 'nypost', 'URL': 'https://www.youtube.com/@nypost/videos'},
    {'id': 20, 'name': 'washingtontimes', 'URL': 'https://www.youtube.com/@washingtontimes/videos'},
    {'id': 21, 'name': 'FoxNews', 'URL': 'https://www.youtube.com/@FoxNews/videos'},
    {'id': 22, 'name': 'breitbartnews92', 'URL': 'https://www.youtube.com/@breitbartnews92/videos'},
    {'id': 23, 'name': 'BlazeTV', 'URL': 'https://www.youtube.com/@BlazeTV/videos'},
    {'id': 24, 'name': 'CBNnewsonline', 'URL': 'https://www.youtube.com/@CBNnewsonline/videos'},
    {'id': 25, 'name': 'NewsmaxTV', 'URL': 'https://www.youtube.com/@NewsmaxTV/videos'},
    {'id': 26, 'name': 'oann', 'URL': 'https://www.youtube.com/@oann/videos'},
]
