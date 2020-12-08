from time import sleep

import pandas as pd
from tabulate import tabulate

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

## LOAD RESULTS ####################################

all_results = pd.read_excel('results.xlsx')
results = all_results[all_results['Email'] == '-']

print(results['Company'])

results['hash'] = results['Company'].apply(lambda x: x.lower().replace('.com', '').replace(' inc.', '').replace(' llc.', '').replace(' ltd.', '').replace(',', '').replace('-', '').replace(' inc', '').replace(' llc', '').replace(' ltd', '').replace('foundation', '').strip())
companies = results['hash'].unique()

## LOAD DRIVER #####################################

driver = webdriver.Chrome(ChromeDriverManager().install())

## GET EMAILS ######################################

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
        urls = [url.text.replace(' › ', '/') for url in urls if ('rocketreach.co' in url.text or 'email-format' in url.text)]
        if len(urls) > 0:
            url = urls[0] if 'https://' in urls[0] else 'https://' + urls[0]
            driver.get(url)
            sleep(3)
            return True
        
        return False
    
    cond = follow_link() if company != '' else False
    
    if cond:
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
            
        df = None

        try:
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
        except NoSuchElementException:
            pass
        
        if df is None:
            print('could not find data for ' + str(company))

        dic[company] = df

driver.quit()

## PROCESS EMAILS ##################################

profiles = []

def process_df(result, df):
    def f(z):
        x, y = z.split('@')
        x = x.replace('jane', '1').replace('doe', '2').replace('j', '3').replace('d', '4')
        x = x.replace('1', result['First'].lower()).replace('2', result['Last'].lower()).replace('3', result['First'][0].lower()).replace('4', result['Last'][0].lower())
        return x + '@' + y
    return list(df['example'].apply(f))

for i in range(results.shape[0]):
    result = results.iloc[i]
    if result is not None:
        try:
            value = dic[result['hash']]
            formats = process_df(result, value)
            for f in formats:
                profile = [result['First'], result['Last'], result['Role'], result['Company'], f]
                print(profile)
                profiles.append(profile)
        except KeyError:
            pass

emails = pd.read_excel('emails.xlsx')
append = pd.DataFrame(profiles, columns=['First', 'Last', 'Role', 'Company', 'Email'])
emails = emails.append(append)

profile_set = set()
set_emails = []
for i in range(emails.shape[0]):
    email = list(emails.iloc[i])
    hsh = str(email)
    if hsh not in profile_set:
        profile_set.add(hsh)
        set_emails.append(email)

emails = pd.DataFrame(data=set_emails, columns=['First', 'Last', 'Role', 'Company', 'Email'])
emails.to_excel('emails.xlsx', index=False)

all_results['Email'] = all_results['Email'].apply(lambda x: 'in emails.xlsx')
all_results.to_excel('results.xlsx', index=False)