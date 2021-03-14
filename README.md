# Voyabot

This is the Voyager LinkedIn Bot (fondly referred to as Voyabot). It automates LinkedIn profile searches. To use it, you need to do a few things. Message Rahul if you have trouble with any of this.

## Setup

### The first time you use Voyabot, you must:

1. Get Python (see [here](https://inst.eecs.berkeley.edu/~cs61a/sp20/lab/lab00/) for full setup details).

2. Clone the repository.
```bash
git clone https://github.com/rahulhayaran/voyabot.git
```

3. `cd` into the repo and use the package manager [`pip`](https://pip.pypa.io/en/stable/) to install all necessary packages.
```bash
cd voyabot
pip install -r requirements.txt
```

4. Create a file called `parameters.py` and fill it up with the appropriate information. An example is provided below
```python
# LinkedInBot
LINKEDIN_USERNAME = # type your LinkedIn username here in single quotes
LINKEDIN_PASSWORD = # type your LinkedIn password here in single quotes
LINKEDIN_PAGES = 5
LINKEDIN_ROLES_TO_REMOVE = ['Intern', 'Contractor']  # these are roles you want removed from your searches
LINKEDIN_SCHOOLS_TO_FLAG = ['Berkeley', 'Haas']  # these are schools whose alumni you want tracked

# RocketBot
ROCKET_GENERAL_TEMPLATE_FREQ_THRESHOLD = 0.0  # this is the minimum frequency an email template must have on RocketReach to be included
ROCKET_FIRST_AT_TEMPLATE_FREQ_THRESHOLD = 0.0  # this is the minimum frequency the 'first@firm.com' email template must have on RocketReach to be included
```

5. Run `setup.py`. This will create a `queries.xlsx` Excel file from which you can begin entering searches.
```bash
python3 setup.py
```

## Usage

### Every other time you use Voyabot, you must:

1. Make sure you have the latest commit of this repo. To ensure that, run
```bash
git pull
```

### If you want to search LinkedIn:

2. Fill in `queries.xlsx` with the `Role`s you are interested in. Every row corresponds to a new `Firm`. Within a single row, enter a spaced-comma list of the `Role`s you want for that specific `Firm`. For instance, if I was trying to search for Machine Learning Engineers and Software Engineers at Firm A and Product Managers and Data Scientists at Firm B, I'd enter the following
```python
----------------------------------------------
|Machine Learning Engineer, Software Engineer|
----------------------------------------------
|Product Manager, Data Scientist             |
----------------------------------------------
```

3. Be sure to close `queries.xlsx` after you finish editing!

4. Run `am_linkedin.py`.
```bash
python3 am_linkedin.py
```

5. When prompted (you'll see a `Done using LinkedIn filters? Press enter to continue`), enter the newly opened LinkedIn window and enter your `Firm` filters (the bot will enter your `Role` filters as per `queries.xlsx`). Note you'll have to repeat this step for every row you have in `queries.xlsx`.

6. Sit back and relax! Your results will appear in `results.xlsx`!

### If you want to generate emails via RocketReach:

2. Make sure you have a 'full' `results.xlsx` that has some non-generated emails (they'll be annotated with `Haven't Tried Yet :/` in the `Found Email?` column). Check to see there are no typos in their `First`, `Last`, or `Firm` columns (you can validate by going to `Link`). This information will be used to generate emails, so it's important it's all correct!

3. Be sure to close `results.xlsx` after you finish checking!

4. Run `am_rocket.py`.
```bash
python3 am_rocket.py
```

5. Sit back and relax! Your results will appear in `emails.xlsx`. From there copy over to YAMM to send out your emails (reach out to Tiffany for details on how that works).
