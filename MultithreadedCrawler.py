from threading import Thread
import logging
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from time import sleep


logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)

urlsToCrawl = [] # written by Crawler, read by Fetcher
pages = [] # written by Fetcher, read by Crawler


def crawl():
	seeds = ['https://www.imdb.com/']
	for seed in seeds:
		urlsToCrawl.append(seed)

	visited = set([])

	while True:
		if pages:
			url, html = pages.pop(0)
			soup = BeautifulSoup(html, 'html.parser')
			for link in soup.find_all('a'):
				path = link.get('href')
				if path and path.startswith('/'):
					path = urljoin(url, path)
				if path not in visited:
					urlsToCrawl.append(path)
					visited.add(path)




def fetch():
	while True:
		if urlsToCrawl:
			url = urlsToCrawl.pop(0)
			logging.info(f'Fetching: {url}')
			pages.append((url, requests.get(url).text))


crawler = Thread(target=crawl)
fetcher = Thread(target=fetch)

crawler.start()
fetcher.start()

crawler.join()
fetcher.join()