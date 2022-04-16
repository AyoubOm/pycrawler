# Multithreaded crawler

The one thread version of this crawler crawls only one page per second.

Decoupling downloading pages (which is an I/O blocking operation) from crawling them minimises idleness.

Increasing the number of fetcher threads further minimises the chance of crawler to be in idle mode.