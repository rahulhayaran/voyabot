# LinkedInBot
LINKEDIN_USERNAME = 'petez@berkeley.edu' # type your LinkedIn username here in single quotes
LINKEDIN_PASSWORD = 'QpWoEi102938!' # type your LinkedIn password here in single quotes
LINKEDIN_PAGES = 2
LINKEDIN_ROLES_TO_REMOVE = ['Intern', 'Contractor', 'Driver', 'Cook', 'Server', 'Associate', 'Creator']  # these are roles you want removed from your searches
LINKEDIN_SCHOOLS_TO_FLAG = ['Berkeley', 'Haas']  # these are schools whose alumni you want tracked
SLEEP_SPEED = 2 # the length of sleep is scaled by this factor, so 0.5 halves the wait time
SLEEP_NOISE = 1 # adds uniform noise from 0 to this cutoff to each sleep, set to 0 to disable

# RocketBot
ROCKET_GENERAL_TEMPLATE_FREQ_THRESHOLD = 20 # this is the minimum frequency (0-100) an email template must have on RocketReach to be included
ROCKET_FIRST_AT_TEMPLATE_FREQ_THRESHOLD = 80  # this is the minimum frequency (0-100) the 'first@firm.com' email template must have on RocketReach to be included
