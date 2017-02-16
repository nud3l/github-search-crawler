#!/usr/bin/python
from crawler import Crawler

if __name__ == '__main__':
    # Solidity crawler
    my_crawler = Crawler("ethereum")
    my_crawler.crawl()