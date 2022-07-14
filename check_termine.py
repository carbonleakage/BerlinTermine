from types import NoneType
import requests
from bs4 import BeautifulSoup

import logging

logging.basicConfig(
    filename="check_anmeldung_termine.log",
    level=logging.INFO,
    format="%(asctime)s --- %(message)s",
    encoding="latin",
)


class TerminePage():

    def __init__(self, url, termine) -> None:
        self.url = url
        self.response = requests.get(self.url)
        self.soup = BeautifulSoup(self.response.text, "html.parser")
        self.next_page = "https://service.berlin.de" 
        if next_page_link := self.soup.find("th", class_="next"): 
            self.next_page += next_page_link.find("a", href=True)["href"]
        self.termine = termine
    
    def count_frei_termine(self):
        self._tables = self.soup.find_all("table")
        for table in self._tables:
            month = table.find("th", class_="month")
            if month not in self.termine:
                dates_notbookable = table.find_all("td", class_="nichtbuchbar")
                dates_bookable = table.find_all("td", class_="buchbar")
                self.termine[month.text, "bookable"] = len(dates_bookable)
                self.termine[month.text, "not-available"] = len(dates_notbookable)

if __name__ == "__main__":
    # Verpflictungserklärung
    # url = "https://service.berlin.de/terminvereinbarung/termin/tag.php?id=3061&anliegen[]=120691#&termin=1&dienstleister=327437&anliegen[]=120691&herkunft=1"

    logging.info("Started running script!") 
    url = "https://service.berlin.de/terminvereinbarung/termin/tag.php?termin=1&dienstleister=122276&anliegen[]=120686&herkunft=1"
    termine = dict()

    while url != "https://service.berlin.de":
        logging.info(f"Checking appointments in {url}") 
        page = TerminePage(url, termine)
        page.count_frei_termine()
        url = page.next_page
        termine = page.termine
    
    for month, termine_type in termine:
        logging.info(
            f"Numer of {termine_type} dates in {month}: {termine[month, termine_type]}"
        )
    logging.info("Finished running script!") 