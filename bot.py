import parameters

from time import sleep

import numpy as np
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

## LOAD DRIVER #####################################

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get('https://www.linkedin.com/login?trk=homepage-basic_conversion-modal-signin')

## SIGN-IN #########################################

username = driver.find_element_by_xpath('//*[@id="username" and @name="session_key"]')
username.send_keys(parameters.linkedin_username)
sleep(0.5)

password = driver.find_element_by_xpath('//*[@id="password" and @name="session_password"]')
password.send_keys(parameters.linkedin_password)
sleep(0.5)

sign_in_button = driver.find_element_by_xpath('//*[@type="submit"]')
sign_in_button.click()
sleep(0.5)

## READ PROFILES ###################################

pages = parameters.pages
queries = pd.read_excel('queries.xlsx', engine='openpyxl')['Roles']
names, tags = [], []

for query in queries:
    driver.execute_script("document.body.style.zoom='100%'")
    sleep(0.5)

    _ = input('\n---\nDone using LinkedIn filters? Press enter to continue')
    search_url = driver.current_url

    for role in query.split(', '):
        driver.get(search_url)
        sleep(0.5)

        search = driver.find_element_by_xpath('//*[@class="search-global-typeahead__input always-show-placeholder"]')
        search.send_keys(Keys.CONTROL + "a")
        sleep(0.8)

        search.send_keys(Keys.DELETE)
        sleep(0.8)

        search.send_keys(role + '\n')
        sleep(0.8)

        driver.execute_script("document.body.style.zoom='30%'")
        url = driver.current_url
        sleep(0.5)

        for i in range(1, pages + 1):
            if i != 1:
                page = '' if i == 0 else '&page=' + str(i)
                driver.get(url + page)
                driver.execute_script("document.body.style.zoom='30%'")
            sleep(0.7)

            blocks = driver.find_elements_by_xpath('//*[@class="search-result__wrapper"]')
            for block in blocks:
                name = block.find_elements_by_xpath('.//*[@class="name actor-name"]')
                tag = block.find_elements_by_xpath('.//*[@class="subline-level-1 t-14 t-black t-normal search-result__truncate"]')
                if name and tag:
                    names.append(name[0].text)
                    tags.append(tag[0].text)
            sleep(0.7)

driver.quit()

## PROCESS PROFILES ################################

firsts, lasts, roles, companies = [], [], [], []

def is_name(names):
    proper_names = []
    for name in names:
        if len(name) > 0\
            and name.isalpha()\
            and 'PhD' not in name\
            and 'MD' not in name\
            and 'JD' not in name\
            and 'He/' not in name\
            and 'She/' not in name\
            and 'They/' not in name\
            and 'Ze/' not in name:
            proper_names.append(name)
    return proper_names

def keep_tag(tag):
    return 'software engineer' not in tag.lower()\
        and 'swe' not in tag.lower()\
        and 'software developer' not in tag.lower()\
        and 'software development engineer' not in tag.lower()\
        and 'sde' not in tag.lower()

for name, tag in zip(names, tags):
    if keep_tag(tag):
        name_split = name.replace('(', ' ').replace(')', ' ').replace(',', ' ').replace('.', '').split(' ')
        firsts.append(is_name(name_split)[0].title())
        lasts.append(is_name(name_split)[-1].title())

        tag_split = max([tag.split(' at '), tag.split(' @ '), tag.split(' — '), tag.split(' - ')], key=lambda t:len(t))
        roles.append(tag_split[0])
        companies.append(tag_split[-1] if len(tag_split) > 1 else '-')

def fix_role(role):
    return role\
        .replace('Jr.', 'Junior')\
        .replace('Jr', 'Junior')\
        .replace('Sr.', 'Senior')\
        .replace('Sr', 'Senior')\
        .replace('EVP', 'Executive Vice President')\
        .replace('SVP', 'Senior Vice President')\
        .replace('AVP', 'Associate Vice President')\
        .replace('VP', 'Vice President')\
        .replace('PM', 'Product Manager')\
        .replace('SWE', 'Software Engineer')\
        .replace('DS', 'Data Scientist')\
        .replace('CEO', 'Chief Executive Officer')\
        .replace('COO', 'Chief Operating Officer')\
        .replace('CFO', 'Chief Financial Officer')\
        .replace('CTO', 'Chief Technology Officer')\
        .replace('CDO', 'Chief Data Officer')\
        .replace('CIO', 'Chief Information Officer')\
        .replace('CMO', 'Chief Marketing Officer')\
        .replace('&', 'and')\

roles = [fix_role(role).title() for role in roles]

arr = np.asarray(list(zip(firsts, lasts, roles, companies, ['-'] * len(firsts))))

for a in arr:
    print(a[:-1])

results = pd.read_excel('results.xlsx', engine='openpyxl')
append = pd.DataFrame(arr, columns=['First', 'Last', 'Role', 'Company', 'Email'])
results = results.append(append)

profile_set = set()
set_results = []
for i in range(results.shape[0]):
    hsh = str(list(results.iloc[i, :-1]))
    if hsh not in profile_set:
        profile_set.add(hsh)
        set_results.append(list(results.iloc[i]))

results = pd.DataFrame(data=set_results, columns=['First', 'Last', 'Role', 'Company', 'Email'])
results.to_excel('results.xlsx', index=False, engine='openpyxl')

print("\n---\nProfiles written to 'results.xlsx' successfully!")