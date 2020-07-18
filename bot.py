import parameters

from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

from parsel import Selector

import numpy as np
import pandas as pd

driver = webdriver.Chrome(parameters.chromedriver)
driver.get('https://www.linkedin.com/login?trk=homepage-basic_conversion-modal-signin')

username = driver.find_element_by_xpath('//*[@id="username" and @name="session_key"]')
username.send_keys(parameters.linkedin_username)
sleep(0.5)

password = driver.find_element_by_xpath('//*[@id="password" and @name="session_password"]')
password.send_keys(parameters.linkedin_password)
sleep(0.5)

sign_in_button = driver.find_element_by_xpath('//*[@type="submit"]')
sign_in_button.click()
sleep(0.5)

queries = pd.read_excel('queries.xlsx')

linkedin_urls = []

for i in range(queries.shape[0]):
    query = queries.iloc[i,:]

    driver.get('https://www.bing.com')
    sleep(3)

    search_query = driver.find_element_by_name('q')
    search_query.send_keys('site:linkedin.com/in/ AND "' + str(query[0]) + '" AND "' + str(query[1]) + '"')
    sleep(0.5)

    search_query.send_keys(Keys.RETURN)
    sleep(3)

    urls = driver.find_elements_by_class_name('b_attribution')
    linkedin_urls.extend([url.text.replace(' › ', '/') for url in urls if ('linkedin.com/in/' in url.text)])
    sleep(0.5)

    for i in range(int(query[2]) - 1):    
        try:
            dumb_ad = driver.find_element_by_class_name('bnp_hfly_cta2')
            dumb_ad.click()
        except NoSuchElementException:
            pass

        next_button = driver.find_element_by_xpath('//*[@title="Next page"]')
        next_button.click()
        sleep(0.5)

        urls = driver.find_elements_by_class_name('b_attribution')
        linkedin_urls.extend([url.text.replace(' › ', '/') for url in urls if ('linkedin.com/in/' in url.text)])
        sleep(0.5)

profiles = []

for linkedin_url in linkedin_urls:
    if linkedin_url == 'https://www.linkedin.com/in/unavailable/':
        continue
    driver.get(linkedin_url)
    sleep(5)
    sel = Selector(text=driver.page_source)

    if driver.current_url == 'https://www.linkedin.com/in/unavailable/':
        continue

    name = sel.xpath('//*[starts-with(@class, "' + parameters.name + '")]/text()').extract_first()
    if name is not None:
        name = name.strip()

    first_name = name.split(' ')[0].split(',')[0]
    last_name = (name.split(' ')[1] if '(' not in name.split(' ')[1] else name.split(' ')[2]).split(',')[0]

    job_title = None
    guesses = ['//*[starts-with(@class, "' + parameters.job_title + '")]/text()', '//*[starts-with(@class, "' + parameters.header + '")]/text()']
    for guess in guesses:
        job_title = sel.xpath(guess).extract_first()
        if job_title and sum(map(lambda x: len(x), job_title.split(' '))) > 1:
            job_title = job_title.strip().split(' at')[0].split(' @')[0].split('...')[0].split('@')[0].split('|')[0].split(' |')[0]
            break
        else:
            job_title = None
    if job_title is not None:
        job_title = ' ' + job_title + ' '
        job_title = job_title.replace(' VP ', ' Vice President ').replace(' EVP ', ' External Vice President ').replace(' IVP ', ' Internal Vice President ').replace(' SVP ', ' Senior Vice President ').replace(' AVP ', ' Associate Vice President ')
        job_title = job_title[1:-1]

    company = sel.xpath('//*[starts-with(@class, "' + parameters.company + '")]/text()').extract_first()
    if company is not None:
        company = company.strip()
        if company[:(min(3, len(company)))] not in query[0]:
            continue
    else:
        company = ''

    linkedin_url = driver.current_url.split('?originalSubdomain')[0]

    profiles.append([first_name, last_name, job_title, company, linkedin_url])

    results = pd.read_excel('results.xlsx')
    append = pd.DataFrame(profiles, columns=['First', 'Last', 'Job Title', 'Company', 'LinkedIn URL'])
    results = results.append(append)

    profile_set = set()
    set_results = []
    for i in range(results.shape[0]):
        result = list(results.iloc[i])
        hsh = str(result)
        if hsh not in profile_set:
            profile_set.add(hsh)
            set_results.append(result)

    results = pd.DataFrame(data=set_results, columns=['First', 'Last', 'Job Title', 'Company', 'LinkedIn URL'])
    results.to_excel('results.xlsx', index=False)

    print(str([first_name, last_name, job_title, company, linkedin_url]))

driver.quit()
