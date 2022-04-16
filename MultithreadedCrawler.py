from threading import Thread, Event
import logging
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from time import sleep
import tldextract
from collections import defaultdict


logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)

nbFetchers = 5
urlsToCrawl = [[] for _ in range(nbFetchers)] # written by Crawler, read by Fetcher
pages = [] # written by Fetcher, read by Crawler


def crawl(runEvent):
	seeds = ['https://www.imdb.com/',
	'https://www.wikipedia.org/',
	'https://www.apache.org/',
	'https://www.britannica.com/',
	'https://www.medium.com/',
	'https://www.quora.com/',
	'https://stackoverflow.com/']

	for seed in seeds:
		domain = tldextract.extract(seed).domain
		hashVal = hash(domain)
		urlsToCrawl[hashVal % nbFetchers].append(seed)

	print(urlsToCrawl)

	visited = set([])

	while runEvent.is_set():
		if pages:
			url, html = pages.pop(0)
			soup = BeautifulSoup(html, 'html.parser')
			for link in soup.find_all('a'):
				path = link.get('href')
				if path:
					if path.startswith('/'):
						path = urljoin(url, path)
					if path not in visited and path.startswith('http'): # this will make crawler ignore some links I guess
						domain = tldextract.extract(path).domain
						hashVal = hash(domain)
						urlsToCrawl[hashVal % nbFetchers].append(path)
						visited.add(path)




def fetch(fetcherId, runEvent):
	while runEvent.is_set():
		if urlsToCrawl[fetcherId]:
			url = urlsToCrawl[fetcherId].pop(0)
			logging.info(f'Fetching: {url}')
			pages.append((url, requests.get(url).text))



def main():
	runEvent = Event()
	runEvent.set()

	crawler = Thread(target=crawl, args=(runEvent, ))
	fetchers = [Thread(target=fetch, args=(i, runEvent)) for i in range(nbFetchers)]

	crawler.start()
	for fetcher in fetchers:
		fetcher.start()

	try:
		while True:
			sleep(2)
	except KeyboardInterrupt:
		runEvent.clear()
		crawler.join()
		for fetcher in fetchers:
			fetcher.join()


if __name__ == '__main__':
	main()


