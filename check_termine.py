from urllib import response
import requests
from bs4 import BeautifulSoup

import logging

logging.basicConfig(
    filename="check_termine.log",
    level=logging.DEBUG,
    format="%(asctime)s --- %(message)s",
    encoding="latin",
)


def get_page(url: str) -> requests.Response:
    """
    Gets and returns the page content of url.
    """
    response = requests.get(url)
    logging.info(f"Connect to url: {url}")
    if response.status_code != 200:
        logging.error(f"Received error code {response.status_code}!")
    else:
        logging.info("Successfully retrieved page!")

    return response


def page_soup(response: requests.Response):

    if response.status_code != 200:
        soup = ""
    else:
        soup = BeautifulSoup(response.text, "html.parser")

    return soup


def check_buchbare_termine(url, months=[]):
    """
    Check the free appointments in the given berlin.de url
    """
    response = get_page(url)
    soup = page_soup(response)

    tables = soup.find_all("table")
    try:
        next = soup.find("th", class_="next").find("a", href=True)["href"]
    except:
        next = ""

    for table in tables:
        month = table.find("th", class_="month")
        logging.debug(f"Found calendar month {month.text} in Termin webpage")
        if month not in months:
            months.append(month.text)
            dates = table.find_all("td")
            dates_notbookable = table.find_all("td", class_="nichtbuchbar")
            dates_bookable = table.find_all("td", class_="buchbar")
            logging.debug(f"Total number of dates in {month.text}: {len(dates)}")
            if len(dates_bookable) > 0:
                logging.debug(
                    f"Number of bookable dates in {month.text}: __{len(dates_bookable)__}"
                )
            else:
                logging.debug(
                    f"Number of bookable dates in {month.text}: {len(dates_bookable)}"
                )
            logging.debug(
                f"Number of not bookable dates in {month.text}: {len(dates_notbookable)}"
            )
    return months, next


if __name__ == "__main__":
    logging.debug("-" * 20 + "Started running script!")
    url = "https://service.berlin.de/terminvereinbarung/termin/tag.php?id=3061&anliegen[]=120691#&termin=1&dienstleister=327437&anliegen[]=120691&herkunft=1"
    months = []

    while url != "https://service.berlin.de":
        months, url = check_buchbare_termine(url, months)
        url = "https://service.berlin.de" + url
    logging.debug("-" * 20 + "Finished running script!")
