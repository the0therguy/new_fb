from flask import Flask, request, jsonify, Response
from pymongo import MongoClient
from dotenv import load_dotenv
from facebook_scraper import FacebookScraper
from datetime import timedelta
import datetime
import os
from pathlib import Path
import json
from utils import get_env_value, facebook_login, get_city
from automate import fb_join_request
ENV_PATH = Path(__file__).resolve().parent/ ".env"
load_dotenv(dotenv_path=ENV_PATH)

app = Flask(__name__)
db_username = get_env_value("DB_USERNAME")
db_password = get_env_value("DB_PASSWORD")
dbname = get_env_value("DATABASE_NAME")
collection_name = get_env_value("COLLECTION_NAME")
client = MongoClient(f"mongodb+srv://{db_username}:{db_password}@grouptracker.qmpwcd4.mongodb.net/{dbname}?retryWrites=true&w=majority")

fb = FacebookScraper()
fb_email = get_env_value("FB_EMAIL")
fb_password = get_env_value("FB_PASSWORD")
fb_url = get_env_value("FB_URL")

# Access a database and collection
db = client[dbname]
collection = db[collection_name]


@app.route('/posts', methods=['POST'])
def get_post():
    url = request.form.get('url')
    group = str(url.rstrip("/").split("/")[-1])
    group_info = fb.get_group_info(group)
    group_type = group_info['type']
    if group_type != 'தனிப்பட்டது குழு':
        group_id = group_info['id']
        group_name = group_info['name']
        print("Group_Id ",group_id,"Group_Name  ",group_name)
        time_window = datetime.datetime.now() - timedelta(hours=1)
        cookies = facebook_login(fb_email,fb_password)
        scraped_posts = []
        try:
            for post in fb.get_posts(account=group_id, pages=1,cookies=cookies,options={"comments": 100}):
                post_time = post['time']
                if post_time >= time_window:
                    post_info = {
                        "user_id": post['user_id'],
                        "username": post['username'],
                        "post_text": post['text'],
                        "post_id": post['post_id'],
                        "group_name": group_name,
                        "post_url": fb_url + f"groups/{group_id}/posts/{post['post_id']}",
                        "post_time": post['time'],
                        "user_city": get_city(fb.get_profile(post['user_id'],cookies=cookies)),
                        "post_comments": post['comments_full']
                    }
                    
                    scraped_posts.append(post_info)
                    print("===================================================================================")
                        # # Check for duplicates in the database
            print(scraped_posts)
            for post in scraped_posts:
                if collection.find_one({'post_id': post['post_id']}) is None:
                    # Post is not already in the database, insert it
                    collection.insert_one(post)
            return jsonify({'posts': scraped_posts})
        except:
        #     # Retrieve all posts from the database and return as JSON response
            all_posts = []
            for post in collection.find():
                all_posts.append({
                    "user_id": post['user_id'],
                    "username": post['username'],
                    "post_text": post['post_text'],
                    "post_id": post['post_id'],
                    "group_name": post['group_name'],
                    "post_url": post['post_url'],
                    "post_time": post['post_time'],
                    "post_comments": post['post_comments'],
                    "user_city": post['user_city']
                })
            
            return jsonify({'posts': all_posts})
        
@app.route('/join_request', methods=['POST'])
def join_request():
    url = request.form.get('url')
    message = fb_join_request(url)
    json_message = json.dumps(message)  # Serialize the message to JSON
    return Response(json_message, mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True,port=5000)
