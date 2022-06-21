from scraping.parse import Scraper
from scraping.quartile import quartile_of
from scraping.research_gate import members_of_Inno

if __name__ == '__main__':
    scraper = Scraper()
    scraper.parse()

