import parameters

from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

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

profiles = []

linkedin_url = 'http://www.linkedin.com/in/rahulhayaran'
driver.get(linkedin_url)
sleep(5)
sel = Selector(text=driver.page_source) 

name = sel.xpath('//*[starts-with(@class, "' + parameters.name + '")]/text()').extract_first()
if name:
    name = name.strip()
name_good = name is not None and name == 'Rahul Hayaran'

job_title = None
job_title = sel.xpath('//*[starts-with(@class, "' + parameters.job_title + '")]/text()').extract_first()
if job_title:
    job_title = job_title.strip().split(' at ')[0].split(' @ ')[0].split('...')[0]
job_title_good = job_title is not None

header = None
header = sel.xpath('//*[starts-with(@class, "' + parameters.header + '")]/text()').extract_first()
if header:
    header = header.strip().split(' at ')[0].split(' @ ')[0].split('...')[0]
header_good = header is not None

company = sel.xpath('//*[starts-with(@class, "' + parameters.company + '")]/text()').extract_first()
if company:
    company = company.strip()
company_good = company is not None

linkedin_url = driver.current_url

driver.quit()

if not name_good:
    print("Need to fix 'name' reference in 'parameters.py'")
if not job_title_good:
    print("Need to fix 'job_title' reference in 'parameters.py'")
if not header_good:
    print("Need to fix 'header' reference in 'parameters.py'")
if not company_good:
    print("Need to fix 'company' reference in 'parameters.py'")

if name_good and header_good and job_title_good and company_good:
    print("No reference errors found, 'bot.py' should run fine")