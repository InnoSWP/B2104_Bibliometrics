from scraping.parse import Scraper

if __name__ == '__main__':
    scraper = Scraper("Path to Chrome driver")
    scraper._get_authors_list()
    with open('scraping/data.html', 'w') as file:
        file.truncate(0)
