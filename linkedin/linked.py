from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup


COOKIE = {
    'name': 'li_at',
    'value': 'AQEDAS6tx2ACzBj1AAABbxfJiXQAAAFw0nROGlEAQE_aYJ8eicWyTAl_HJZlFC2DBYmtLe38Mwuzk5peiD0qUtwCwXhbudahOnLSROoq-AFTbnFGDfpawiUfi9-T5xgOh7hQrP11iTDovnCU4DLRdJom'
    }

def setDriver(executable_path):
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    chrome_options.add_experimental_option("prefs",prefs)
    return webdriver.Chrome(executable_path = executable_path, chrome_options=chrome_options)

def loginLinkedIn(driver, loginCredentials):
    wait = WebDriverWait(driver, 15)
    email = loginCredentials["email"]
    password = loginCredentials["password"]
    driver.get("https://www.linkedin.com/login")
    try:
        user = wait.until(EC.presence_of_element_located((By.ID, 'username')))
    except TimeoutException:
        print("Failed")
        return None
    try:
        pwd = driver.find_element_by_id('password')
    except NoSuchElementException:
        print("Failed")
        return None
    user.send_keys(email)
    pwd.send_keys(password)
    try:
        driver.find_element_by_xpath('//button[@aria-label="Sign in"]').click()
    except NoSuchElementException:
        print("Failed")
    cookie = driver.get_cookie('li_at')
    if not cookie:
        print('login failed. Security verification required')
    return driver

def getLinkedInCookies(driver, *args):
    cookies = []
    for arg in args:
        cookies.append(driver.get_cookie(arg))
    return cookies

def getResults(content, entityType):
    soup = BeautifulSoup(content, "html.parser")
    ul = soup.find('ul', {'class': 'search-results__list'})
    results = []
    if ul:
        for li in ul.find_all('li', {'class': 'search-result'}):
            result = {}
            user = li.find('div', {'class': 'search-result__info'})
            if user:
                res = user.find('a').get('href')
                if res:
                    result["username"] = res.split("/")[2]
                if entityType == "people":
                    res = user.find('span', {'class': 'actor-name'})
                else:
                    res = user.find('h3', {'class': 'search-result__title'})
                if res:
                    result["full_name"] = " ".join([a for a in res.text.replace("\n", "").split() if not a == ""])
            img = li.find('div', {'class': 'search-result__image-wrapper'})
            if img:
                img = img.find('img')
                if img:
                    result["picture_url"] = img.get('src')
            for al in ["username", "full_name", "picture_url", "id"]:
                if not result.get(al):
                    result[al] = ""
            if result["username"] != "":
                results.append(result)
    return results

def search(driver, keywords, entityType = "people", depth = 2):
    driver.get("https://www.linkedin.com")
    if not driver.get_cookie('li_at'):
        driver.add_cookie(COOKIE)
    wait = WebDriverWait(driver, 10)
    query = "+".join(keywords.split())
    url = f'https://linkedin.com/search/results/{entityType}/?keywords={query}&origin=GLOBAL_SEARCH_HEADER'
    driver.get(url)
    r = driver.find_elements_by_xpath('//div[contains(@class, "search-result__info")]')
    if len(r) != 0:
        driver.execute_script("arguments[0].scrollIntoView();", r[-1])
    results = getResults(driver.page_source, entityType)
    if len(results) == 0:
        return []
    iteration = 1
    while(iteration < depth):
        iteration += 1
        driver.get(url + f'&page={str(iteration)}')
        r = driver.find_elements_by_xpath('//div[contains(@class, "search-result__info")]')
        if len(r) != 0:
            driver.execute_script("arguments[0].scrollIntoView();", r[-1])
        result = getResults(driver.page_source, entityType)
        if len(result) == 0:
            break
        results += result
    return {
        "site": "linkedin",
        "data": results
    }
