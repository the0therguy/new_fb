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

def fb_login():
  driver = driver_connection()
  wait = WebDriverWait(driver, 10)
  driver.get(fb_url)
  driver.find_element(By.ID,'email').send_keys('8608600374')
  driver.find_element(By.ID,'pass').send_keys('krishanjel01')
  sleep(random.randint(0,3))
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
  except:
    pass
  driver.quit()
  message = {'message': 'Join Request has been sent successfully!'}
  return message


def private_groups(url):
  driver,wait = fb_login()
  sleep(random.randint(5,6)) # adjust this delay as necessary
  driver.get(url) 
  sleep(random.randint(3,5))
  driver.find_element(By.XPATH,"//span[contains(text(), 'Most Relevant')]").click()
  sleep(random.randint(2,3))
  driver.find_element(By.XPATH,"//span[contains(text(), 'New posts')]").click()
  sleep(random.randint(2,4))
  sleep(2)
  feed = driver.find_element(By.XPATH,"//div[@role='feed']").get_attribute("innerHTML")
  driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
  sleep(2)
  wait.until(EC.presence_of_element_located((By.XPATH,"//span[@id]/span[2]/span/a")))
  a_tags = driver.find_elements(By.XPATH,"//span[@id]/span[2]/span/a")
  for a in a_tags:
    print("Anchor  ",a.get_attribute("href"))
  soup = BeautifulSoup(feed,'html.parser')
  # print(soup)
  # a_tags = soup.select("a[role='link']")
  # print(a_tags)
  messages = soup.find_all('div', {'data-ad-comet-preview': 'message'})
  if len(messages) != 0:
    print(messages[0].get_text())

  # for span in soup.find_all('span', string=re.compile(pattern)):
  #     print(span)
  # for a in a_tags:
  #   if 'posts' in a['href']:
  #       print(a['href'])
  driver.close()
  driver.quit()

# private_groups("https://www.facebook.com/groups/206676653699112")


