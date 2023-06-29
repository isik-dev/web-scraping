import time
import json
import requests
import pandas as pd
import concurrent.futures
from bs4 import BeautifulSoup

# ====================================================================================
originURL = 'https://twu.tennis-warehouse.com/cgi-bin/compareracquets.cgi'
racketUrl = 'https://twu.tennis-warehouse.com/cgi-bin/compareracquetsdata.cgi'
# ====================================================================================


# @@@ requests method @@@
optionListtm1 = time.perf_counter()
optionsList = requests.get(originURL)
soup = BeautifulSoup(optionsList.text, 'html.parser')
optionListtm2 = time.perf_counter()
print(
    f'Total time to fetch options list: {optionListtm2-optionListtm1:0.2f} seconds')
print('####################################')

# Extract values from option tag
valuestm1 = time.perf_counter()
values = []
options = soup.select('option')
for option in options:
    if option['value'] != 'none' and 'racquetB' not in option['value']:
        values.append(option['value'])
valuestm2 = time.perf_counter()
print(f'Total time to extract values: {valuestm2-valuestm1:0.2f} seconds')
print(f'Total # of values extracted: {len(values)}')
print('####################################')

# Create urls list
targetURLListtm1 = time.perf_counter()
targetURLList = []
for v in values:
    targetURLList.append(f'{racketUrl}?{v}')
targetURLListtm2 = time.perf_counter()
print(f'Total time to create target url list: {targetURLListtm2-targetURLListtm1:0.2f} seconds')
print(f'Total # of target URLs created: {len(targetURLList)}')
print('####################################')


urls = targetURLList
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

print('#################################################')
print('################# Concurrency ###################')
print(f'Took {time2-time1:.2f} s')
print(f'Total # of requests made: {len(out)}')
print('#################################################')

# convert out to regular shape and sort alphabetically
jsontm1 = time.perf_counter()
regular_list = []
for item in out:
    parsed_item = json.loads(item)
    regular_list.append(parsed_item)
sorted_list = sorted(regular_list, key=lambda x: x['mfg'])
jsontm2 = time.perf_counter()
print(f'Total time to normalize and sort: {jsontm2-jsontm1:0.2f} seconds')
print('#################################################')


# Create an empty DataFrame
csvtm1 = time.perf_counter()
df = pd.DataFrame(columns=['index', 'mfg', 'racket', 'headsize', 'length', 'weight', 'balance', 'swingweight', 'flex', 'acor', 'sweet', 'twistweight', 'vibration'])
# Iterate over the out and extract the values
for i, item in enumerate(sorted_list):
    mfg = item['mfg']
    racquet = item['racquet']
    headsize = item['headsize']
    length = item['length']
    weight = item['weight']
    balance = item['balance']
    swingweight = item['swingweight']
    flex = item['flex']
    acor = item['acor']
    sweet = item['sweet']
    twistweight = item['twistweight']
    vibration = item['vibration']

    # unclear
    pcode = item['pcode']
    rccode = item['rccode']
    units = item['units']
    changed = item['changed']
    current = item['current']  # probably means selected from options

    # Append the extracted values to the DataFrame
    df = df._append({
                     'index': i,
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
csvtm2 = time.perf_counter()

print(f'Total time write and create csv: {csvtm2-csvtm1:0.2f} seconds')
print('####################################')
