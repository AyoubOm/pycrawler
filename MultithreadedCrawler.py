from threading import Thread, Event
import logging
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from time import sleep
import tldextract
from collections import defaultdict


logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

nbFetchers = 23
urlsToCrawl = [[] for _ in range(nbFetchers)] # written by Crawler, read by Fetcher
pages = [] # written by Fetcher, read by Crawler
counts = [0]*nbFetchers


def crawl(runEvent):
	seeds = [
			'https://www.imdb.com/',
			'https://www.wikipedia.org/',
			'https://www.apache.org/',
			'https://www.britannica.com/',
			'https://www.medium.com/',
			'https://www.quora.com/',
			'https://stackoverflow.com/',
			'https://spotify.com',
			'https://youtube.com',
			'https://cisco.com',
			'https://cloudflare.com',
			'https://godaddy.com',
			'https://openclassrooms.com']

	for seed in seeds:
		domain = tldextract.extract(seed).domain
		hashVal = hash(domain)
		urlsToCrawl[hashVal % nbFetchers].append(seed)

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
					if path not in visited and path.startswith('http'):
						domain = tldextract.extract(path).domain
						hashVal = hash(domain)
						urlsToCrawl[hashVal % nbFetchers].append(path)
						visited.add(path)




def fetch(fetcherId, runEvent):
	session = requests.Session()
	while runEvent.is_set():
		if urlsToCrawl[fetcherId]:
			url = urlsToCrawl[fetcherId].pop(0)
			logging.info(f'Fetcher-{fetcherId+1}\tFetching: {url}')
			pages.append((url, session.get(url).text))
			counts[fetcherId] += 1

	logging.info(f'Fetcher-{fetcherId+1}\tNb urls={counts[fetcherId]}')





def main(benchmark=False):
	runEvent = Event()
	runEvent.set()

	crawler = Thread(target=crawl, args=(runEvent, ))
	fetchers = [Thread(target=fetch, args=(i, runEvent)) for i in range(nbFetchers)]

	crawler.start()
	for fetcher in fetchers:
		fetcher.start()

	try:
		if not benchmark:
			while True:
				sleep(2)
		else:
			for _ in range(150): # => 5 minutes benchmark
				sleep(2)

		runEvent.clear()

	except KeyboardInterrupt:
		runEvent.clear()

	crawler.join()
	for fetcher in fetchers:
		fetcher.join()

	print(f'Number of fetched pages in 5mins = {sum(counts)}')


if __name__ == '__main__':
	main(True)


