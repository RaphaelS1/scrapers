"""
Script that utilises Beautiful Soup to scrape details of tweet interactions from UK MPs in a given date range.
 The data is saved both as a full data-set containing every single tweets interactions (not the tweet itself) and as
    an aggregated dataset, grouped for each MP. Interactions are defined as number of likes + number of retweets.
"""

import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import time

""""""

# Start_Date/End_Date - ("dd-mm-yyyy") to start/end scrape from
# file_loc - Location to save csvs
# likes - If True (default) saves number of likes for each tweet
# retweets - If True (default) saves number of retweets for each tweet
# interactions - If True (default) saves number of interactions (likes + retweets) for each tweet

def scrape_tweets(start_date, end_date, file_loc, likes=False, retweets=False, interactions=True):
    _URL = 'https://www.mpsontwitter.co.uk/archive/search?query=&literal=0&date_from=' + start_date + '&date_to=' + end_date + '&party=all&order=retweets'

    r = requests.get(_URL)
    soup = bs(r.text, "lxml")

    searchinfo = soup.findAll("div", attrs="search_results_info")
    numtweets = searchinfo[0].findAll("p")[0].contents[0]
    totaltweets = int(numtweets[6:len(numtweets) - len(" tweets matching the criteria ")].replace(",", ""))

    mps = []
    parties = []
    constituency = []
    lst_likes = []
    lst_retweets = []
    lst_interactions = []

    for i in range(0, totaltweets, 50):
        time.sleep(.5)
        loop_start = time.time()

        _URL = 'https://www.mpsontwitter.co.uk/archive/search?query=&literal=0&date_from=' + start_date + '&date_to=' + \
               end_date + '&party=all&order=retweets&offset=' + str(i)

        r = requests.get(_URL)
        soup = bs(r.text, "lxml")

        tweetdetails = soup.findAll("p", attrs="tweet_details text-muted")
        mpdetails = soup.findAll("p", attrs="tweet_mp_details")

        for x in range(0, len(mpdetails)):
            mp = mpdetails[x].findAll("span", attrs="bold")
            party = mpdetails[x].findAll("span", attrs="badge")
            if len(mpdetails[x].contents) < 6:
                continue
            else:
                con_end = mpdetails[x].contents[6][10:1000].find("\n")
            if len(mp) == 0 or len(party) == 0 or con_end == -1:
                continue
            else:
                mps.append(mp[0].contents[0])
                parties.append(party[0].contents[0])
                constituency.append(mpdetails[x].contents[6][10:(10 + con_end)])
                end = tweetdetails[x].contents[2].find("|")
                num_retweets = int(tweetdetails[x].contents[2][1:end - 1].replace(",", ""))
                end = tweetdetails[x].contents[4].find("|")
                num_likes = int(tweetdetails[x].contents[4][1:end - 1].replace(",", ""))
                if likes:
                    lst_likes.append(num_likes)
                if retweets:
                    lst_retweets.append(num_retweets)
                if interactions:
                    lst_interactions.append(num_retweets + num_likes)

        loop_end = time.time()
        time_dif = loop_end - loop_start
        remaining = (time_dif * (totaltweets - int(i)) / 50) / 60
        print("There is roughly {0:.2f} minutes remaining".format(remaining))
        print("Percentage of tweets scraped = {0:04.2f}%".format(float((i / totaltweets))*100))

    candidate_df = pd.DataFrame(
        {"MP": mps,
         "Party": parties,
         "Constituency": constituency
         }
    )

    if interactions:
        candidate_df["Interactions"] = lst_interactions
    if likes:
        candidate_df["Likes"] = lst_likes
    if retweets:
        candidate_df["Retweets"] = lst_retweets

    agg_df = candidate_df.groupby(['MP', 'Party', 'Constituency']).agg(['sum', 'min', 'max', 'mean', 'count']).round(2)

    candidate_df.to_csv(file_loc + 'Candidates.csv')
    agg_df.to_csv(file_loc + 'Candidates_Agg.csv')
