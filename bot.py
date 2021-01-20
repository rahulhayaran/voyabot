import parameters

from time import sleep

import numpy as np
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

import unidecode

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
scraped_links, raw_links, scraped_names, raw_names, raw_roles, raw_companies = [], [], [], [], [], []

def safe_html_read(block, index=0):
    read = '-'
    if len(block) > 0:
        read = block[index].text
    return read

for query in queries:
    driver.execute_script("document.body.style.zoom='100%'")
    sleep(0.5)

    _ = input('\n---\nDone using LinkedIn filters? Press enter to continue')
    search_url = driver.current_url

    for position in query.split(', '):
        driver.get(search_url)
        sleep(0.5)

        search = driver.find_element_by_xpath('//*[@class="search-global-typeahead__input always-show-placeholder"]')
        search.send_keys(Keys.COMMAND + Keys.CONTROL + "a")
        sleep(0.8)

        search.send_keys(Keys.DELETE)
        sleep(0.8)

        search.send_keys(position + '\n')
        sleep(1.5)

        driver.execute_script("document.body.style.zoom='30%'")
        url = driver.current_url
        sleep(0.5)

        for i in range(1, pages + 1):
            if i != 1:
                page = '' if i == 0 else '&page=' + str(i)
                driver.get(url + page)
                driver.execute_script("document.body.style.zoom='30%'")
            sleep(0.7)

            blocks = driver.find_elements_by_xpath('//*[@class="entity-result__item"]')
            for block in blocks:
                scraped_name = safe_html_read(block.find_elements_by_xpath('.//*[@aria-hidden="true"]'))
                scraped_tag = safe_html_read(block.find_elements_by_xpath('.//*[@class="entity-result__primary-subtitle t-14 t-black"]'))
                scraped_link = block.find_elements_by_xpath('.//*[@class="app-aware-link"]')
                if scraped_name and scraped_tag and scraped_link:
                    scraped_names.append(scraped_name)
                    scraped_links.append(scraped_link[0].get_attribute('href'))
            sleep(0.7)

    for scraped_name, scraped_link in zip(scraped_names, scraped_links):
        if scraped_link and 'search' not in scraped_link:
            driver.get(scraped_link)
            sleep(0.5)

            raw_names.append(scraped_name)
            raw_links.append(scraped_link)

            option1 = driver.find_elements_by_xpath('//*[@class="pv-profile-section__card-item-v2 pv-profile-section pv-position-entity ember-view"]')
            option2 = driver.find_elements_by_xpath('//*[@class="pv-entity__summary-info pv-entity__summary-info--background-section mb2"]')
            option3 = driver.find_elements_by_xpath('//*[@class="pv-entity__summary-info pv-entity__summary-info--background-section "]')
            option4 = driver.find_elements_by_xpath('//*[@class="full-width ember-view"]')

            raw_role, raw_company = '-', '-'

            hail_mary = True

            if len(option1) > 0 and (len(option2) == 0 or option1[0].location['y'] < option2[0].location['y']):
                role_block = option1[0].find_elements_by_xpath('.//*[@class="t-14 t-black t-bold"]')
                if len(role_block) > 0:
                    raw_role = safe_html_read(role_block[0].find_elements_by_tag_name('span'), -1)
                    hail_mary = False
                company_block = option1[0].find_elements_by_xpath('.//*[@class="t-16 t-black t-bold"]')
                if len(company_block) > 0:
                    raw_company = safe_html_read(company_block[0].find_elements_by_tag_name('span'), -1)
            elif len(option2) > 0:
                raw_role = safe_html_read(option2[0].find_elements_by_xpath('.//*[@class="t-16 t-black t-bold"]'))
                hail_mary = False if raw_role != '-' else True
                raw_company = safe_html_read(option2[0].find_elements_by_xpath('.//*[@class="pv-entity__secondary-title t-14 t-black t-normal"]'))
            
            if hail_mary and len(option3) > 0:
                raw_role = safe_html_read(option3[0].find_elements_by_xpath('.//*[@class="t-16 t-black t-bold"]'))
                hail_mary = False
                raw_company = safe_html_read(option3[0].find_elements_by_xpath('.//*[@class="pv-entity__secondary-title t-14 t-black t-normal"]'))
            
            if hail_mary and len(option4) > 0:
                raw_role = safe_html_read(option4[0].find_elements_by_xpath('.//*[@class="t-16 t-black t-bold"]'))
                hail_mary = False
                raw_company = safe_html_read(option4[0].find_elements_by_xpath('.//*[@class="pv-entity__secondary-title t-14 t-black t-normal"]'))

            raw_roles.append(raw_role)
            raw_companies.append(raw_company)

driver.quit()

## PROCESS PROFILES ################################

def is_role(role):
    return 'software engineer' not in role.lower()\
        and 'swe' not in role.lower()\
        and 'software developer' not in role.lower()\
        and 'software development engineer' not in role.lower()\
        and 'sde' not in role.lower()\
        and 'analyst' not in role.lower()\
        and 'legal' not in role.lower()\
        and 'researcher' not in role.lower()\
        and 'designer' not in role.lower()\
        and 'intern' not in role.lower()\
        and 'creative' not in role.lower()\
        and 'leader' not in role.lower()\
        and 'real estate' not in role.lower()\
        and 'tax' not in role.lower()

firsts, lasts, roles, companies, links = [], [], [], [], []

def get_name(names):
    proper_names = []
    for name in names:
        if len(name) > 0\
            and name.replace("'", ' ').replace('-', ' ').isalpha()\
            and 'Mr' not in name\
            and 'Mrs' not in name\
            and 'Ms' not in name\
            and 'Dr' not in name\
            and 'MBA' not in name\
            and 'CPA' not in name\
            and 'CFA' not in name\
            and 'PMP' not in name\
            and 'SCPM' not in name\
            and 'PhD' not in name\
            and 'MD' not in name\
            and 'JD' not in name\
            and 'He/' not in name\
            and 'She/' not in name\
            and 'They/' not in name\
            and 'Ze/' not in name:
            proper_names.append(name)
    if len(proper_names) == 0:
        proper_names.append('-')
    return proper_names

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
        .replace('DS', 'Data Scientist')\
        .replace('CEO', 'Chief Executive Officer')\
        .replace('COO', 'Chief Operating Officer')\
        .replace('CFO', 'Chief Financial Officer')\
        .replace('CTO', 'Chief Technology Officer')\
        .replace('CDO', 'Chief Data Officer')\
        .replace('CIO', 'Chief Information Officer')\
        .replace('CMO', 'Chief Marketing Officer')\
        .replace(', ', ' of ')\
        .replace(' & ', ' and ')\
        .replace(' --- ', ' of ')\
        .replace('---', ' of ')\
        .replace(' -- ', ' of ')\
        .replace('--', ' of ')\
        .replace(' - ', ' of ')\

for raw_name, raw_role, raw_company, raw_link in zip(raw_names, raw_roles, raw_companies, raw_links):
    if is_role(raw_role):
        name_split = get_name(raw_name.replace('(', ' ').replace(')', ' ').replace(',', ' ').replace('.', '').split(' '))
        firsts.append(unidecode.unidecode(name_split[0].title()))
        lasts.append(unidecode.unidecode(name_split[-1].title()))
        roles.append(fix_role(raw_role))
        companies.append(raw_company.replace(' Full Time', '').replace('Full Time', '').replace(' Full-time', '').replace('Full-time', '').replace(' Full-Time', '').replace('Full-Time', ''))
        links.append(raw_link)

arr = np.asarray(list(zip(firsts, lasts, roles, companies, links, ['-'] * len(firsts))))

for a in arr:
    print(a[:-1])

results = pd.read_excel('results.xlsx', engine='openpyxl')
append = pd.DataFrame(arr, columns=['First', 'Last', 'Role', 'Company', 'Link', 'Email'])
results = results.append(append)

profile_set = set()
set_results = []
for i in range(results.shape[0]):
    hsh = str(list(results.iloc[i, :-1]))
    if hsh not in profile_set:
        profile_set.add(hsh)
        set_results.append(list(results.iloc[i]))

results = pd.DataFrame(data=set_results, columns=['First', 'Last', 'Role', 'Company', 'Link', 'Email'])
results.to_excel('results.xlsx', index=False, engine='openpyxl')

print("\n---\nProfiles written to 'results.xlsx' successfully!")