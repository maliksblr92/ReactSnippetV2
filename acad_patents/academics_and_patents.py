from bs4 import BeautifulSoup
import requests

def scholar(query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    s = requests.Session()
    query = '+'.join(query.split())
    url = f'https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={query}&btnG='
    r = s.get(url, headers = headers)
    soup = BeautifulSoup(r.text, "html.parser")
    output = []
    for one in soup.find_all('div', {'class': 'gs_r gs_or gs_scl'}):
        result = {
            "title": "",
            "link": "",
            "publish_data": {
                "authors": "",
                "journal/conference": "",
                "site": ""
            },
            "pdf": {
                "site": "",
                "link": ""
            },
            "partial_summary": "",
            "citations": "",
            "versions": ""
        }
        a = one.find('div', {'class': 'gs_or_ggsm'})
        if a:
            a = a.find('a')
            if a:
                result["pdf"]["link"] = a.get('href', '')
                result["pdf"]["site"] = a.text.partition('[PDF]')[2]
        a = one.find(True, {'class': 'gs_rt'})
        if a:
            a = a.find('a')
            if a:
                result['title'] = a.text
                result['link'] = a.get('href', '')
        a = one.find('div', {'class': 'gs_a'})
        if a:
            a = a.text
            result['publish_data']['authors'] = a.partition(" - ")[0]
            result['publish_data']['journal/conference'] = a.partition(" - ")[2].partition("-")[0]
            result['publish_data']['site'] = a.partition(" - ")[2].partition(" - ")[2]
        a = one.find('div', {'class': 'gs_rs'})
        if a:
            result['partial_summary'] = a.text
        a = one.find(lambda tag: tag.name == "a" and "Cited by " in tag.text)
        if a:
            result['citations'] = a.text.partition('Cited by ')[2]
        a = one.find(lambda tag: tag.name == "a" and "version" in tag.text)
        if a:
            result['versions'] = a.text.partition('All ')[2].partition(' version')[0]
        output.append(result)
    return output

def patents(query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    s = requests.Session()
    query = '+'.join(query.split())
    url = f'https://www.google.com/search?tbm=pts&q={query}&ie=utf-8&oe=utf-8'
    r = s.get(url, headers = headers)
    soup = BeautifulSoup(r.text, "html.parser")
    output = []
    for one in soup.find_all('div', {'class': 'rc'}):
        result = {
            "title": "",
            "link": "",
            "cited_link": "",
            "inventors": [],
            "partial_description": "",
            "status": "",
            "filing_date": "",
            "issued_date": "",
            "published_date": ""
        }
        a = one.find('a')
        if a:
            b = a.find(True, {'class': "LC20lb DKV0Md"})
            if b:
                result['title'] = b.text
            else:
                b = a.find('h3')
                if b:
                    result['title'] = b.text
            result['link'] = a.get('href', '')
        a = one.find('cite')
        if a:
            result['cited_link'] = a.text
        a = one.find('div', {'class': 'dhIWPd f'})
        if a:
            for b in a.find_all('a', {'class': 'fl'}):
                person = {
                    "name": "",
                    "google_inventor_search_link": "",
                }
                person['name'] = b.text
                link = b.get('href')
                if link.startswith('/'):
                    link = 'https://www.google.com' + link
                person["google_inventor_search_link"] = link
                result["inventors"].append(person)
            a = a.text
            result['status'] = a.partition(" - ")[0]
            result['filing_date'] = a.partition(" - ")[2].partition(" - ")[0].replace("Filed ", "").replace("\u200e", "")
            ipub = a.partition(" - ")[2].partition(" - ")[2].partition(" - ")[0]
            if "Issued" in ipub:
                result["issued_date"] = ipub.replace("Issued ", "").replace("\u200e", "")
            elif "Published" in ipub:
                result["published_date"] = ipub.replace("Published ", "").replace("\u200e", "")
            
        a = one.find('span', {'class': 'st'})
        if a:
            result["partial_description"] = a.text
        output.append(result)
    return output
