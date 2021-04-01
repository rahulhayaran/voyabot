import pandas as pd

from sheet import Sheet, Queries
from voyabot import LinkedInBot
from parameters import LINKEDIN_ROLES_TO_REMOVE, LINKEDIN_SCHOOLS_TO_FLAG

inputs = Queries('queries.xlsx')

outputs = Sheet('results.xlsx')

bot = LinkedInBot(inputs)
df = bot.scrape_data()

def f(x):
    for role in LINKEDIN_ROLES_TO_REMOVE:
        if role.lower() in x.lower():
            return False
    return True

df = df[df['Role'].apply(f)]

if len(LINKEDIN_SCHOOLS_TO_FLAG) > 0:
    for school in LINKEDIN_SCHOOLS_TO_FLAG:
        df[school + ' Alumni?'] = df['Schools'].apply(lambda x: school.lower() in x.lower())
    df.drop(columns=['Schools'], inplace=True)

df['Found Email?'] = "Haven't Tried :/"
outputs.write(df)

bot.close_driver()