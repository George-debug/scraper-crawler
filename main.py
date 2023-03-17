import psycopg2
from psycopg2 import errors
from psycopg2.errorcodes import UNIQUE_VIOLATION
from ziare_com import CRAWLER_ZIARE_COM, SCRAPER_ZIARE_COM
from database import CURSOR, CONN

import datetime

# table_name = "extracted"
# key "url" as varchar
# title as text
# content as text
# date as date

COMMIT_EVERY = 5


def link_exists(url: str) -> bool:
    CURSOR.execute(f"""SELECT * FROM extracted WHERE url = %s""", (url,))
    return CURSOR.fetchone() is not None


# TODO: find your starting date yourself

if __name__ == "__main__":
    time = datetime.datetime.now()
    time_int = time.hour * 3600 + time.minute * 60 + time.second

    log_file = open(f"log-{time_int}.txt", "a")

    commited = 0

    for link in CRAWLER_ZIARE_COM:
        try:
            scrapped = SCRAPER_ZIARE_COM.scrape(link)

            CURSOR.execute(
                f"""INSERT INTO extracted (url, title, content, date) VALUES (%s, %s, %s, %s)""",
                (
                    link,
                    scrapped.title,
                    scrapped.content,
                    scrapped.date
                )
            )

            commited += 1

            if commited == COMMIT_EVERY:
                CONN.commit()

                commited = 0

            print(link)

        except errors.lookup(UNIQUE_VIOLATION) as e:
            print(f"-- duplicate {link}")
            CONN.rollback()

        except Exception as e:
            log_file.write(f"{link}\n    {e}\n")
            log_file.flush()

    log_file.close()

    CONN.close()
