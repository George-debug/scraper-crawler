from datetime import date
from typing import Any, Callable
import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from pipeline import ScrapperPipelineCell, PIPELINE_TEXT_EXTRACTOR, ScrapperPipelineCellMap


class Scraper(ABC):
    @abstractmethod
    def scrape(self, url: str) -> dict[str, list[Any]]:
        pass


class _PipelineHandler:
    def __init__(self, pipeline: list[ScrapperPipelineCell]):
        self._pipeline = pipeline

    @abstractmethod
    def __call__(self, d: dict[str, list[Any]]):
        pass


class _PipelineHandlerAll(_PipelineHandler):
    def __init__(self, pipeline: list[ScrapperPipelineCell]):
        super().__init__(pipeline)

    def __call__(self, d: dict[str, list[Any]]):
        for p in self._pipeline:
            for key, value in d.items():
                d[key] = p(value)


class _PipelineHandlerSpecific(_PipelineHandler):
    def __init__(self, pipeline: list[ScrapperPipelineCell], keys: list[str]):
        super().__init__(pipeline)
        self._keys = keys

    def __call__(self, d: dict[str, list[Any]]):
        for p in self._pipeline:
            for key, value in d.items():
                if key in self._keys:
                    d[key] = p(value)


class _PipelineHandlerExcept(_PipelineHandler):
    def __init__(self, pipeline: list[ScrapperPipelineCell], keys: list[str]):
        super().__init__(pipeline)
        self._keys = keys

    def __call__(self, d: dict[str, list[Any]]):
        for p in self._pipeline:
            for key, value in d.items():
                if key not in self._keys:
                    d[key] = p(value)


class ScraperWithPipeline(Scraper):
    def __init__(self, selectors: dict[str, str | list[str]]):
        self.__selectors: dict[str, list[str]] = {}
        self.__pipeline_handlers: list[_PipelineHandler] = []

        for key, value in selectors.items():
            if isinstance(value, list):
                self.__selectors[key] = value
            else:
                self.__selectors[key] = [value]

    def pipe_all(self, pipeline: list[ScrapperPipelineCell]) -> 'ScraperWithPipeline':
        self.__pipeline_handlers.append(_PipelineHandlerAll(pipeline))
        return self

    def pipe_specific(self, pipeline: list[ScrapperPipelineCell], keys: list[str]) -> 'ScraperWithPipeline':
        self.__pipeline_handlers.append(
            _PipelineHandlerSpecific(pipeline, keys))
        return self

    def pipe_except(self, pipeline: list[ScrapperPipelineCell], keys: list[str]) -> 'ScraperWithPipeline':
        self.__pipeline_handlers.append(_PipelineHandlerExcept(pipeline, keys))
        return self

    def scrape(self, url: str) -> dict[str, list[Any]]:
        html = requests.get(url)
        soup = BeautifulSoup(html.text, "lxml")

        data_extracted: dict[str, list[Any]] = {}

        for key, selectors in self.__selectors.items():
            data_extracted[key] = []
            for selector in selectors:
                tag_list = list(soup.select(selector))
                data_extracted[key].extend(tag_list)

        for handler in self.__pipeline_handlers:
            handler(data_extracted)

        return data_extracted


class NewsData:
    def __init__(self, title: str, content: str, date: date):
        self.title = title
        self.content = content
        self.date = date


class ScraperSimpleNews:
    def __init__(self, title_selector: str | list[str], content_selector: str | list[str], date_selector: str | list[str], date_parser: Callable[[str], date]):
        date_parser_cell = ScrapperPipelineCellMap(date_parser)

        self.scraper = ScraperWithPipeline({
            "title": title_selector,
            "content": content_selector,
            "date": date_selector
        }) \
            .pipe_all(PIPELINE_TEXT_EXTRACTOR) \
            .pipe_specific([date_parser_cell], ["date"])

    def scrape(self, url: str) -> NewsData:
        data = self.scraper.scrape(url)

        for key in data.keys():
            if len(data[key]) == 0:
                raise ValueError(
                    f"Could not find data for key \"{key}\" in url {url}")

            if len(data[key]) > 1:
                raise ValueError(
                    f"Found multiple data for key \"{key}\" in url {url}")

        return NewsData(data["title"][0], data["content"][0], data["date"][0])
