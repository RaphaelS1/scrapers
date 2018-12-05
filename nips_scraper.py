"""
Script that utilises Beautiful Soup to scrape all the names, abstracts and papers from a
    given year of NIPS publications. Names and abstracts are saved to a csv, the papers are downloaded as pdfs.
Before running, set the NIPS year of interest and the location to save the files.
"""
import requests
from bs4 import BeautifulSoup as bs
import urllib.request
import urllib
import pandas as pd


""""""
#   Set year of interest and location to save files here

year = 2017
file_loc = '/Desktop/NIPS/'
""""""

_URL = 'https://papers.nips.cc/book/advances-in-neural-information-processing-systems-30-' + str(year)

r = requests.get(_URL)
soup = bs(r.text,"lxml")
urls = []
names = []
abstracts = []
papers = []

for link in soup.find_all('a'):
     if "paper" in link.get('href'):
         papers.append('https://papers.nips.cc/' + link.get('href')+'.pdf')
         urls.append('https://papers.nips.cc/' + link.get('href'))
         names.append(link.get('href').replace("/paper/", ""))
 
names_urls = zip(names, papers, urls)

 
counter = 1
for name, paper, url in names_urls:
    print(name)
    print ("{:.3%}".format(counter/len(names)))
    rq = urllib.request.urlopen(paper)
    pdf = open(file_loc + name + '.pdf', 'wb')
    pdf.write(rq.read())
    pdf.close()
    r = requests.get(url)
    soup = bs(r.text,"lxml")
    abstracts.append(soup.find('p', {'class': 'abstract'}).text.strip())
    counter += 1

df = pd.DataFrame(data={names,abstracts})
df.to_csv(file_loc+'Names and Abstracts of NIPS ' + str(year) + ' papers')


