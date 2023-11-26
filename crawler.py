#-------------------------------------------------------------------------
# AUTHOR: Chi Le
# FILENAME: crawler.py
# SPECIFICATION: The program retrieves and parses HTML content from linked pages of the CS department
# website at CPP, searching for the page with the "Permanent Faculty" heading.
# Extracted data, including URLs, titles, and content,
# is stored in a MongoDB collection named "pages" for persistence.
# FOR: CS 4250- Assignment #3
# TIME SPENT: 5h
#-----------------------------------------------------------*/
from pymongo import MongoClient
from bs4 import BeautifulSoup
import re
from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError
from urllib.parse import urljoin

#Connect to database
def connectDataBase():
    DB_NAME = "CPP"
    DB_HOST = "localhost"
    DB_PORT = 27017
    try:
        client = MongoClient(host=DB_HOST, port=DB_PORT)
        db = client[DB_NAME]
        return db
    except:
        print("Database not connected successfully")

# Class to manage the list of URLs to visit
class Frontier:
    def __init__(self, initial_url):
        self.urls = [initial_url]
        self.visited = set()

    def add_url(self, url):
        if url not in self.visited and url not in self.urls:
            self.urls.append(url)

    def next_url(self):
        if not self.urls:
            return None
        url = self.urls.pop(0)
        self.visited.add(url)
        return url

    def done(self):
        return not self.urls

    def clear_frontier(self):
        self.urls = []

# Retrieve HTML content from a URL
def retrieve_url(url):
    try:
        html = urlopen(url)
        return html.read().decode(encoding="iso-8859-1")
    except HTTPError as e:
        # print(e)
        return None
    except URLError as e:
        # print('The server could not be found!')
        return None

# Store page data in MongoDB
def store_page(collection, url, html, bool):
    data = {
        '_id': collection.count_documents({}) + 1,
        'url': url,
        'html': html,
        'isTarget': bool
    }
    collection.insert_one(data)

# Check if the page contains the target heading
def target_page(html):
    bs = BeautifulSoup(html, 'html.parser')
    heading = bs.find('h1', string='Permanent Faculty')
    return heading

# Extract links from HTML
def parse(html):
    bs = BeautifulSoup(html, 'html.parser')
    links = bs.find_all('a', href=True)
    return [link['href'] for link in links]

# Crawler main function
def crawler_thread(collection, frontier):
    crawled_pages = []
    while not frontier.done():
        is_target = False
        url = frontier.next_url()
        crawled_pages.append(url)
        html = retrieve_url(url)

        if html:
            if target_page(html):
                print(f"Target page found: {url}")
                is_target = True
                frontier.clear_frontier()
            else:
                for new_url in parse(html):
                    new_url = new_url.strip()
                    is_absolute = re.search('^http', new_url)
                    if is_absolute:
                        full_url = new_url
                    else:
                        full_url = urljoin(url, new_url)
                    if full_url not in frontier.urls and full_url not in crawled_pages:
                        frontier.add_url(full_url)
        store_page(collection, url, html, is_target)

def main():
    db = connectDataBase()
    pages = db.pages
    base_url = "https://www.cpp.edu/sci/computer-science/"
    frontier = Frontier(base_url)
    frontier.add_url(base_url)
    crawler_thread(pages, frontier)

if __name__ == '__main__':
    main()