#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import requests
import math
from bs4 import BeautifulSoup
import pymysql
import time
import random
import traceback
import re
import json
import jieba
from wordcloud import WordCloud,STOPWORDS,ImageColorGenerator
import matplotlib.pyplot as plt



print ("start running mode")

#用来过滤表情符号，因为表情符号的四个字节的字符无法存入我本地低于5.3、不支持utf8mb4的mysql数据库
emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)

#用于生成分词 直接存放短评的字符创列表
string_list = []

#insert进数据库的语句
sql = "insert into t_content(content, username) values(%s, %s)"

# 打开数据库连接
db = pymysql.connect( host = 'localhost', 
                      port = 3306, 
                      user = 'root',
                      password = 'admin',
                      db = 'the_wandering_earth', 
                      charset='utf8')

#每页返回的最大页容量
page_size = 50

#请求url格式字符串
request_url_pattern = "https://m.douban.com/rexxar/api/v2/movie/26266893/interests?count=%d&order_by=hot&start=%d"

#请求头里referer_url的格式字符串
referer_url_pattern = "https://m.douban.com/movie/subject/26266893/comments?sort=new_score&start=%d"
        
headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'}

start_index = 0

while start_index <= 500 :
    
    if start_index == 500 :
        start_index = 499
        for i in range (0, 50) :
            del_index = len(string_list) - 1
            del string_list[del_index]
        
    request_url = request_url_pattern % (page_size, start_index)
    
    if start_index == 0 :
        referer_url = "https://m.douban.com/movie/subject/26266893/"
    else :
        referer_url = referer_url_pattern % (start_index - 50)
    
    try:
        
        print (request_url)
        
        session = requests.Session()
        
        print (referer_url)
        
        headers['referer'] = referer_url
        
        r = session.get(request_url, headers=headers, allow_redirects=False)
        
        print ("start_index:%d status_code:%d" % (start_index, r.status_code))
        if r.status_code != 200 :   
            break
        
        response_json = json.loads(r.text)
        interests = response_json['interests']
        print(len(interests))
        for interest in interests :
            comment = interest['comment']
            comment = emoji_pattern.sub(r'', comment)
            user = interest['user']
            name = user['name']
            name = emoji_pattern.sub(r'', name)
            cursor = db.cursor()
            if name == "𝔸𝕫𝕖𝕣𝕚𝕝" :
                name = "Azeril"
            #print (name)
            cursor.execute(sql, ( comment, name ) )
            db.commit()
            cursor.close()
            string_list.insert(0, comment)
        #break       
    except requests.exceptions.ProxyError as e:
        print('Error', e.args)
        print (ip_port + " not work, removed")
        break
    
    sleep_second = random.randint(5, 15)
    time.sleep(sleep_second)
    
    start_index = start_index + page_size
    
db.close()

all_string = ''.join(string_list)

cut_text = " ".join(jieba.cut(all_string))
wordcloud = WordCloud(font_path="C:/Windows/Fonts/STFANGSO.TTF",
background_color="white", width=1680, height=1050).generate(cut_text)

plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.savefig('H:/2019/2/20/result.jpg')
plt.show()

