from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Scraper:
    def __init__(self, headless=False):
        self.authors = dict()  # (author id) -> (full data on author)
        self.author_to_paper = dict()  # (person id) -> [(paper id)]
        self.papers = dict()  # (paper id) -> (full data on paper)

        driver_folder = "path to google chrome driver"
        path = driver_folder + "chromedriver.exe"
        options = Options()
        options.headless = headless
        self.driver = webdriver.Chrome(path, options=options)
        print("Scraper " + str(id(self)) + " created")
        with open('scraping/data.html'):
            pass

    # Returns a list of scopus ids
    def _get_authors_list(self):
        print("Scraper " + str(id(self)) + " parses university workers")
        url = "https://www.scopus.com/results/authorNamesList.uri?affiliationId=60105869&" \
              "s=AF--ID%2860105869%29&resultsPerPage=500"
        self.driver.get(url)
        text = self.driver.page_source
        self.driver.quit()
        with open('scraping/data.html', 'w', encoding='utf-8') as file:
            file.write(text)

    def _get_author_data(self, author_id):
        print("Scraper " + str(id(self)) + " parses author " + str(author_id))
        self.driver.get("https://www.scopus.com/authid/detail.uri?authorId=" + str(author_id))
        data = self.driver.page_source
        self.driver.quit()
        with open('scraping/data.html', 'w', encoding='utf-8') as file:
            file.write(data)

    def _get_general_university_stats(self):
        print("Scraper " + str(id(self)) + " parses university general statistics")
        url = "https://www.scopus.com/affil/profile.uri?afid=60105869"
        self.driver.get(url)
        data = self.driver.page_source
        subject_list = self.driver.find_element(By.ID, "subjectList")
        affiliation_general = self.driver.find_element(By.ID, "affilAddlSec")
        print(subject_list.text)
        print("=========================================")
        print(affiliation_general.text)
        with open('scraping/data.html', 'w', encoding='utf-8') as file:
            file.write(data)
        self.driver.quit()

    def _get_papers(self, author_id):
        url = "https://www.scopus.com/results/results.uri?sort=plf-f&src=s&sid=c1140baa70c949831487b6121ec26b3d&sot=aff&sdt=a&sl=15&s=AF-ID%2860105869%29&origin=AffiliationProfile&editSaveSearch=&txGid=2b6475e16d6694003cc51e4df73b6ae1"
        citation_dynamics_url = "https://www.scopus.com/record/pubmetrics.uri?eid=2-s2.0-85054938535&origin=recordpage"
