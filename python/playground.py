import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import time
# for concurrency
import concurrent.futures

# ================================================================
originURL = 'https://twu.tennis-warehouse.com/cgi-bin/compareracquets.cgi'
racketUrl = 'https://twu.tennis-warehouse.com/cgi-bin/compareracquetsdata.cgi'

# @@@ selenium method @@@
# driver = webdriver.Chrome()
# driver.get(originURL)
# content = driver.page_source
# soup = BeautifulSoup(content, 'html.parser')

# @@@ requests method @@@
optionListtm1 = time.perf_counter()
optionsList = requests.get(originURL)
soup = BeautifulSoup(optionsList.text, 'html.parser')
optionListtm2 = time.perf_counter()
print(
    f'Total time to fetch options list: {optionListtm2-optionListtm1:0.2f} seconds')

# Extract values from option tag
valuestm1 = time.perf_counter()
values = []
options = soup.select('option')
for option in options:
    if option['value'] != 'none':
        values.append(option['value'])
valuestm2 = time.perf_counter()
print(f'Total time to extract values: {valuestm2-valuestm1:0.2f} seconds')

# Create urls list
targetURLListtm1 = time.perf_counter()
targetURLList = []
for v in values:
    targetURLList.append(f'{racketUrl}?{v}')
targetURLListtm2 = time.perf_counter()
# print(f'Total time to create target url list: {targetURLListtm2-targetURLListtm1:0.2f} seconds')
# print(targetURLList[0])

# Fetch racket data
# racketsDatatm1 = time.perf_counter()
# for url in targetURLList:
#     res = requests.get(url)
#     print(res.status_code)
# racketsDatatm2 = time.perf_counter()

# print(f'Total time to fetch each target url in targetURLList: {racketsDatatm2-racketsDatatm1:0.2f} seconds')

urls = targetURLList[:10]

# ==============================> 1 way of concurrency: took 8.97 seconds per 100 <==============================
# def get_status(url):

#     resp = requests.get(url=url)
#     return resp.status_code

# tm1 = time.perf_counter()

# with concurrent.futures.ThreadPoolExecutor() as executor:

#     futures = []

#     for url in urls:
#         futures.append(executor.submit(get_status, url=url))

#     for future in concurrent.futures.as_completed(futures):
#         print(future.result())

# tm2 = time.perf_counter()
# print(f'Total time elapsed: {tm2-tm1:0.2f} seconds')

# ==============================> 2 way of concurrency: took 2.27 seconds per 100 <==============================
out = []
CONNECTIONS = 100
TIMEOUT = 5


def load_url(url, timeout):
    ans = requests.get(url, timeout=timeout)
    return ans.text


with concurrent.futures.ThreadPoolExecutor(max_workers=CONNECTIONS) as executor:
    future_to_url = (executor.submit(load_url, url, TIMEOUT) for url in urls)
    time1 = time.time()
    for future in concurrent.futures.as_completed(future_to_url):
        try:
            data = future.result()
        except Exception as exc:
            data = str(type(exc))
        finally:
            out.append(data)

            print(str(len(out)), end="\r")

    time2 = time.time()

print(f'Took {time2-time1:.2f} s')

# Create an empty DataFrame
# shape of data:

# ['{"pcode":"ARR","mfg":"Adidas","racquet":"Response","headsize":100,
# "length":27.00,"weight":294,"balance":34.1,"swingweight":316,"flex":64,
# "acor":40,"sweet":15,"rccode":"RCADIDAS","current":"","twistweight":12.0,
# "vibration":"145","units":"","changed":"racquetA"}']

df = pd.DataFrame(columns=['index', 'mfg', 'racket', 'headsize'])

# Iterate over the out and extract the values
for i, item in enumerate(out, start=0):
    parsed_data = eval(item)  # Parse the JSON string into a dictionary
    mfg = parsed_data['mfg']
    racquet = parsed_data['racquet']
    headsize = parsed_data['headsize']
    length = parsed_data['length']
    weight = parsed_data['weight']
    balance = parsed_data['balance']
    swingweight = parsed_data['swingweight']
    flex = parsed_data['flex']
    acor = parsed_data['acor']
    sweet = parsed_data['sweet']
    twistweight = parsed_data['twistweight']
    vibration = parsed_data['vibration']

    # unclear
    pcode = parsed_data['pcode']
    rccode = parsed_data['rccode']
    units = parsed_data['units']
    changed = parsed_data['changed']
    current = parsed_data['current']  # probably means selected from options

    # Append the extracted values to the DataFrame
    df = df._append({'index': i,
                     'mfg': mfg,
                     'racket': racquet,
                     'headsize': headsize,
                     'length': length,
                     'weight': weight,
                     'balance': balance,
                     'swingweight': swingweight,
                     'flex': flex,
                     'acor': acor,
                     'sweet': sweet,
                     'twistweight': twistweight,
                     'vibration': vibration,
                     # unclear
                     'pcode': pcode,
                     'rccode': rccode,
                     'units': units,
                     'changed': changed,
                     'current': current,
                     }, ignore_index=True)

df.to_csv('rackets.csv', index=False, encoding='utf-8')


# Below piece of code takes so much time to make when you make multiple requests, so had to improvise
# # Fetch and append individual racket data into racketsList
# dummyList = ['racquetB-IS200', 'racquetB-IS3HM', 'racquetB-SRQ7']
# rackets = []
# for value in dummyList:
#     res = requests.get(racketUrl, params=value)
#     rackets.append(res.text)
# print(rackets)


# df = pd.DataFrame({'Names': rackets})
# df.to_csv('rackets.csv', index=False, encoding='utf-8')
