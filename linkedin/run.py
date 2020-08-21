# This is an example code
#########################
#########################

import linked

# Substitute relevant data
##########################

# credentials for linked-in login
email = "SaadEjaz474@gmail.com"
password = "Saadiejaz"

# driver location
chromeDriver = "../chromedriver"

# keywords for search
keywords = "tanveer ahmed"


# add required cookie names
requiredCookies = ["li_at"]

driver = linked.setDriver(executable_path = chromeDriver)
linked.loginLinkedIn(driver, loginCredentials = {'email': email, 'password':password})

# use this function to get cookies for a list of cookie names
print(linked.getLinkedInCookies(driver, *requiredCookies))

# use this to search using keywords. Choose an entity type of either 'people' or 'companies'. Depth decides the number of pages to crawl
print(linked.search(driver, keywords, entityType = "people", depth = 2))
