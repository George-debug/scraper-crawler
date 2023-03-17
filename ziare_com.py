from misc import ROMANIAN_MONTHS
import datetime
from scraper import ScraperSimpleNews
from crawler import Crawler, CrawlerSimple


class _CrawlerZiareCom (Crawler):
    def __init__(self):
        # datetime.date(2006, 2, 1)
        self.incremented_day = datetime.date(2006, 3, 1)
        self.current_simple_crawler: CrawlerSimple = _CrawlerZiareCom._day_to_crawler(
            self.incremented_day)
        self.current_day_date = datetime.date.today()

    @staticmethod
    def _day_to_crawler(day: datetime.date) -> CrawlerSimple:
        link = f"https://ziare.com/arhiva/{day.strftime('%Y-%m-%d')}"

        return CrawlerSimple(link, "#content__container .title__article a")

    def __next__(self):
        while self.current_day_date >= self.incremented_day:
            rv = next(self.current_simple_crawler)
            if rv is not StopIteration:
                return rv

            self.incremented_day += datetime.timedelta(days=1)
            self.current_simple_crawler = _CrawlerZiareCom._day_to_crawler(
                self.incremented_day)

        raise StopIteration


CRAWLER_ZIARE_COM = _CrawlerZiareCom()


def _ziare_com_parse_date(date: str) -> datetime.date:
    date = date.split(",")[1].strip()
    day, month, year = date.split(" ")
    month = month.lower()

    if month not in ROMANIAN_MONTHS:
        raise Exception(f"Month \"{month}\" not found")
    month_id = ROMANIAN_MONTHS.index(month) + 1

    return datetime.date(int(year), month_id, int(day))


SCRAPER_ZIARE_COM = ScraperSimpleNews(
    "#article__container > h1",
    "#article__container > div.news__content.descriere_main.article__marker > p",
    "#article__container > div.news__info__content.d-flex > div.d-flex > div.news__publish",
    _ziare_com_parse_date
)
