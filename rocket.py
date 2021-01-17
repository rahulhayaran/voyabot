import parameters

from time import sleep

import pandas as pd
from tabulate import tabulate

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

## LOAD RESULTS ####################################

all_results = pd.read_excel('results.xlsx', engine='openpyxl')
results = all_results[all_results['Email'] == '-']

def hash_name(x):
    return x.lower().replace('.com', '')\
        .replace(' inc.', '')\
        .replace(' llc.', '')\
        .replace(' ltd.', '')\
        .replace(',', '')\
        .replace('-', '')\
        .replace(' inc', '')\
        .replace(' llc', '')\
        .replace(' ltd', '')\
        .replace('foundation', '')\
        .strip()

results['hash'] = results['Company'].apply(hash_name)
companies = results['hash'].unique()
found_companies = []

## LOAD DRIVER #####################################

driver = webdriver.Chrome(ChromeDriverManager().install())

## GET EMAILS ######################################

dic = dict()

for company in companies:
    def follow_link():
        driver.get('https://www.bing.com')
        sleep(3)

        search_query = driver.find_element_by_name('q')
        search_query.send_keys('"site: rocketreach.co" + ' + '"' + str(company) + '"' + ' + "email format"')
        sleep(0.5)

        search_query.send_keys(Keys.RETURN)
        sleep(3)

        urls = driver.find_elements_by_class_name('b_attribution')
        urls = [url.text.replace(' › ', '/') for url in urls if ('rocketreach.co' in url.text and 'email-format' in url.text)]
        if len(urls) > 0:
            url = urls[0] if 'https://' in urls[0] else 'https://' + urls[0]
            driver.get(url)
            sleep(3)
            return True
        
        return False
    
    is_url = follow_link() if company != '' else False
    
    if is_url:
        # check if the site is really a rocketreach table
        while True:
            is_url = True
            try:
                dumb_ad = driver.find_element_by_class_name('modal-title ng-binding ng-scope')
                follow_link()
            except NoSuchElementException:
                is_url = False
                pass
            if not is_url:
                break
            
        df = pd.DataFrame([])

        # try getting a rocketreach table
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

            found_companies.append(company)
            print(txt)

            with open('company_formats/' + str(company) + '.txt', 'w') as f:
                f.write(txt)
        except NoSuchElementException:
            pass
        
        if df.empty:
            print('could not find data for ' + str(company))

        dic[company] = df

driver.quit()

## PROCESS EMAILS ##################################

dupes = results[results['Last'].str.contains(" ") | results['Last'].str.contains("-")]
dupes['Last'] = dupes['Last'].str.replace('-', ' ').str.split().str[-1]
results['Last'] = results['Last'].str.replace('-', '').str.replace(' ', '')
results = pd.concat([results, dupes])

profiles = []

def process_df(result, df):
    def f(z):
        if z is not None and '@' in z:
            x, y = z.split('@')
            x = x.replace('jane', '1').replace('doe', '2').replace('j', '3').replace('d', '4')
            x = x.replace('1', result['First'].lower()).replace('2', result['Last'].lower()).replace('3', result['First'][0].lower()).replace('4', result['Last'][0].lower())
            return x + '@' + y
        return None

    if df.empty:
        return None 
    else:
        df['frequency'] = df['frequency'].apply(lambda x: float(x.replace('%', '') if type(x) == str else x))
        
        df = df[df['frequency'] >= parameters.frequency_threshold]
        
        first = list(df[df['format'] == 'first']['frequency'])
        if first and len(first) > 0 and first[0] < parameters.first_at_threshold:
            df = df[df['format'] != 'first']

        return list(df['example'].apply(f))

for i in range(results.shape[0]):
    result = results.iloc[i]
    if result is not None:
        try:
            value = dic[result['hash']]
            formats = process_df(result, value)
            if formats is not None:
                for f in formats:
                    profile = [result['First'], result['Last'], result['Role'], result['Company'], result['Link'], f]
                    print(profile)
                    profiles.append(profile)
        except KeyError:
            pass

emails = pd.read_excel('emails.xlsx', engine='openpyxl')
append = pd.DataFrame(profiles, columns=['First', 'Last', 'Role', 'Company', 'Link', 'Email'])
emails = emails.append(append)

profile_set = set()
set_emails = []
for i in range(emails.shape[0]):
    email = list(emails.iloc[i])
    hsh = str(email)
    if hsh not in profile_set:
        profile_set.add(hsh)
        set_emails.append(email)

emails = pd.DataFrame(data=set_emails, columns=['First', 'Last', 'Role', 'Company', 'Link', 'Email'])
emails.to_excel('emails.xlsx', index=False, engine='openpyxl')

for i in range(all_results.shape[0]):
    all_results['Email'][i] = 'in emails.xlsx' if all_results['Email'][i] == 'in emails.xlsx' or hash_name(all_results['Company'][i]) in found_companies else 'NEED TO SOURCE MANUALLY!!!'

all_results.to_excel('results.xlsx', index=False, engine='openpyxl')