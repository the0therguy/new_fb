from flask import Flask, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
from facebook_scraper import FacebookScraper
from datetime import datetime,timedelta
import os
from pathlib import Path
from utils import get_env_value, facebook_login ,get_comments

ENV_PATH = Path(__file__).resolve().parent/ ".env"
load_dotenv(dotenv_path=ENV_PATH)


# app = Flask(__name__)
username = get_env_value("DB_USERNAME")
password = get_env_value("DB_PASSWORD")
dbname = get_env_value("DATABASE_NAME")
collection_name = get_env_value("COLLECTION_NAME")
client = MongoClient(f"mongodb+srv://{username}:{password}@grouptracker.qmpwcd4.mongodb.net/{dbname}?retryWrites=true&w=majority")
fb = FacebookScraper()
# Access a database and collection
db = client[dbname]
collection = db[collection_name]

cookies = facebook_login(username,password)
print(cookies)
# @app.route('/', methods=['GET'])
def get_fb_post():
    group_id = '206676653699112'
    info = fb.get_group_info(group_id)
    print(info)
    # url = request.form.get('url')
    time_window = datetime.now() - timedelta(hours=1)
    scraped_posts = []
    for post in fb.get_posts(account=group_id, pages=1,cookies=cookies,options={"comments": 100}):
        post_time = post['time']
        if post_time >= time_window:
            print("comments_full",get_comments(post['comments_full']))
            print("user_id",post['user_id'])
            print("is_live",post['is_live'])
            print('username: ',post['username'])
            print('post_Text: ',post['text'])
            print('post_id: ',post['post_id'])
            print('post_url: ',post['post_url'])
            print("post time: ",post['time'])
            print("post comments: ",post['comments'])
            print('post_url: ',post['post_url'])
            group_name = post['with'][0]['name']
            print("group_name", group_name)
            print('post_url: ',f"https://www.facebook.com/{group_name}/posts/{post['post_id']}")
            print("post time: ",post['time'])
            print("post comments: ",post['comments'])
            profile = fb.get_profile(post['user_id'],cookies=cookies)
            print("User's profile info::: ",profile)
            print("===================================================================================")

# if __name__ == '__main__':
#     app.run()
#  https://www.facebook.com/206676653699112/posts/908593513507419
# get_fb_post()
