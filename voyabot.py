from parameters import *
from sheet import *

import pandas as pd
import unidecode
from time import sleep
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from numpy import random

class VoyaBot:
    def __init__():
        pass

    def load_driver(self) -> None:
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")

        self.driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)

    def load_site(self) -> None:
        pass

    def scrape_data(self) -> pd.DataFrame:
        pass

    def close_driver(self):
        self.driver.quit()


def safe_html_read(blocks: list):
    read = []
    for block in blocks:
        read.append(block.text)
    return read if len(read) > 0 else ['-']


def bot_sleep(time):
    sleep(time * SLEEP_SPEED + random.uniform(0, SLEEP_NOISE))
class LinkedInBot(VoyaBot):
    
    # Core API

    def __init__(self, inputs: Sheet):
        self.inputs = inputs

        self.load_driver()
        self.load_site()

    def load_site(self):
        self.driver.get('https://www.linkedin.com/login?trk=homepage-basic_conversion-modal-signin')
        username = self.driver.find_element_by_xpath('//*[@id="username" and @name="session_key"]')
        username.send_keys(LINKEDIN_USERNAME)
        sleep(0.5)

        password = self.driver.find_element_by_xpath('//*[@id="password" and @name="session_password"]')
        password.send_keys(LINKEDIN_PASSWORD)
        sleep(0.5)

        sign_in_button = self.driver.find_element_by_xpath('//*[@type="submit"]')
        sign_in_button.click()
        sleep(0.5)

    def scrape_data(self) -> pd.DataFrame:

        queries = self.inputs.get_queries()
        arr = []

        for nfirm, firm, roles in queries:
            print("Scraping {}, firm {} of {}".format(firm, nfirm + 1, len(list(queries))))
            bot_sleep(5)

            query_url = "https://www.linkedin.com/search/results/people/?currentCompany=%5B\"" + str(firm) + "\"%5D"
            for nrole, search in enumerate(roles.split(', ')):
                print("Scraping {}, role {} of {}".format(search, nrole + 1, len(roles.split(", "))))
                bot_sleep(1)
                self.driver.get(query_url)
                pages = LINKEDIN_PAGES
                if " - " in search:
                    search, pages = search.split(" - ")

                links = self.do_search(self.process_search(search), int(pages))

                for link in links:
                    try:
                        arr.append(self.scrape_profile(link))
                    except NoSuchElementException as err:
                        print("Profile not fully loaded:", link)
                    except KeyboardInterrupt:
                        if input("Input any text to save profiles. To exit, hit ENTER."):
                            return pd.DataFrame(arr, columns=['First', 'Last', 'Role', 'Firm', 'Schools', 'Skills', 'Link'])
                        quit()
                    except Exception as err:
                        print("Encountered error", err)
        
                        
        return pd.DataFrame(arr, columns=['First', 'Last', 'Role', 'Firm', 'Schools', 'Skills', 'Link'])

    # Scrapers

    def scrape_profile(self, profile_url: str) -> tuple:
        
        self.driver.get(profile_url)
        self.driver.execute_script("document.body.style.zoom='30%'")
        bot_sleep(1)

        if 'headless' in profile_url or 'search' in profile_url:
            raise Exception("Profile link error:", profile_url)

        first, last = self.scrape_name()
        role, firm = self.scrape_xp()
        schools = self.scrape_schools()
        skills = self.scrape_skills()

        return (first, last, role, firm, ' | '.join(schools), ' | '.join(skills), profile_url)

    def scrape_name(self) -> tuple:
        def split_name(phrases):
            valid_phrases = []
            for phrase in phrases:
                if len(phrase) > 0\
                    and phrase.replace("'", ' ').replace('-', ' ').isalpha()\
                    and 'Mr' not in phrase\
                    and 'Mrs' not in phrase\
                    and 'Ms' not in phrase\
                    and 'Dr' not in phrase\
                    and 'MBA' not in phrase\
                    and 'CPA' not in phrase\
                    and 'CFA' not in phrase\
                    and 'PMP' not in phrase\
                    and 'SCPM' not in phrase\
                    and 'PhD' not in phrase\
                    and 'SPHR' not in phrase\
                    and 'PHR' not in phrase\
                    and 'CPSP-1' not in phrase\
                    and 'MD' not in phrase\
                    and 'JD' not in phrase\
                    and 'He/' not in phrase\
                    and 'She/' not in phrase\
                    and 'They/' not in phrase\
                    and 'Ze/' not in phrase:
                    valid_phrases.append(phrase)
            return valid_phrases if len(valid_phrases) > 0 else ['-']

        name = safe_html_read(self.driver.find_elements_by_xpath('//*[@class="text-heading-xlarge inline t-24 v-align-middle break-words"]'))[0]
        valid_phrases = split_name(name.replace('(', ' ').replace(')', ' ').replace(',', ' ').replace('.', '').split(' '))
        first = unidecode.unidecode(valid_phrases[0].title())
        last = unidecode.unidecode(valid_phrases[-1].title())

        return first, last

    def scrape_xp(self) -> tuple:    
        block = self.driver.find_element_by_xpath('//*[@class="pv-profile-section__card-item-v2 pv-profile-section pv-position-entity ember-view"]')
        role = safe_html_read(block.find_elements_by_xpath('//*[@class="t-16 t-black t-bold"]'))[0]
        firm = safe_html_read(block.find_elements_by_xpath('//*[@class="pv-entity__secondary-title t-14 t-black t-normal"]'))[0]

        if 'Company Name' in role:
            role = safe_html_read(block.find_elements_by_xpath('//*[@class="t-14 t-black t-bold"]'))[0]
            firm = safe_html_read(block.find_elements_by_xpath('//*[@class="t-16 t-black t-bold"]'))[0]
        
        return role.replace('Title', '').replace('Sr. ', 'Senior ')\
                                        .replace('Sr ', 'Senior ')\
                                        .replace('Of ', 'of ')\
                                        .replace('& ', 'and ')\
                                        .replace('Director,', 'Director of')\
                                        .replace('officer', 'Officer')\
                                        .replace('Manager,', 'Manager of')\
                                        .replace('President,', 'President of')\
                                        .replace('VP,', 'VP of')\
                                        .replace('Head,', 'Head of')\
                                        .replace('Leader,', 'Leader of')\
                                        .replace('Lead,', 'Leader of')\
                                        .replace(" - ", " of ")\
                                        .strip(), firm.replace('Company Name', '')\
                                              .replace('Full-time', '')\
                                              .replace('Part-time', '')\
                                              .replace('Self-employed', '')\
                                              .replace('Freelance', '')\
                                              .replace('Contract', '')\
                                              .replace('Internship', '')\
                                              .replace('Apprenticeship', '')\
                                              .replace('Seasonal', '')\
                                              .strip()    

    def scrape_schools(self) -> list:
        return safe_html_read(self.driver.find_elements_by_xpath('//*[@class="pv-entity__school-name t-16 t-black t-bold"]'))

    def scrape_skills(self) -> list:
        return safe_html_read(self.driver.find_elements_by_xpath('//*[@class="pv-skill-category-entity__name-text t-16 t-black t-bold"]'))

    # Utilities

    def process_search(self, role: str) -> str:
        bot_sleep(0.25)
        search = self.driver.find_element_by_xpath('//*[@class="search-global-typeahead__input always-show-placeholder"]')
    
        search.send_keys(Keys.COMMAND + Keys.CONTROL + "a")
        bot_sleep(0.25)

        search.send_keys(Keys.DELETE)
        bot_sleep(0.25)

        search.send_keys(role + '\n')
        bot_sleep(1)

        self.driver.execute_script("document.body.style.zoom='30%'")
        return self.driver.current_url

    def do_search(self, reset_url: str, pages: int) -> list:
        scraped_links = []
        for i in range(1, LINKEDIN_PAGES + 1):
            if i != 1:
                page = '' if i == 0 else '&page=' + str(i)
                self.driver.get(reset_url + page)
                self.driver.execute_script("document.body.style.zoom='30%'")
            bot_sleep(0.7)

            blocks = self.driver.find_elements_by_class_name('entity-result__item')

            if not blocks:
                break

            for block in blocks:
                scraped_link = block.find_elements_by_class_name('app-aware-link')
                scraped_links.append(scraped_link[0].get_attribute('href'))
            
            bot_sleep(0.7)
        return scraped_links


class RocketBot(VoyaBot):
    
    # Core API

    def __init__(self, inputs: Sheet):
        self.inputs = inputs
        self.inputs_df = self.inputs.read()

        self.load_driver()

    def scrape_data(self) -> pd.DataFrame:
        emails = []
        
        def clean_firm(firm: str) -> str:
            return firm.lower().replace('.com', '')\
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


        firms_df = dict()

        for i, row in self.inputs_df.iterrows():
            if row['Found Email?'] != 'Yup :)':
                firm = clean_firm(row['Firm'])

                # find firm if new
                if firm not in firms_df:
                    df = self.do_search(firm)
                    if df is not None and df.iloc[0][0] != '-':
                        firms_df[firm] = self.clean_df(df)
                    else:
                        firms_df[firm] = None
                
                # else check valid
                elif firms_df[firm] is not None:
                    df = firms_df[firm]
                    for template in df['template']:
                        email, address = template.split('@')
                        email = email.replace('jane', '1').replace('doe', '2').replace('j', '3').replace('d', '4')

                        def clean_first(name):
                            return name.lower().replace('-', ' ').split(' ')[0]
                        def clean_last(name):
                            return name.lower().replace('-', ' ').split(' ')[-1]

                        email = email.replace('1', clean_first(row['First']))\
                                    .replace('2', clean_last(row['Last']))\
                                    .replace('3', clean_first(row['First'])[0])\
                                    .replace('4', clean_last(row['Last'])[0])
                        
                        email = [email + '@' + address]
                        emails.append(list(row)[:-1] + email)
                    self.inputs_df.at[i, 'Found Email?'] = 'Yup :)'
                else:
                    self.inputs_df.at[i, 'Found Email?'] = 'Tried and Failed :('

        self.inputs.clear()
        self.inputs.write(self.inputs_df)

        return pd.DataFrame(emails, columns=self.inputs_df.columns)

    # Utilities

    def do_search(self, firm: str) -> pd.DataFrame:
        self.driver.get('https://duckduckgo.com/')
        sleep(1)

        search_query = self.driver.find_element_by_xpath("//*[@class='js-search-input search__input--adv']")
        search_query.send_keys('site:rocketreach.co' + ' + "' + firm + '" + ' + 'email format')
        sleep(0.5)

        search_query.send_keys(Keys.RETURN)
        sleep(1)

        urls = [url.get_attribute('href') for url in self.driver.find_elements_by_xpath("//*[@class='result__url js-result-extras-url']")\
            if ('rocketreach.co' in url.text and 'email-format' in url.text)]

        for url in urls:
            url = urls[0] if 'https://' in urls[0] else 'https://' + urls[0]
            self.driver.get(url)
            bot_sleep(10)
            break

        table = self.driver.find_elements_by_xpath("//*[@class='table']")
        if len(table) > 0: 
            table, data = table[0], []
            rows, cols = len(table.find_elements_by_xpath("//tr")) - 1, len(table.find_elements_by_xpath("//tr[2]/td"))
            for i in range(1, rows + 1):
                row = []
                for j in range(1, cols + 1):
                    row.append(safe_html_read(table.find_elements_by_xpath("//tr["+str(i)+"]/td["+str(j)+"]"))[0])
                data.append(row)
            
            if len(data[0]) == 0:
                data = [[safe_html_read(table.find_elements_by_xpath("//tr/td["+str(j)+"]"))[0] for j in range(1, 4)]]

            return pd.DataFrame(data=data, columns=['_', 'template', 'frequency'])

    def clean_df(self, df: pd.DataFrame) -> pd.DataFrame:

        df['frequency'] = df['frequency'].apply(lambda x: float(x.replace('%', '').replace('-', '0') if type(x) == str else x))
        df = df[df['frequency'] >= ROCKET_GENERAL_TEMPLATE_FREQ_THRESHOLD]
        first = list(df[df['_'] == 'first']['frequency'])
        if first and len(first) > 0 and first[0] < ROCKET_FIRST_AT_TEMPLATE_FREQ_THRESHOLD:
            df = df[df['_'] != 'first']
        
        return df