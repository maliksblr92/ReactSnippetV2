from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, ElementNotInteractableException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep

# Change this
EXECUTABLE_PATH = "./geckodriver"

## Usage
# from insta import insta_followers
# results = insta_followers(username = "imrankhanpti")


INSTA_URL = "https://www.instagram.com/"
COOKIE = {
    "name":"sessionid",
    "value": "31549332914%3Ad7cb3sp99cMeiq%3A12"
}


def setDriver(executable_path = EXECUTABLE_PATH, headless = True):
    fp = webdriver.FirefoxProfile()
    fp.set_preference("permissions.default.desktop-notification", 2)
    options = webdriver.FirefoxOptions()
    options.add_argument('-headless')
    options.headless = headless
    caps = DesiredCapabilities().FIREFOX
    caps["pageLoadStrategy"] = "eager"
    return webdriver.Firefox(executable_path = executable_path, firefox_options = options, firefox_profile = fp, capabilities = caps)

def completeInstaLink(string):
    if string.startswith("/"):
        string = INSTA_URL + string[1:]
    return string

def insta_followers(username = "", url = ""):
    if username:
        url = INSTA_URL + username
    if url:
        text = ""
        with setDriver() as driver:
            driver.get(INSTA_URL)
            driver.add_cookie(COOKIE)
            sleep(0.5)
            driver.get(url)
            wait = WebDriverWait(driver, 10)
            try:
                WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//*[text()="Sorry, this page isn\'t available."]')))
                print("Invalid profile")
                return []
            except TimeoutException:
                pass
            try:
                element = wait.until(EC.visibility_of_element_located((By.XPATH, '//a[contains(@href, "/followers/")]')))
                driver.execute_script("arguments[0].click();", element)
                element = wait.until(EC.visibility_of_element_located((By.XPATH, '//ul[contains(@class, "jSC57")]')))
                for _ in range(10):
                    s = driver.find_elements_by_xpath('//a[contains(@class, "notranslate")]')[-1]
                    driver.execute_script("arguments[0].scrollIntoView();", s)
                    sleep(0.2)
                text = element.get_attribute("innerHTML")
            except (NoSuchElementException, TimeoutException, StaleElementReferenceException, ElementNotInteractableException):
                print("Failed")
                return []
        results = []
        if text:
            soup = BeautifulSoup(text, "html.parser")
            for li in soup.find_all('li', {'class': 'wo9IH'}):
                result = {
                    "full_name": "",
                    "username": "",
                    "url": "",
                    "picture_image_url": ""
                }
                a = li.find('a')
                if a:
                    result["url"] = completeInstaLink(a.get("href", ""))
                    i = a.find('img')
                    if i:
                        result["picture_image_url"] = i.get('src', '')
                a = li.find('a', {'class': 'notranslate'})
                if a:
                    result["username"] = a.text
                    a = a.findNext('div')
                    if a:
                        result["full_name"] = a.text
                if result.get("username"):
                    results.append(result)
        return results
    else:
        print("Please provide one of username or url")
        return []