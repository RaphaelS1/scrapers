"""
Script that utilises Beautiful Soup to scrape details of tweet interactions from UK MPs in a given date range.
 The data is saved both as a full data-set containing every single tweets interactions (not the tweet itself) and as
    an aggregated dataset, grouped for each MP. Interactions are defined as number of likes + number of retweets.

Before running, set the start date and end date of interest and file location to save csvs.
"""

import requests
from bs4 import BeautifulSoup as bs
import urllib.request
import urllib
import pandas as pd
import numpy as np
import re
import time

""""""
#   Set date range of interest and location to save files here

start_date = "08-06-2016"
end_date = "08-06-2017"
file_loc = "/Desktop/mpsontwitter/"
""""""

_URL = 'https://www.mpsontwitter.co.uk/archive/search?query=&literal=0&date_from='+start_date+'&date_to='+end_date+'&party=all&order=retweets'

r = requests.get(_URL)
soup = bs(r.text, "lxml")

searchinfo = soup.findAll("div", attrs="search_results_info")
numtweets = searchinfo[0].findAll("p")[0].contents[0]
totaltweets = int(numtweets[6:len(numtweets)-len(" tweets matching the criteria ")].replace(",", ""))

mps = []
parties = []
constituency = []
interactions = []


for i in range(0,totaltweets,50):
    loop_start = time.time()

    _URL = 'https://www.mpsontwitter.co.uk/archive/search?query=&literal=0&date_from=' + start_date + '&date_to=' + end_date + '&party=all&order=retweets&offset=' + str(i)

    r = requests.get(_URL)
    soup = bs(r.text, "lxml")

    tweetdetails = soup.findAll("p", attrs="tweet_details text-muted")
    mpdetails = soup.findAll("p", attrs="tweet_mp_details")

    for x in range(0,len(mpdetails)):
        mp = mpdetails[x].findAll("span", attrs="bold")
        party = mpdetails[x].findAll("span",attrs="badge")
        if len(mpdetails[x].contents) < 6:
            break
        else:
            con_end = mpdetails[x].contents[6][10:1000].find("\n")
        if len(mp) == 0 or len(party) == 0 or con_end == -1:
            break
        else:
            mps.append(mp[0].contents[0])
            parties.append(party[0].contents[0])
            constituency.append(mpdetails[x].contents[6][10:(10 + con_end)])
            end = tweetdetails[x].contents[2].find("|")
            retweets = int(tweetdetails[x].contents[2][1:end - 1].replace(",", ""))
            end = tweetdetails[x].contents[4].find("|")
            likes = int(tweetdetails[x].contents[4][1:end - 1].replace(",", ""))
            interactions.append(retweets + likes)

    loop_end = time.time()
    time_dif = loop_end - loop_start
    remaining = (time_dif * (324500-i)/50) / 60
    print("There is roughly {0} minutes remaining".format(remaining))
    print("Tweets scraped = " + str(i))

candidate_df = pd.DataFrame(
        {"MP": mps,
         "Party" : parties,
         "Constituency" : constituency,
         "Interactions" : interactions})

agg_df = candidate_df.groupby(['MP', 'Party', 'Constituency']).agg(['sum', 'min', 'max', 'mean', 'count']).round(2)

candidate_df.to_csv(file_loc+'Candidates')
agg_df.to_csv(file_loc+'Candidates_Agg')
