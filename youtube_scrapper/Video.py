from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, NoSuchElementException, JavascriptException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from youtube_transcript_api import YouTubeTranscriptApi
import json
from time import sleep
import re
import time
driver=""

def channel_information():
    elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="top-row"]/ytd-video-owner-renderer')))
    for element in elements:
        html_text = element.get_attribute("innerHTML")
        soup = BeautifulSoup(html_text, 'html.parser')

        channel_information={
                "channel_image":soup.find("img").attrs.get("src"),
                "channel_name":soup.find("a", class_="yt-simple-endpoint style-scope yt-formatted-string").text,
                "channel_link":soup.find("a", class_="yt-simple-endpoint style-scope yt-formatted-string").attrs.get("href"),
                "subscribers":soup.find(id="owner-sub-count").text
        }

        return channel_information

def video_information():
    try:
        element = driver.find_element_by_xpath('//yt-formatted-string[text()="Show more"]')
        driver.execute_script("arguments[0].click();", element)
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//yt-formatted-string[text()="Category"]')))
        html=driver.page_source
     
        soup = BeautifulSoup(html, 'html.parser')
        contents= soup.findAll( id="content")


        descriptions=contents[0].find('script', id ="scriptTag").text
        description=json.loads(descriptions)

        cat = soup.find('yt-formatted-string', text = "Category")
        if cat:
            cat = cat.findNext('a', class_="yt-simple-endpoint style-scope yt-formatted-string")
            if cat:
                cat = cat.text
        else:
            cat = ""
       
        general_info=soup.findAll("yt-formatted-string", class_="style-scope ytd-toggle-button-renderer style-text")
        video_information={
            "likes":general_info[0].attrs.get("aria-label"),
            "dislikes":general_info[1].attrs.get("aria-label"),
            "category":cat
            # contents[4].find("a", class_="yt-simple-endpoint style-scope yt-formatted-string")
        }
        return video_information, description
    except Exception as e:
        print(e)




def get_comments(scroll=500):

    elem = driver.find_element_by_tag_name("body")
    comments_data=[]
   
    
    while scroll:
        elem.send_keys(Keys.PAGE_DOWN)
        scroll-=1
        
    comments = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//*[@id='contents']/ytd-comment-thread-renderer")))
    
    html_text=driver.page_source
    soup = BeautifulSoup(html_text, 'html.parser')
    no_comments=soup.find("h2", id="count").text

    for comment in comments:
        html_text=comment.get_attribute("innerHTML")
        soup = BeautifulSoup(html_text, 'html.parser')
        comment_={
                "name":soup.find("img", id="img").attrs.get("alt"),
                "image":soup.find("img", id="img").attrs.get("src"),
                "time":soup.find("a" ,class_="yt-simple-endpoint style-scope yt-formatted-string").text,
                "text": soup.find(id="content-text").text,
                "likes":soup.find("span", id="vote-count-middle").attrs.get("aria-label"),

        }
        comments_data.append(comment_)
    
    return comments_data, no_comments




def video_scrapper( driver_,video_id="",):
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--start-maximized")
    global driver
    driver=driver_
    #driver=webdriver.Chrome(executable_path="./chromedriver", chrome_options=chrome_options)
    driver.get(f"https://www.youtube.com/watch?v={video_id}")
    channel_info= channel_information()
    video_info, descriptions=video_information()
    comment_data, number_of_comments=get_comments()
    subtitiles=video_subtitle(video_id)
    data={
        "channel_information":channel_info,
        "video_information":video_info,
        "description":descriptions,
        "number_of_comments":number_of_comments,
        "comments":comment_data,
        "subtitles":subtitiles
    }

    return data


def video_subtitle(videoID=""):
    data="subtitle are not enabled"
    try:
        data=YouTubeTranscriptApi.get_transcript(videoID)
        return data
    except Exception:
        return data