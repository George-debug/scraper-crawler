from ziare_com import CRAWLER_ZIARE_COM, SCRAPER_ZIARE_COM


if __name__ == "__main__":
    for link in CRAWLER_ZIARE_COM:
        print(link)
        scrapped = SCRAPER_ZIARE_COM.scrape(link)
        print(scrapped["title"])
        print(scrapped["content"])
        print("================================")
