from config import *

import pymysql
import pandas as pd

from sshtunnel import SSHTunnelForwarder
from datetime import datetime


tunnel = SSHTunnelForwarder(
    (DB_ENV['SSH_HOST'], DB_ENV['SSH_PORT']),
    ssh_username=DB_ENV['SSH_USER'],
    ssh_password=DB_ENV['SSH_PASSWORD'],
    remote_bind_address=(DB_ENV['HOST'], DB_ENV['PORT'])
); tunnel.start()

mysql = pymysql.connect(
    host='127.0.0.1', # tunnel.local_bind_host,
    port=tunnel.local_bind_port,
    user=DB_ENV['USER'],
    password=DB_ENV['PASSWORD'],
    database=DB_ENV['DATABASE'],
    charset='utf8'
)

channel_name_lst = [
    # KOR
    '@MBCNEWS11',
    '@sbsnews8',
    '@newskbs',
    '@jtbc_news',
    '@ytnnews24',
    '@channelA-news',
    '@tvchosunnews',
    
    # US
    '@msnbc',
    '@ABCNews',
    '@AssociatedPress',
    '@CBSNews',
    '@CNN',
    '@guardiannews',
    '@NBCNews',
    '@BBCNews',
    '@NewsNation',
    '@Reuters',
    '@wsj',
    '@nypost',
    '@washingtontimes',
    '@FoxNews',
    '@breitbartnews92',
    '@BlazeTV',
    '@CBNnewsonline',
    '@NewsmaxTV',
    '@oann'
]


def check_and_create_channel_table(cur, conn):
    table_name = 'CHANNEL_TABLE'
    check_table = cur.execute(f"SHOW TABLE STATUS LIKE '{table_name}'")
    if not check_table:
        create_table_query = f'''
            CREATE TABLE {table_name} (
                ID            BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
                CHANNEL_NAME  VARCHAR(30) NULL,
                CHANNEL_URL   VARCHAR(70) NULL,
                TIME_STAMP    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
        '''; cur.execute(create_table_query); conn.commit()
        
        ## If you want to add youtube channel, then add it here
        for CHANNEL_NAME in channel_name_lst:
            CHANNEL_URL = f'https://www.youtube.com/{CHANNEL_NAME}/videos'
            insert_query = f'''
                INSERT INTO CHANNEL_TABLE (CHANNEL_NAME, CHANNEL_URL)
                VALUES {CHANNEL_NAME, CHANNEL_URL}
            '''; cur.execute(insert_query)
        conn.commit()
        
    print(pd.read_sql(f'SELECT * FROM {table_name};', conn))

def check_and_create_channel_follower_cnt_table(cur, conn):
    table_name = 'CHANNEL_FOLLOWER_CNT_TABLE'
    check_table = cur.execute(f"SHOW TABLE STATUS LIKE '{table_name}'")
    if not check_table:
        create_table_query = f'''
            CREATE TABLE {table_name} (
                ID                  BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
                CHANNEL_TABLE_ID    BIGINT,
                FOLLOWER_COUNT      INT(20),
                TIME_STAMP          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (CHANNEL_TABLE_ID) REFERENCES CHANNEL_TABLE (ID)
            ) CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
        '''; cur.execute(create_table_query); conn.commit()

def check_and_create_video_url_table(cur, conn):
    table_name = 'VIDEO_URL_TABLE'
    check_table = cur.execute(f"SHOW TABLE STATUS LIKE '{table_name}'")
    if not check_table:
        create_table_query = f'''
            CREATE TABLE {table_name} (
                ID                  BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
                CHANNEL_TABLE_ID    BIGINT,
                YOUTUBE_URL         VARCHAR(70),
                TIME_STAMP          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (CHANNEL_TABLE_ID) REFERENCES CHANNEL_TABLE (ID)
            ) CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
        '''; cur.execute(create_table_query); conn.commit()

def check_and_create_content_table(cur, conn):
    table_name = 'CONTENT_TABLE'
    check_table = cur.execute(f"SHOW TABLE STATUS LIKE '{table_name}'")
    if not check_table:
        create_table_query = f'''
            CREATE TABLE {table_name} (
                ID                    BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
                C_ID                  VARCHAR(20),
                C_TITLE               VARCHAR(200),
                C_DESCRIPTION         TEXT,
                C_THUMBNAIL_URL       VARCHAR(100),
                C_DURATION            VARCHAR(10),
                C_DURATION_STRING     VARCHAR(10),
                C_CATEGORIES          TEXT,
                C_TAGS                TEXT,
                C_UPLOAD_DATE         VARCHAR(20),
                TIME_STAMP            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
        '''; cur.execute(create_table_query); conn.commit()
        
def check_and_create_content_revised_table(cur, conn):
    table_name = 'CONTENT_REVISED_TABLE'
    check_table = cur.execute(f"SHOW TABLE STATUS LIKE '{table_name}'")
    if not check_table:
        create_table_query = f'''
            CREATE TABLE {table_name} (
                ID                    BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
                C_ID                  VARCHAR(20),
                C_TITLE               VARCHAR(200),
                C_DESCRIPTION         TEXT,
                C_THUMBNAIL_URL       VARCHAR(100),
                C_DURATION            VARCHAR(10),
                C_DURATION_STRING     VARCHAR(10),
                C_CATEGORIES          TEXT,
                C_TAGS                TEXT,
                C_UPLOAD_DATE         VARCHAR(20),
                TIME_STAMP            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
        '''; cur.execute(create_table_query); conn.commit()
        
def check_and_create_content_detail_table(cur, conn):
    table_name = 'CONTENT_DETAIL_TABLE'
    check_table = cur.execute(f"SHOW TABLE STATUS LIKE '{table_name}'")
    if not check_table:
        create_table_query = f'''
            CREATE TABLE {table_name} (
                ID                      BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
                CONTENT_TABLE_ID        BIGINT,
                C_VIEW_COUNT            VARCHAR(20),
                C_COMMENT_COUNT         VARCHAR(20),
                C_LIKE_COUNT            VARCHAR(20),
                TIME_STAMP              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (CONTENT_TABLE_ID) REFERENCES CONTENT_TABLE (ID)
            ) CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
        '''; cur.execute(create_table_query); conn.commit()
        
def check_and_create_content_thumbnail_table(cur, conn):
    table_name = 'CONTENT_THUMBNAIL_TABLE'
    check_table = cur.execute(f"SHOW TABLE STATUS LIKE '{table_name}'")
    if not check_table:
        create_table_query = f'''
            CREATE TABLE {table_name} (
                ID                  BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
                CONTENT_TABLE_ID    BIGINT,
                C_THUMBNAIL_IMAGE   BLOB,
                TIME_STAMP          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (CONTENT_TABLE_ID) REFERENCES CONTENT_TABLE (ID)
            ) CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
        '''; cur.execute(create_table_query); conn.commit()
        
def check_and_create_comment_table(cur, conn):
    table_name = 'COMMENT_TABLE'
    check_table = cur.execute(f"SHOW TABLE STATUS LIKE '{table_name}'")
    if not check_table:
        create_table_query = f'''
            CREATE TABLE {table_name} (
                ID                  BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
                CONTENT_TABLE_ID    BIGINT,
                COMMENT_ID          VARCHAR(100),
                COMMENT_PARENT_ID   VARCHAR(100),
                USER_ID             VARCHAR(100),
                USER_NAME           VARCHAR(100),
                COMMENT             TEXT,
                LIKE_COUNT          VARCHAR(20),
                TIME_TEXT           VARCHAR(100),
                UNIX_TIMESTAMP      VARCHAR(30),
                TIME_STAMP          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (CONTENT_TABLE_ID) REFERENCES CONTENT_TABLE (ID)
            ) CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
        '''; cur.execute(create_table_query); conn.commit()  

# def check_and_create_comment_revised_table(cur, conn):
#     table_name = 'COMMENT_REVISED_TABLE'
#     check_table = cur.execute(f"SHOW TABLE STATUS LIKE '{table_name}'")
#     if not check_table:
#         create_table_query = f'''
#             CREATE TABLE {table_name} (
#                 ID                  BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
#                 CONTENT_TABLE_ID    BIGINT,
#                 REVISED_COMMENT     TEXT,
#                 TIME_STAMP          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                 FOREIGN KEY (CONTENT_TABLE_ID) REFERENCES CONTENT_TABLE (ID)
#             ) CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
#         '''; cur.execute(create_table_query); conn.commit()              

# def check_and_create_comment_like_count_table(cur, conn):
#     table_name = 'COMMENT_LIKE_COUNT_TABLE'
#     check_table = cur.execute(f"SHOW TABLE STATUS LIKE '{table_name}'")
#     if not check_table:
#         create_table_query = f'''
#             CREATE TABLE {table_name} (
#                 ID                  BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
#                 CONTENT_TABLE_ID    BIGINT,
#                 REVISED_LIKE_COUNT  VARCHAR(20),
#                 TIME_STAMP          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                 FOREIGN KEY (CONTENT_TABLE_ID) REFERENCES CONTENT_TABLE (ID)
#             ) CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
#         '''; cur.execute(create_table_query); conn.commit()              


if __name__ == "__main__":
    with tunnel:
        with mysql as conn:
            with conn.cursor() as cur:
                # MySQL: CREATE DATABASE YOUTUBE_2024 character set utf8mb4 collate utf8mb4_general_ci;
                
                check_and_create_channel_table(cur, conn)
                check_and_create_channel_follower_cnt_table(cur, conn)
                check_and_create_video_url_table(cur, conn)
                check_and_create_content_table(cur, conn)
                check_and_create_content_revised_table(cur, conn)
                check_and_create_content_detail_table(cur, conn)
                check_and_create_content_thumbnail_table(cur, conn)
                check_and_create_comment_table(cur, conn)
                # check_and_create_comment_revised_table(cur, conn)
                # check_and_create_comment_like_count_table(cur, conn)
                
                print(cur.execute("SHOW TABLES;"))
                
    tunnel.stop()
