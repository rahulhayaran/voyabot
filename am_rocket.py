from sheet import Sheet
from voyabot import RocketBot

inputs = Sheet('results.xlsx')
outputs = Sheet('emails.xlsx')

bot = RocketBot(inputs)
df = bot.scrape_data()

outputs.write(df)
bot.close_driver()