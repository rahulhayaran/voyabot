This is the Voyager LinkedIn Bot. It automates LinkedIn profile searches.

To use it, you need to do a few things. Message Rahul if you have any trouble while doing this.

The first time you use it, you need to:
1. Get Python (see https://inst.eecs.berkeley.edu/~cs61a/sp20/lab/lab00/ for full setup details)
2. Run 'pip3 install -r requirements.txt' to get the requisite packages
3. Download the appropriate Chrome Driver (see https://sites.google.com/a/chromium.org/chromedriver/downloads) and place it in the 'voyabot' folder 
4. Update 'parameters.py' with your LinkedIn username and password (these need to be in quotes!)

Every other time, all you need to do is:
1. Run 'test.py' to verify everything is functional (type 'python3 test.py' to run the script). If any errors appear, message Rahul and/or fix them
2. Update 'queries.xlsx' with your Bing searches
3. Make sure neither 'queries.xlsx' nor 'results.xlsx' are open!
4. Run 'bot.py' (type 'python3 bot.py' to run the script). Your results should be written to 'results.xlsx'
5. Enjoy!