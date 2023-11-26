# Homework Repository for CS 4250

**Author**: Chi Le
**Assignment**: Assignment #3

## Program: parser.py & crawler.py

### Specification
The crawler retrieves and parses HTML content from linked pages of the CS department website at CPP, searching for the page with the "Permanent Faculty" heading.
Extracted data, including URLs, titles, and content, is stored in a MongoDB collection named "pages" for persistence.

The parser reads and parses CS faculty information persisted in MongoDB, extracting faculty members' name, title, office, email, 
and website using BeautifulSoup and PyMongo. The parsed data is then stored in the MongoDB collection named "professors".
