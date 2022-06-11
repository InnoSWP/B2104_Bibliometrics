from scraping.parse import Scraper

if __name__ == '__main__':
    scraper = Scraper("Path to Chrome driver folder")
    scraper._get_paper_data(85087819719)

