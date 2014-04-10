import heapq
import HTMLParser
import itertools
import os
import sys
import time


import feedparser


class Feed(object):
    blacklist_words = set(['exp:', 'joystiq', 'review', 'ign', 'podcast', 'episode'])

    def __init__(self, url):
        self.__url = url
        self.title = feedparser.parse(self.__url).feed.title

    def get_latest(self, limit):
        entries = filter(lambda e: not any(word in e.title for word in Feed.blacklist_words),
                feedparser.parse(self.__url).entries)
        return heapq.nlargest(limit, entries,
                key=lambda entry: entry.published_parsed)


class FeedManager(object):
    def __init__(self, url_list):
        feeds = (Feed(url) for url in url_list)
        self.__h = HTMLParser.HTMLParser()
        self.named_feeds = {feed.title : feed for feed in feeds}

    def get_latest(self, limit):
        entries_by_source = ((source, feed.get_latest(limit))
                for source, feed in self.named_feeds.iteritems())

        all_sourced_entries = itertools.chain.from_iterable(
                ((source, entry) for entry in entries)
                        for source, entries in entries_by_source)

        return heapq.nlargest(limit, all_sourced_entries,
                key=lambda t: t[1].published_parsed)

    def __format(self, source, title, show_source):
        if show_source:
            return  ': '.join([''.join(['[', source, ']']), ''.join(['"', title, '"'])])
        else:
            return self.__h.unescape(title)

    def display_latest(self, limit):
        return '   --   '.join(self.__format(source, entry.title, False)
                for (source, entry) in self.get_latest(limit))


class FileManager(object):
    def __init__(self, filename, feed_manager, limit=25, delay=120):
        self.filename = filename
        self.feed_manager = feed_manager
        self.limit = limit
        self.delay = delay

    def work(self):
        while True:
            latest_news = self.feed_manager.display_latest(self.limit) + os.linesep

            with open(self.filename, 'w') as f:
                f.write(latest_news.encode('utf8'))

            time.sleep(self.delay)


if __name__ == "__main__":

    rss_list = [
        #'http://www.gamespot.com/feeds/news/',
        #'http://www.escapistmagazine.com/rss/news/0.xml',
        'http://www.gamesradar.com/all-platforms/news/rss/',
        'http://www.joystiq.com/rss.xml',
        'http://feeds.ign.com/ign/news?format=xml'
    ]

    fileManager = FileManager('the_news.txt', FeedManager(rss_list))
    fileManager.work()

