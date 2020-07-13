import parameters

from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

from parsel import Selector

import numpy as np
import pandas as pd
from tabulate import tabulate

driver = webdriver.Chrome(parameters.chromedriver)

results = pd.read_excel('results.xlsx')
results['hash'] = results['Company'].apply(lambda x: x.lower().replace('.com', '').replace(' inc.', '').replace(' llc.', '').replace(' ltd.', '').replace(' inc', '').replace(' llc', '').replace(' ltd', '').strip())
companies = results['hash'].unique()

dic = dict()

for company in companies:
    def follow_link():
        driver.get('https://www.bing.com')
        sleep(3)

        search_query = driver.find_element_by_name('q')
        search_query.send_keys('"rocket reach"+' + '"' + str(company) + '"' + '+"email format"')
        sleep(0.5)

        search_query.send_keys(Keys.RETURN)
        sleep(3)

        urls = driver.find_elements_by_class_name('b_attribution')
        urls = [url.text.replace(' › ', '/') for url in urls if ('rocketreach.co' in url.text and 'email-format' in url.text)]
        url = urls[0] if 'https://' in urls[0] else 'https://' + urls[0]
        driver.get(url)
        sleep(3)
    
    follow_link()

    while True:
        cond = True
        try:
            dumb_ad = driver.find_element_by_class_name('modal-title ng-binding ng-scope')
            follow_link()
        except NoSuchElementException:
            cond = False
            pass
        if not cond:
            break

    table = driver.find_element_by_xpath("//*[@class='table table-bordered']")
    rows = len(table.find_elements_by_xpath("//tr")) - 1
    cols = len(table.find_elements_by_xpath("//tr[2]/td"))
    data = []
    for i in range(1, rows + 1):
        row = []
        for j in range(1, cols + 1) :
            row.append(table.find_element_by_xpath("//tr["+str(i)+"]/td["+str(j)+"]").text)
        data.append(row)
    df = pd.DataFrame(data=data, columns=['format', 'example', 'frequency'])

    txt = str(company) + '\n' + tabulate(df, headers='keys', tablefmt='psql', showindex=False)
    
    print(txt)

    with open('company_formats/' + str(company) + '.txt', 'w') as f:
        f.write(txt)
    
    dic[company] = df

driver.quit()

profiles = []

def process_df(result, df):
    def f(z):
        x, y = z.split('@')
        x = x.replace('jane', result['First'].lower()).replace('doe', result['Last'].lower()).replace('j', result['First'][0].lower()).replace('d', result['Last'][0].lower())
        return x + '@' + y
    return list(df['example'].apply(f))

for i in range(results.shape[0]):
    result = results.iloc[i]
    formats = process_df(result, dic[result['hash']])
    for f in formats:
        profiles.append([result['First'], result['Last'], result['Job Title'], result['Company'], result['LinkedIn URL'], f])

emails = pd.read_excel('emails.xlsx')
append = pd.DataFrame(profiles, columns=['First', 'Last', 'Job Title', 'Company', 'LinkedIn URL', 'Email'])
emails = emails.append(append)

profile_set = set()
set_emails = []
for i in range(emails.shape[0]):
    email = list(emails.iloc[i])
    hsh = str(email)
    if hsh not in profile_set:
        profile_set.add(hsh)
        set_emails.append(email)

emails = pd.DataFrame(data=set_emails, columns=['First', 'Last', 'Job Title', 'Company', 'LinkedIn URL', 'Email'])
emails.to_excel('emails.xlsx', index=False)