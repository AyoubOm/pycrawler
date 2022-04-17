# Multithreaded crawler

The one thread version of this crawler crawls only one page per second.

Decoupling downloading pages (which is an I/O blocking operation) from crawling them minimises idleness.

Increasing the number of fetcher threads further minimises the chance of crawler to be in idle mode.

Maintaining a http session in a fetcher thread keeps tcp connections open and increases performance. 