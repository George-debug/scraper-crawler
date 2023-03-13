from scraper import ScraperWithPipeline
from pipeline import LINK_EXTRACTOR
from abc import ABC, abstractmethod


class Crawler(ABC):
    def __iter__(self):
        return self

    @abstractmethod
    def __next__(self) -> str:
        pass


class CrawlerSimple(Crawler):
    def __init__(self, start_url: str, link_selector: str | list[str]):
        self.__start_url = start_url
        scraper = ScraperWithPipeline(
            {"url": link_selector}).pipe_all([LINK_EXTRACTOR])
        self.__links = scraper.scrape(start_url)["url"]
        self.__index = 0

    def __next__(self):
        if self.__index >= len(self.__links):
            return StopIteration

        link = self.__links[self.__index]
        self.__index += 1

        return link
