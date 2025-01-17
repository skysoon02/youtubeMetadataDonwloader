from config import *
import json
import jsonlines
import os

def addChannelToMetadata():
    for channel in channels:
        videoListPath = path_videoList + '/videoList_' + channel['name'] + '.jsonl'
        with jsonlines.open(videoListPath, 'r') as f:
            for video in f.iter():
                metadataPath = path_metadata+'/metadata_'+video['webpage_url'][-11:]+'.jsonl'
                print(metadataPath)
                if os.path.isfile(metadataPath):
                    data = None
                    with open(metadataPath, 'r', encoding='UTF-8-sig') as file:
                        data = json.load(file)
                    data['channelId'] = channel['id']
                    data['channelName'] = channel['name']
                    with open(metadataPath, 'w') as file:
                        json.dump(data, file)