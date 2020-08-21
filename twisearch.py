from selenium.common.exceptions import TimeoutException, JavascriptException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep

#-----------------------------------------------------------Usage-----------------------------------------------------------------#
# ### Change EXECUTABLE_PATH variable below to the path to chromedriver ###
# ### Code:                                                             ###
# from twisearch import twitterSearch
# results = twitterSearch(query = "Pakistan News")
# print(results)
#---------------------------------------------------------------------------------------------------------------------------------#

EXECUTABLE_PATH = './chromedriver'

def setDriver(executable_path, headless = False, maximize = True):
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    chrome_options.add_experimental_option("prefs",prefs)
    if maximize:
        chrome_options.add_argument("--start-maximized")
    if headless:
        chrome_options.add_argument("--headless")
    return webdriver.Chrome(executable_path = executable_path, chrome_options=chrome_options)

def scroll(driver, numScrolls = 20000, fastScroll = False):
    scroll_time = 8
    if fastScroll:
        driver.execute_script("document.body.style.transform = 'scale(0.05)'")
    current_scrolls = 0
    old_height = 0
    sleep(0.5)
    while True:
        try:
            if current_scrolls == numScrolls:
                return
            try:
                old_height = driver.execute_script("return document.body.scrollHeight")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                WebDriverWait(driver, scroll_time, 0.05).until(
                    lambda driver: check_height(driver, old_height)
                )
                current_scrolls += 1
            except JavascriptException:
                pass
        except TimeoutException:
            break
    driver.execute_script("document.body.style.transform = 'scale(1.00)'")
    return

def check_height(driver, old_height):
    new_height = driver.execute_script("return document.body.scrollHeight")
    return new_height != old_height

def twitterSearch(query, scrollDepth = 3):
    driver = setDriver(executable_path = EXECUTABLE_PATH)
    query = query.lower()
    url = f'https://twitter.com/search?q={query}&src=typed_query&f=user'
    wait = WebDriverWait(driver, 10)
    driver.get(url)
    try:
        element = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Timeline: Search timeline"]')))
        scroll(driver, numScrolls = scrollDepth)
        wait.until(EC.visibility_of_all_elements_located((By.XPATH, '//div[@data-testid="UserCell"]')))
    except KeyboardInterrupt:
        raise Exception("Interrupted")
    except TimeoutException:
        print("Failed")
        return []
    results = []
    soup = BeautifulSoup(element.get_attribute("innerHTML"), "html.parser")
    for data in soup.find_all('div', {'data-testid': 'UserCell'}):
        result = {
            "id": "",
            "username": "",
            "full_name": "",
            "picture_url": ""
        }
        a = data.find('a')
        if a:
            user = a.get('href', '')
            if user != '':
                username = user.split('/')[-1]
                result["username"] = username
            i = data.find('img')
            if i:
                result["picture_url"] = i.get('src', '')
            a = a.findNext('a')
            if a:
                username = a.get('href', '')
                if user == username:
                    a = a.find('span')
                    if a:
                        result["full_name"] = a.text
        a = data.find(lambda tag: tag.name == 'div' and '-follow' in tag.get('data-testid', ''))
        if a:
            result["id"] = a.get('data-testid', '').partition('-')[0]
        results.append(result)
    driver.close()
    return {
        "site": "twitter",
        "data": results
    }
