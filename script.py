import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
# ================================================================
# url = 'https://oxylabs.io/blog'
# # betterUrl = 'https://betterday.co.kr/'
# response = requests.get(url)

# soup = BeautifulSoup(response.text, 'html.parser')

# blog_title = soup.select('a.e1dscegp1')

# for title in blog_title:
#     print(title.text)
# ================================================================
# racketDB = 'https://twu.tennis-warehouse.com/cgi-bin/compareracquets.cgi'
# response = requests.get(racketDB)

# soup = BeautifulSoup(response.text, 'html.parser')

# targetTable = soup.select('table.simtable')

# print(soup)
# ================================================================
# driver = webdriver.Chrome()
# driver.get('https://oxylabs.io/blog')

# blog_titles = driver.find_elements(By.CSS_SELECTOR, 'a.e1dscegp1')
# for title in blog_titles:
#     print(title.text)
# driver.quit()  # closing the browser
# ================================================================
driver = webdriver.Chrome()
driver.get('https://twu.tennis-warehouse.com/cgi-bin/compareracquets.cgi')
results = []
content = driver.page_source
soup = BeautifulSoup(content, 'html.parser')

options = soup.select('option')
titles = []
for title in options:
    titles.append(title.text)
print(titles)