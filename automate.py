from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from mail import send_join_request_email
import random
from dotenv import load_dotenv
from pathlib import Path
from selenium.webdriver.common.by import By
from utils import get_env_value
import re
from datetime import datetime, timedelta

pattern = r'[0-9]+m|3h'
ENV_PATH = Path(__file__).resolve().parent/ ".env"
load_dotenv(dotenv_path=ENV_PATH)

driver_path = get_env_value("DRIVER_PATH")
fb_url = get_env_value("FB_URL")

# Set up selenium webdriver
def driver_connection():
   chrome_options = Options()
   chrome_service = Service(driver_path)
   chrome_options.add_argument("--disable-notifications")
   chrome_options.add_argument("--disable-popup-blocking")
   chrome_options.add_argument("--disable-geolocation")
   chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36")
   chrome_options.add_argument('--disable-blink-features=AutomationControlled')
   chrome_options.add_argument('--disable-gpu')
   chrome_options.add_argument('--disable-dev-shm-usage')
   chrome_options.add_argument('--no-sandbox')
   chrome_options.add_argument('--disable-extensions')
   chrome_options.add_argument('--disable-infobars')
   chrome_options.add_argument('--remote-debugging-port=9222')
   chrome_options.add_argument('--disable-notifications')
   chrome_options.add_argument('--ignore-certificate-errors')
  #  chrome_options.add_argument("--headless")
   driver = webdriver.Chrome(service=chrome_service,options=chrome_options)
   return driver

def fb_login(email,password):
  driver = driver_connection()
  wait = WebDriverWait(driver, 10)
  driver.get(fb_url)
  driver.find_element(By.ID,'email').send_keys(email)
  driver.find_element(By.ID,'pass').send_keys(password)
  sleep(random.randint(1,3))
  driver.find_element(By.XPATH,"//button[@name='login']").click()
  return driver,wait

def fb_join_request(group_url):
  driver,wait = fb_login()
  # Wait for login to complete and extract cookies
  sleep(random.randint(3,5)) # adjust this delay as necessary
  driver.get(group_url)
  sleep(random.randint(5,6))
  wait.until(EC.presence_of_element_located((By.XPATH,"//div[@aria-label='Join group']")))
  driver.find_element(By.XPATH,"//div[@aria-label='Join group']").click()
  try:
    wait.until(EC.presence_of_element_located((By.XPATH,"//span[contains(text(),'Answer questions')]")))
    text = driver.find_element(By.XPATH,"//span[contains(text(),'Answer questions')]").text.strip()
    send_join_request_email(group_url)
    message = {'message': 'Join Request has been sent successfully!'}
  except:
    message = {'message': 'You are now a member in that group!'}
  driver.quit()
  return message

def get_user_data(html, driver):
  soup = BeautifulSoup(html,'html.parser')
  user_data = soup.find("a")['href'].split("?")[0]
  print("User_data", user_data)
  user_id = user_data.rstrip("/").split("/")[-1]
  print("USER ID  ", user_id)
  user_url = fb_url + user_id + '/about'
  print("User URL  ", user_url)
  driver.get(user_url)
  try: lives_in = driver.find_element(By.XPATH,"//span[contains(text(), 'Lives')]/a").text
  except: lives_in = None
  sleep(random.randint(2,4))
  soup = BeautifulSoup(driver.page_source,'html.parser')
  username = soup.find('h1').text
  return username,user_id,lives_in

def create_post_timestamp(html):
    past_date = None
    time_str = ""
    try:
      soup = BeautifulSoup(html,'html.parser')
      spans_without_style = soup.find_all('span', attrs={'style': None})
      # Print the text of the selected spans
      for span in spans_without_style:
          if len(span.text) < 5:
              time_str += span.text
      if 'h' in time_str.lower() or "hr" in time_str.lower() or "hrs" in time_str.lower():
          hours_to_subract = re.sub("\D", '', time_str)
          past_date = datetime.today() - timedelta(hours=int(hours_to_subract))
          return past_date.isoformat()

      if 'm' in time_str.lower() or "min" in time_str.lower() or "mins" in time_str.lower():
          minutes_to_subtract = re.sub("\D", '', time_str)
          past_date = datetime.now() - timedelta(minutes=int(minutes_to_subtract))
          return past_date.isoformat()

      if 's' in time_str.lower():
          seconds_to_subtract = re.sub("\D", '', time_str)
          past_date = datetime.now() - timedelta(seconds=int(seconds_to_subtract))
          return past_date.isoformat()

      elif 'd' in time_str.lower() or "ds" in time_str.lower():
          days_to_subtract = re.sub("\D", '', time_str)
          past_date = datetime.today() - timedelta(days=int(days_to_subtract))
          return past_date.isoformat()
    except:
       pass
    # print(f"time is : {t}")
    return past_date

def prepare_comments(comments,post_text):
    comments_list = []
    if comments is not None and len(comments) >0:
      for comment in comments:
          if comment.replace("\n",'').lower() != post_text.lower():
              comments_list.append(comment)
      cmts = list(set(comments_list))
      comments_list.clear()
      for cmt in cmts:
          cmt_name,cmt_txt = cmt.split("\n", 1)
          # print(split_result)
          temp_dct = {"commenter_name":cmt_name,"commenter_text":cmt_txt}
          comments_list.append(temp_dct)
    return comments_list

def get_post_data(html):
  soup = BeautifulSoup(html,'html.parser')
  group_name = soup.find("h1").text
  # messages = soup.find_all('div', {'data-ad-comet-preview': 'message'})
  # # except: messages = soup.find('div', {'dir': 'auto'}).text
  # if len(messages) != 0:
  #   post_text = messages[0].text
  # else:
  #   post_text = ''
  return group_name

def extract_comments(html_content):
    comments = []
    soup = BeautifulSoup(html_content, 'html.parser')
    pattern = re.compile(r'\d+')
    for div in soup.find_all('span'):
        if div.find_all(text=True, recursive=False) and not div.find_all(True):
            div_text = div.get_text()
            pattern = re.compile(r'\d+')
            if not re.search(pattern, div_text):
                comments.append(div.text)
    for div in soup.find_all('div'):
        if div.find_all(text=True, recursive=False) and not div.find_all(
        True)and 'Reply' not in div.get_text() and 'Share' not in div.get_text() and 'Like' not in div.get_text():
            comments.append(div.text)
    return comments

def get_post_comments(driver,post_text):
  comments_lst = []
  try:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(random.randint(2,4))
    try:
      post_comments = driver.find_element(By.XPATH,"//span[contains(text(), 'more comments')]")
      post_comments.click()
    except:
      pass
    sleep(random.randint(2,4))
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(random.randint(2,3))
    try:
       post_comments = driver.find_elements(By.XPATH,"//div[@role='article']")
       for comment in post_comments:
         try:
          cmt_name,cmt_txt = extract_comments(comment.get_attribute("innerHTML"))
          temp_dct = {"commenter_name":cmt_name,"commenter_text":cmt_txt}
          print(temp_dct)
          comments_lst.append(temp_dct)
         except Exception as exp:
            pass
       comments = comments_lst
    except:
      comments = driver.find_elements(By.CSS_SELECTOR,"div[dir='auto'][style='text-align: start;']")
      for comment in comments:
        comment = comment.find_element(By.XPATH, "../../../..").text.strip()
        comments_lst.append(comment)
      comments = prepare_comments(comments_lst,post_text)
  except:
    comments = None
  return comments

def get_post_text(html):
  text = ''
  try:
    soup = BeautifulSoup(html, 'html.parser')
    fb_feed_text = soup.get_text()
    try:
      post_text = fb_feed_text.replace("Facebook",'').strip('\n')
      text += re.split(r'(?i)(?:group\)|group)', post_text)[1]
      if "All reactions" in text:
          text = text.rsplit("All reactions",1)[0]
      else:
          text = text.rsplit("Like",1)[0]
      if ' ' not in text[-60:]:
        text = text[:-60]
    except Exception as exp:
      print("Regex error", exp)
  except Exception as exp:
     print("Error at getting post text function::", exp)
  return text
  
def get_group_posts(url, keywords, email, password):
  post_data = {}
  driver,wait = fb_login(email,password)
  sleep(random.randint(2,3)) # adjust this delay as necessary
  driver.get(url) 
  sleep(random.randint(3,5))
  try:
    driver.find_element(By.XPATH,"//span[contains(text(), 'Most Relevant')]").click()
    sleep(random.randint(2,3))
    driver.find_element(By.XPATH,"//span[contains(text(), 'New posts')]").click()
    sleep(random.randint(2,4))
  except:
    pass
  feed = driver.find_element(By.XPATH,"//div[@role='feed']/div[2]")
  try:
    see_more = driver.find_element(By.XPATH,"//div[contains(text(), 'See more')]")
    see_more.click()
  except:
     pass
  fb_feed = feed.get_attribute("innerHTML")
  post_text = get_post_text(fb_feed)
  # print(fb_feed_text)
  try:
    recent_post = feed.find_element(By.XPATH, "//span[@id]/span[2]/span/a")
  except:
    recent_post = feed.find_element(By.XPATH, "//span[@id]/span[4]/span/a")
  post_time_element = recent_post.find_element(By.TAG_NAME, "span")
  post_time = create_post_timestamp(post_time_element.get_attribute("innerHTML"))
  recent_post.click()
  sleep(random.randint(2,4))
  post_url = driver.current_url
  post_id = post_url.rstrip("/").split("/")[-1]
  group_name = get_post_data(driver.page_source)
  if any(name.lower() in post_text.lower() for name in keywords):
    comments = get_post_comments(driver,post_text)
    # comments = prepare_comments(post_comments, post_text)
    post_data['post_url'] = post_url
    post_data['post_id'] = post_id
    post_data['post_text'] = post_text
    post_data['group_name'] = group_name
    post_data['comments'] = comments
    post_data['post_time'] = post_time
    user_data = dict(zip(["username", "user_id", "lives_in"], get_user_data(fb_feed, driver)))
    post_data.update(user_data)
  driver.quit()
  print('post_data',post_data)
  return post_data
