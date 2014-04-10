import heapq
import itertools
import sys


import feedparser


class Feed(object):
    def __init__(self, url):
        self.__url = url
        self.title = feedparser.parse(self.__url).feed.title

    def get_latest(self, limit):
        entries = feedparser.parse(self.__url).entries
        return heapq.nlargest(limit, entries,
                key=lambda entry: entry.published_parsed)


class FeedManager(object):
    def __init__(self, url_list):
        feeds = (Feed(url) for url in url_list)
        self.named_feeds = {feed.title : feed for feed in feeds}

    def get_latest(self, limit):
        entries_by_source = ((source, feed.get_latest(limit))
                for source, feed in self.named_feeds.iteritems())

        all_sourced_entries = itertools.chain.from_iterable(
                ((source, entry) for entry in entries)
                        for source, entries in entries_by_source)

        return (': '.join([''.join(['[', source, ']']), ''.join(['"', entry.title, '"'])])
                for source, entry in heapq.nlargest(limit, all_sourced_entries,
                        key=lambda t: t[1].published_parsed))


if __name__ == "__main__":
    limit = int(sys.argv[1])

    rss_list = [
        'http://www.gamespot.com/feeds/news/',
        'http://www.nintendolife.com/feeds/news',
        'http://www.escapistmagazine.com/rss/news/0.xml'
    ]

    manager = FeedManager(rss_list)

    print('   --   '.join(manager.get_latest(limit)))
