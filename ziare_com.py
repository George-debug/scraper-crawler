import datetime
from scraper import ScraperSimpleNews
from crawler import Crawler, CrawlerSimple


class _CrawlerZiareCom (Crawler):
    def __init__(self):
        self.incremented_day = datetime.date(2006, 2, 1)
        self.current_simple_crawler: CrawlerSimple = _CrawlerZiareCom._day_to_crawler(
            self.incremented_day)
        self.current_day_date = datetime.date.today()

    @staticmethod
    def _day_to_crawler(day: datetime.date) -> CrawlerSimple:
        link = f"https://ziare.com/arhiva/{day.strftime('%Y-%m-%d')}"

        return CrawlerSimple(link, "#content__container .title__article a")

    def __next__(self):
        while self.current_day_date >= self.incremented_day:
            try:
                return next(self.current_simple_crawler)
            except StopIteration:
                self.incremented_day += datetime.timedelta(days=1)
                self.current_simple_crawler = _CrawlerZiareCom._day_to_crawler(
                    self.incremented_day)

        raise StopIteration


CRAWLER_ZIARE_COM = _CrawlerZiareCom()

SCRAPER_ZIARE_COM = ScraperSimpleNews(
    "#article__container > h1",
    "#article__container > div.news__content.descriere_main.article__marker > p"
)
