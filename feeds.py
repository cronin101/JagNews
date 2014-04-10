import heapq
import HTMLParser
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
        print('   --   '.join(self.__format(source, entry.title, False)
                for (source, entry) in self.get_latest(limit)))


if __name__ == "__main__":
    limit = int(sys.argv[1])

    rss_list = [
        'http://www.gamespot.com/feeds/news/',
        'http://www.escapistmagazine.com/rss/news/0.xml',
        'http://www.gamesradar.com/all-platforms/news/rss/',
        'http://www.joystiq.com/rss.xml'
    ]

    FeedManager(rss_list).display_latest(limit)


