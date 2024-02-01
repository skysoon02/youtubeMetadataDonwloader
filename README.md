# Result Data Scheme

directory

```python
data/
 ├─comment/
 ├─detail/
 ├─followerCount/
 ├─metadata/
 ├─thumbnail/
 └─videoList/
```

## About Channel

/videoList/videoList_{channel_name}.jsonl

```json
{"webpage_url": "https://www.youtube.com/watch?v=av6a5pfIRFE", "title": "\"분명한 건 대원들은 최선 다해\"…'문경 화재' 소방관 2명 순직 브리핑 / SBS / 바로 이 뉴스", "upload_dated": "20240201", "mtime": "2024-02-01 17-59-31"}
{"webpage_url": "https://www.youtube.com/watch?v=P_cIxVAadOc", "title": "'이럴 경우' 차 바꾸면 개별소비세 70%↓…감면 효과 얼마나? / SBS / 친절한 경제", "upload_dated": "20240201", "mtime": "2024-02-01 17-59-31"}
{"webpage_url": "https://www.youtube.com/watch?v=4Ex7rEU3qaQ", "title": "우려 목소리 터져 나오자…'대학 압박' 한발 물러섰다 (자막뉴스) / SBS", "upload_dated": "20240201", "mtime": "2024-02-01 17-59-30"}
```

/followerCount/followerCount_{channel_name}.jsonl

```json
{"follower": 2720000.0, "mtime": "[2024-02-01 19:53:41]"}
{"follower": 2720000.0, "mtime": "[2024-02-01 20:13:23]"}
```

## About Video

/metadata/metadata_{video_id}.jsonl

```json
{"id": "3VtXGybKj84", "title": "불 난 건물 '인명 구조'하다가‥문경 화재 소방관 2명 순직 (2024.02.01/뉴스데스크/MBC)", "duration": 155, "duration_string": "2:35", "categories": ["News & Politics"], "tags": ["MBC", "MBC뉴스", "뉴스데스크", "newsdesk", "뉴스투데이", "newstoday", "8시뉴스", "아침뉴스", "뉴스", "정오뉴스", "news", "문경 공장 화재", "소방관", "소방관 순직"], "upload_date": "20240201", "description": "27살 김수광 소방교, 35살 박수훈 소방사.\n타인의 목숨을 구하기 위해 나섰던, 젊은 두 소방관이 순직했습니다.\n어제저녁 경북 문경의 공장 화재현장에서 \n인명 수색을 위해 가장 먼저 불길 속으로 뛰어들었던 두 사람입니다. \n먼저 화재 현장 연결하겠습니다. \n차현진 기자, 불탄 건물 앞에 있군요.\n현장 상황 전해주시죠.ㅤ\n\n\nhttps://imnews.imbc.com/replay/2024/nwdesk/article/6567855_36515.html\n\n#문경 공장화재 #소방관 #소방관순직\n\nⓒ MBC & iMBC 무단 전재, 재배포 및 이용(AI학습 포함)금지"}
```

/thumbnail

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/a2ba7b33-6caf-42b2-a4ba-08952b584ed6/1d209d9b-aea4-42d3-a26b-9ffe2f831596/Untitled.png)

```python
thumbnail/
├─{video_id1}_YY-MM-DD HH-MM-SS.jpg
├─{video_id1}_latest.jpg
├─{video_id2}_YY-MM-DD HH-MM-SS.jpg
├─{video_id2}_YY-MM-DD HH-MM-SS.jpg
├─{video_id2}_latest.jpg
├─{video_id3}_YY-MM-DD HH-MM-SS.jpg
└─{video_id3}_latest.jpg
```

/comment/{video_id}_YY-MM-DD HH-MM-SS.json

```json
[
  {
    "id": "UgwdZa2XvWrUhh5Y5gR4AaABAg",
    "text": "Contents of the comment",
    "like_count": 1,
    "author_id": "UCQ-KzGSntOtqHO2gx-e615g",
    "author": "@user-pm6ws5jk5f",
    "author_thumbnail": "https://yt3.ggpht.com/ytc/AIf8zZQVbr36cK0RckJPHBHxXQTcROew0hLESjSa7w=s176-c-k-c0x00ffffff-no-rj",
    "parent": "root",
    "_time_text": "11 days ago",
    "timestamp": 1705795200,
    "author_url": "https://www.youtube.com/channel/UCQ-KzGSntOtqHO2gx-e615g",
    "author_is_uploader": false,
    "is_favorited": false
  },
  {
    "id": "UgxzuNu5_t0Rs78Hle54AaABAg",
    "text": "Contents of the comment",
    "like_count": null,
    "author_id": "UCoMkNRBRRRwhGnEitd01gRA",
    "author": "@user-iu3fg5bu3l",
    "author_thumbnail": "https://yt3.ggpht.com/ytc/AIf8zZQJaSrd-dZjS8wzk9bod6WEIOhiV2kN5c-PXg=s176-c-k-c0x00ffffff-no-rj",
    "parent": "root",
    "_time_text": "11 days ago",
    "timestamp": 1705795200,
    "author_url": "https://www.youtube.com/channel/UCoMkNRBRRRwhGnEitd01gRA",
    "author_is_uploader": false,
    "is_favorited": false
  },
	...
]
```

# 실행 방법
