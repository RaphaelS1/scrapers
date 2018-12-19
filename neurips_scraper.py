"""
Script that utilises Beautiful Soup to scrape all the names, abstracts and papers from a
    given year of NeurIPS publications. Names and abstracts are saved to a csv, the papers are downloaded as pdfs.
"""
import requests
from bs4 import BeautifulSoup as bs
import urllib.request
import urllib
import pandas as pd


# year - Desired year of NeurIPS papers
# file_loc - location to save files to
# name_abstracts - If True (default) will save all papers with IDs and abstracts to a CSV
# papers - If True (default) will download papers as pdfs
# cites - If True (default) will write all the citations of the papers into one txt

def scrape_neurips(year, file_loc, name_abstracts=True, dl_papers=True, cites=True):
    _URL = 'https://papers.nips.cc/book/advances-in-neural-information-processing-systems-30-' + str(year)

    r = requests.get(_URL)
    soup = bs(r.text, "lxml")

    urls = []
    bib_urls = []
    bibs = []
    names = []
    abstracts = []
    papers = []

    for link in soup.find_all('a'):
        if "paper" in link.get('href'):
            urls.append('https://papers.nips.cc/' + link.get('href'))
            papers.append('https://papers.nips.cc/' + link.get('href') + '.pdf')
            bib_urls.append('https://papers.nips.cc/' + link.get('href') + '/bibtex')
            names.append(link.get('href').replace("/paper/", ""))

    names_urls = zip(names, papers, urls, bib_urls)

    counter = 1
    for name, paper, url, bib_url in names_urls:
        print(name)
        print("{:.3%}".format(counter / len(names))+" of papers scraped")
        if dl_papers:
            rq = urllib.request.urlopen(paper)
            pdf = open(file_loc + name + '.pdf', 'wb')
            pdf.write(rq.read())
            pdf.close()
        if cites:
            rq = urllib.request.urlopen(bib_url)
            bibs.append(rq.read())
        if name_abstracts:
            r = requests.get(url)
            soup = bs(r.text, "lxml")
            abstracts.append(soup.find('p', {'class': 'abstract'}).text.strip())
        counter += 1

    if name_abstracts:
        df = pd.DataFrame(data={names, abstracts})
        df.to_csv(file_loc + 'Names and Abstracts of NIPS ' + str(year) + ' papers')

    if cites:
        with open(file_loc + 'Bibs.txt', 'w') as f:
            for bib in bibs:
                bibstr = str(bib).replace("\\n", "")
                bibstr = bibstr.replace("b'", "")
                bibstr = bibstr.replace("'", "")
                f.write(bibstr + "\n")



