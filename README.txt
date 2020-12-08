This is the Voyager LinkedIn Bot. It automates LinkedIn profile searches.

To use it, you need to do a few things. Message Rahul if you have any trouble while doing this.

The first time you use it, you need to:
1. Get Python (see https://inst.eecs.berkeley.edu/~cs61a/sp20/lab/lab00/ for full setup details)
2. Run 'pip3 install -r requirements.txt' to get the requisite packages
3. Update 'parameters.py' with your LinkedIn username and password (these need to be in quotes!)

Every other time, all you need to do is:
1. Make sure neither 'results.xlsx' nor 'emails.xlsx' are open
2. Run 'bot.py' (type 'python3 bot.py' to run the script).
3. In the Chrome window it opens, use the LinkedIn search bar to narrow your query. Press enter after you're done. 
4. Your results should be written to 'results.xlsx'.
5. Run 'rocket.py' (type 'python3 rocket.py' to run the script). It will generate emails for all rows in 'results.xlsx' that are marked with a '-'.
6. Your results should be written to 'emails.xlsx'.
7. Enjoy!