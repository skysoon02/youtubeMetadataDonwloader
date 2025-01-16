from config import *

import httpx
import json
import jsonlines
from datetime import datetime
import time

stopFlag = False


def startParser(videoDicts, channelName):
    file = jsonlines.open('./videoList/videoList_'+channelName+'.jsonl', 'a')
    for videoDict in videoDicts:
        #id: richItemRenderer>>content>>videoRenderer>>videoId
        webpage_url = 'https://www.youtube.com/watch?v=' + videoDict['richItemRenderer']['content']['videoRenderer']['videoId']
        #title: richItemRenderer>>content>>videoRenderer>>title>>runs[0]>>text
        title = videoDict['richItemRenderer']['content']['videoRenderer']['title']['runs'][0]['text']
        #upload_dated: richItemRenderer>>content>>videoRenderer>>publishedTimeText>>simpleText
        upload_dated = videoDict['richItemRenderer']['content']['videoRenderer']['publishedTimeText']['simpleText']

        videoInfo = {"webpage_url": webpage_url, "title": title, "upload_dated": upload_dated, "mtime": datetime.now().strftime("%Y-%m-%d %H-%M-%S")}
        file.write(videoInfo)


def startCode(channel):
    url = channel['URL']
    channelName = channel['name']
    print(url)

    headers = {
        "host": "www.youtube.com",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "x-browser-channel": "stable",
        "x-browser-year": "2024",
        "x-browser-validation": "QFEz3B6Z4AT6PlLzuts1mBxQGCM=",
        "x-browser-copyright": "Copyright 2024 Google LLC. All rights reserved.",
        "x-client-data": "CMGNywE=",
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-full-version": "131.0.6778.205",
        "sec-ch-ua-arch": "x86",
        "sec-ch-ua-platform": "Windows",
        "sec-ch-ua-platform-version": "10.0.0",
        "sec-ch-ua-model": "",
        "sec-ch-ua-bitness": "64",
        "sec-ch-ua-wow64": "?0",
        "sec-ch-ua-full-version-list": '"Google Chrome";v="131.0.6778.205", "Chromium";v="131.0.6778.205", "Not_A Brand";v="24.0.0.0"',
        "sec-ch-ua-form-factors": "Desktop",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "priority": "u=0, i",
        "cookie": "GPS=1; YSC=YAtL0dvqv60; VISITOR_INFO1_LIVE=Od_bRcKzFjc; VISITOR_PRIVACY_METADATA=CgJLUhIEGgAgUA%3D%3D; __Secure-ROLLOUT_TOKEN=CMXAsKCbwKi1xAEQvLbzjZvwigMYvLbzjZvwigM%3D"
    }

    with httpx.Client(http2=True) as client:
        response = client.get(url, headers=headers)
        
        data = response.text
        startIdx = data.find('ytInitialData')+len('ytInitialData = ')
        data = data[startIdx:]
        lastIdx = data.find(';')
        data = data[:lastIdx]
        
        dataDict = json.loads(data)
        
        #videoDicts: contents>> twoColumnBrowseResultsRenderer>>tabs[1]>>tabRenderer>>content>>richGridRenderer>>contents   <-- 이거 리스트임
        videoDicts = dataDict['contents']['twoColumnBrowseResultsRenderer']['tabs'][1]['tabRenderer']['content']['richGridRenderer']['contents'][:-1]

        #continuation: contents>> twoColumnBrowseResultsRenderer>>tabs[1]>>tabRenderer>>content>>richGridRenderer>>contents[-1]>>continuationItemRenderer>>continuationEndpoint>>continuationCommand>>token
        continuation = dataDict['contents']['twoColumnBrowseResultsRenderer']['tabs'][1]['tabRenderer']['content']['richGridRenderer']['contents'][-1]['continuationItemRenderer']['continuationEndpoint']['continuationCommand']['token']

        startParser(videoDicts, channelName)
    return continuation



def repeatParser(videoDicts, channelName):
    file = jsonlines.open('./videoList/'+channelName+'.jsonl', 'a')
    for videoDict in videoDicts:
        #id: richItemRenderer>>content>>videoRenderer>>videoId
        webpage_url = 'https://www.youtube.com/watch?v=' + videoDict['richItemRenderer']['content']['videoRenderer']['videoId']
        #title: richItemRenderer>>content>>videoRenderer>>title>>runs[0]>>text
        title = videoDict['richItemRenderer']['content']['videoRenderer']['title']['runs'][0]['text']
        #upload_dated: richItemRenderer>>content>>videoRenderer>>publishedTimeText>>simpleText
        upload_dated = videoDict['richItemRenderer']['content']['videoRenderer']['publishedTimeText']['simpleText']

        videoInfo = {"webpage_url": webpage_url, "title": title, "upload_dated": upload_dated, "mtime": datetime.now().strftime("%Y-%m-%d %H-%M-%S")}
        file.write(videoInfo)
        
        if upload_dated == '7개월 전':
            global stopFlag
            stopFlag = True


def repeatCode(channel, continuation):
    url = "https://www.youtube.com/youtubei/v1/browse?prettyPrint=false"
    referer = channel['URL']
    channelName = channel['name']

    headers = {
        "host": "www.youtube.com",
        "content-length": "5290",
        "sec-ch-ua-full-version-list": '"Google Chrome";v="131.0.6778.205", "Chromium";v="131.0.6778.205", "Not_A Brand";v="24.0.0.0"',
        "sec-ch-ua-platform": "Windows",
        "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-bitness": "64",
        "sec-ch-ua-model": "",
        "sec-ch-ua-mobile": "?0",
        "x-youtube-client-name": "1",
        "sec-ch-ua-wow64": "?0",
        "sec-ch-ua-form-factors": "Desktop",
        "x-youtube-client-version": "2.20250108.06.00",
        "sec-ch-ua-arch": "x86",
        "sec-ch-ua-full-version": "131.0.6778.205",
        "content-type": "application/json",
        "x-youtube-bootstrap-logged-in": "false",
        "x-goog-visitor-id": "Cgt0Si1oUGplcHM4QSjhqJK8BjIKCgJLUhIEGgAgFg%3D%3D",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "sec-ch-ua-platform-version": "10.0.0",
        "accept": "*/*",
        "origin": "https://www.youtube.com",
        "x-client-data": "CMTbygE=",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "same-origin",
        "sec-fetch-dest": "empty",
        "referer": referer, #"https://www.youtube.com/sbs8news/videos",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "priority": "u=1, i",
        "cookie": "YSC=1r2wbIwwczI; VISITOR_INFO1_LIVE=tJ-hPjeps8A; VISITOR_PRIVACY_METADATA=CgJLUhIEGgAgFg%3D%3D; __Secure-ROLLOUT_TOKEN=CMXAsKCbwKi1xAEQvLbzjZvwigMYvLbzjZvwigM%3D; PREF=tz=Asia.Seoul; GPS=1"
    }

    payload = {
        "context": {
            "client": {
                "hl": "ko",
                "gl": "KR",
                "remoteHost": "143.248.41.93",
                "deviceMake": "",
                "deviceModel": "",
                "visitorData": "Cgt0Si1oUGplcHM4QSjhqJK8BjIKCgJLUhIEGgAgFg%3D%3D",
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36,gzip(gfe)",
                "clientName": "WEB",
                "clientVersion": "2.20250108.06.00",
                "osName": "Windows",
                "osVersion": "10.0",
                "originalUrl": referer, #"https://www.youtube.com/sbs8news/videos",
                "platform": "DESKTOP",
                "clientFormFactor": "UNKNOWN_FORM_FACTOR",
                "configInfo": {
                    "appInstallData": "COGokrwGEP28zhwQ4M2xBRCHrM4cEK_CzhwQ-KuxBRDJ5rAFEM3RsQUQ4eywBRCZ0v8SELfq_hIQvoqwBRCmk7EFEKLUsQUQjdSxBRCrns4cEI7XsQUQxr-xBRDmz7EFEOLUrgUQ6sOvBRDAt84cENfBsQUQwcLOHBCU_rAFEOeazhwQgdaxBRCM0LEFELekzhwQxtixBRCBw7EFEJK4zhwQ56jOHBDT4a8FEMzfrgUQppqwBRCmwM4cEMrUsQUQytixBRD6uM4cEN-0zhwQ3q2xBRCDw7EFEMHa_xIQwc2xBRDRlM4cEN68zhwQ6-j-EhCIh7AFENqUzhwQ9quwBRDKws4cEJS7zhwQksuxBRDYts4cEPyyzhwQh8OxBRCPw7EFEKKjzhwQvbauBRCO0LEFEMK3zhwQrsHOHBComrAFEMTYsQUQnaawBRCL1LEFEInorgUQhaexBRC3768FENO5zhwQg73OHBDlubEFEJmYsQUQmY2xBRC9mbAFENCNsAUQ7bmxBRCI468FEJrOsQUQ2arOHBDJ968FEIqhsQUQwavOHBDL0bEFEMjYsQUQndCwBRDbr68FEI3MsAUQsZ3_EhCfrM4cKixDQU1TR3hVUW9MMndETkhrQnZQdDhRdVA5QTZvRE9GeTFueWpfd1FkQnc9PQ%3D%3D",
                    "coldConfigData": "CMGokrwGGjJBT2pGb3gxeUU0ZG5jLThuLTY3bk1JWUFNem44R2Q1akhCRzdJdWxNWlBTV3N5RWxaQSIyQU9qRm94MXlFNGRuYy04bi02N25NSVlBTXpuOEdkNWpIQkc3SXVsTVpQU1dzeUVsWkE%3D",
                    "coldHashData": "COGokrwGEhQxNTMwNDM1ODcwNTA4OTI3NDQwMhiIkI-8BjIyQU9qRm94MXlFNGRuYy04bi02N25NSVlBTXpuOEdkNWpIQkc3SXVsTVpQU1dzeUVsWkE6MkFPakZveDF5RTRkbmMtOG4tNjduTUlZQU16bjhHZDVqSEJHN0l1bE1aUFNXc3lFbFpBQmhDQU1TU0EwWnVOMjNBdDRVemczdktkQVJwZ2FYQmIwVl9RTzZ4NXNROGhXM0E3WUlGU0dtM3JVZm1yc0dfMW5WeGdUcndnWUU1UVRMQU9GeThTM2pFYWdWMzF1OHFnYldQdldvQmc9PQ%3D%3D",
                    "hotHashData": "COGokrwGEhQxNDIyMTMxOTE1MzU1ODAyNDQ0MhiIkI-8BiiU5PwSKKXQ_RIonpH-EijIyv4SKLfq_hIowYP_Eiixnf8SKM6o_xIopcf_Eiibzv8SKMTR_xIomdL_EijW0v8SKPLZ_xIoqdz_Eija4_8SKLDk_xIoheX_Eiik6P8SKKzp_xIo7un_Eiim6v8SMjJBT2pGb3gxeUU0ZG5jLThuLTY3bk1JWUFNem44R2Q1akhCRzdJdWxNWlBTV3N5RWxaQToyQU9qRm94MXlFNGRuYy04bi02N25NSVlBTXpuOEdkNWpIQkc3SXVsTVpQU1dzeUVsWkFCKENBTVNHQTBPb3RmNkZhN0JCcVZFRlF6ZHo4SU14cWZ0Qy1TVUNnPT0%3D"
                },
                "userInterfaceTheme": "USER_INTERFACE_THEME_LIGHT",
                "timeZone": "Asia/Seoul",
                "browserName": "Chrome",
                "browserVersion": "131.0.0.0",
                "acceptHeader": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "deviceExperimentId": "ChxOelExT1RJMU1EQXlOemMwTXprME1qYzRPUT09EOGokrwGGOGokrwG",
                "rolloutToken": "CMXAsKCbwKi1xAEQvLbzjZvwigMYvLbzjZvwigM%3D",
                "screenWidthPoints": 929,
                "screenHeightPoints": 1045,
                "screenPixelDensity": 1,
                "screenDensityFloat": 1,
                "utcOffsetMinutes": 540,
                "connectionType": "CONN_CELLULAR_3G",
                "memoryTotalKbytes": "8000000",
                "mainAppWebInfo": {
                    "graftUrl": referer, #"https://www.youtube.com/sbs8news/videos",
                    "pwaInstallabilityStatus": "PWA_INSTALLABILITY_STATUS_CAN_BE_INSTALLED",
                    "webDisplayMode": "WEB_DISPLAY_MODE_BROWSER",
                    "isWebNativeShareAvailable": True
                }
            },
            "user": {
                "lockedSafetyMode": False
            },
            "request": {
                "useSsl": True,
                "internalExperimentFlags": [],
                "consistencyTokenJars": []
            },
            "clickTracking": {
                "clickTrackingParams": "CCgQ8eIEIhMIu4nciOzxigMVtkr1BR0E5SvQ"
            },
            "adSignalsInfo": {
                "params": [
                    {"key": "dt", "value": "1736741985860"},
                    {"key": "flash", "value": "0"},
                    {"key": "frm", "value": "0"},
                    {"key": "u_tz", "value": "540"},
                    {"key": "u_his", "value": "3"},
                    {"key": "u_h", "value": "1200"},
                    {"key": "u_w", "value": "1920"},
                    {"key": "u_ah", "value": "1160"},
                    {"key": "u_aw", "value": "1920"},
                    {"key": "u_cd", "value": "24"},
                    {"key": "bc", "value": "31"},
                    {"key": "bih", "value": "1045"},
                    {"key": "biw", "value": "912"},
                    {"key": "brdim", "value": "522,98,522,98,1920,0,945,1140,929,1045"},
                    {"key": "vis", "value": "1"}, 
                    {"key": "wgl", "value": "true"},
                    {"key": "ca_type", "value": "image"}
                ],
                "bid": "ANyPxKr0wxwg8zoZnlpdsiMLa_Tt-E97Mfx4VypJjTfUvyDxp5gk_T7TsS8WOvWaO1Osm5AN6fzEINaD2HyOvpiWM4Pyh5spFg"
            }
        },
        "continuation": continuation
    }

    payload_json = json.dumps(payload, separators=(',', ':'))
    headers["content-length"] = str(len(payload_json))

    try:    
        with httpx.Client(http2=True) as client:
            response = client.post(url, headers=headers, data=payload_json)
            
            dataDict = json.loads(response.text)
            
            #videoDicts: onResponseReceivedActions[0]>>appendContinuationItemsAction>>continuationItems   <-- 이거 리스트임
            videoDicts = dataDict['onResponseReceivedActions'][0]['appendContinuationItemsAction']['continuationItems'][:-1]

            #continuation: onResponseReceivedActions[0]>>appendContinuationItemsAction>>continuationItems[-1]>>continuationItemRenderer>>continuationEndpoint>>continuationCommand>>token
            continuation = dataDict['onResponseReceivedActions'][0]['appendContinuationItemsAction']['continuationItems'][-1]['continuationItemRenderer']['continuationEndpoint']['continuationCommand']['token']

            repeatParser(videoDicts, channelName)
        return continuation
    except Exception as e:
        print(response.text)
        print(e)


for channel in channels:
    stopFlag = False
    continuation = startCode(channel)
    while stopFlag == False:
        continuation = repeatCode(channel, continuation)
        time.sleep(1)