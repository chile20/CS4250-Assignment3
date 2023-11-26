# -------------------------------------------------------------------------
# AUTHOR: Chi Le
# FILENAME: parser.py
# SPECIFICATION: The program reads and parses CS faculty information persisted in MongoDB,
# extracting faculty members' name, title, office, email, and website using BeautifulSoup and PyMongo.
# The parsed data is then stored in the MongoDB collection named "professors".
# FOR: CS 4250- Assignment #3
# TIME SPENT: 2.5h
# -----------------------------------------------------------*/
from pymongo import MongoClient
from bs4 import BeautifulSoup
import re

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

def store(collection, name, title, office, email, website):
    data = {
        '_id': collection.count_documents({}) + 1,
        'name': name,
        'title': title,
        'office': office,
        'email': email,
        'website': website
    }
    collection.insert_one(data)

def parse(collection, content):
    try:
        name = content.h2.text
        title = content.find('strong', string=re.compile('Title')).next_sibling.get_text().strip()
        office = content.find('strong', string=re.compile('Office')).next_sibling.get_text().strip()
        email = content.find('strong', string=re.compile('.*Email.*')).find_next('a').get('href').replace("mailto:", "")
        website = content.find('strong', string=re.compile('.*Web.*')).find_next('a').get('href')
        store(collection, name, title, office, email, website)
    except Exception as e:
        return

db = connectDataBase()
pages = db.pages
professors = db.professors
query = {"isTarget": True}
result = pages.find_one(query)

if result:
    url = result.get("url")
    html_content = result.get("html")
    bs = BeautifulSoup(html_content, 'html.parser')
    divs = bs.find_all('div', {'class': 'clearfix'})
    for div in divs:
        parse(professors, div)